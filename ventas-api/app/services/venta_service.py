"""Caso de uso de creación, conciliación, notificación y outbox de ventas."""
import hashlib
import json
from uuid import uuid4
from decimal import Decimal
from datetime import datetime, timezone, timedelta
import httpx
from sqlalchemy.exc import IntegrityError
from app.db import SessionLocal
from app.models import Venta, Comprador
from app.repositories.venta_repository import VentaRepository
from app.repositories.outbox_repository import OutboxRepository
from app.clients.vehiculos_client import VehiculosClient, FalloRemoto
from app.config import NOTIF_URL, NOTIF_KEY
from app.errors import ApiError
from app.security import propietario
from app.correlation import get_correlation_id

remote = VehiculosClient()

ESPERAS_SEGUNDOS = [10, 30, 60]


def _aplicar_espera_progresiva(v: Venta):
    """S13: Aplica cálculo de reintento con espera progresiva (10s, 30s, 60s)."""
    espera = ESPERAS_SEGUNDOS[min(v.intentos, len(ESPERAS_SEGUNDOS) - 1)]
    v.intentos += 1
    v.proximo_intento_utc = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(seconds=espera)


def salida(v):
    return {
        "id": v.id,
        "operacionId": v.operacion_id,
        "vehiculoId": v.vehiculo_id,
        "compradorId": v.comprador_id,
        "precioAcordado": str(v.precio_acordado) if v.precio_acordado is not None else None,
        "moneda": v.moneda,
        "estado": v.estado,
        "notificacion": v.notificacion,
        "intentos": v.intentos,
        "proximoIntentoUTC": v.proximo_intento_utc.isoformat() + "Z" if v.proximo_intento_utc else None,
        "fechaUTC": v.fecha.isoformat() + "Z"
    }


def crear(datos, clave, usuario):
    cuerpo = json.dumps(datos.model_dump(), sort_keys=True, separators=(",", ":"))
    huella = hashlib.sha256(cuerpo.encode()).hexdigest()
    nueva = False

    with SessionLocal() as db:
        repo = VentaRepository(db)
        v = repo.por_clave(usuario["usuario"], clave)
        if v is None:
            comprador = db.get(Comprador, datos.compradorId)
            if comprador is None:
                raise ApiError(404, "COMPRADOR_NO_EXISTE", "Comprador inexistente")
            propietario(usuario, comprador.usuario)
            v = Venta(
                operacion_id=str(uuid4()),
                usuario=usuario["usuario"],
                vehiculo_id=datos.vehiculoId,
                comprador_id=datos.compradorId,
                idempotency_key=clave,
                request_hash=huella,
                intentos=0,
                proximo_intento_utc=None
            )
            db.add(v)
            try:
                db.commit()
                nueva = True
            except IntegrityError:
                db.rollback()
                v = repo.por_clave(usuario["usuario"], clave)
                if v is None:
                    raise

        if v.request_hash != huella:
            raise ApiError(409, "CLAVE_REUTILIZADA", "La misma clave requiere el mismo cuerpo")

        id = v.id

    procesar(id)
    notificar(id)

    with SessionLocal() as db:
        v = db.get(Venta, id)
        if v.estado == "FALLIDA":
            raise ApiError(v.error_status or 409, "VENTA_RECHAZADA", v.error_detalle or "La venta fue rechazada")
        status = (201 if nueva else 200) if v.estado == "COMPLETADA" else 202
        return salida(v), status


def procesar(id):
    with SessionLocal.begin() as db:
        v = VentaRepository(db).bloquear(id)
        if v is None or v.estado in ("COMPLETADA", "FALLIDA"):
            return

        try:
            try:
                r = remote.por_operacion(v.operacion_id)
            except FalloRemoto as ex:
                if ex.status != 404:
                    raise
                try:
                    r = remote.reservar(v.vehiculo_id, v.operacion_id)
                except FalloRemoto as rechazo:
                    if rechazo.status in (404, 409, 422):
                        v.estado = "FALLIDA"
                        v.error_status = rechazo.status
                        v.error_detalle = "Vehículo inexistente o no disponible"
                        v.proximo_intento_utc = None
                        return
                    raise

            v.reserva_id = r["id"]
            v.precio_acordado = Decimal(str(r["precio"]))
            v.moneda = r["moneda"]

            if r["estado"] == "LIBERADA":
                v.estado = "FALLIDA"
                v.error_status = 409
                v.error_detalle = "Reserva liberada"
                v.proximo_intento_utc = None
                return

            if r["estado"] == "RESERVADA":
                r = remote.confirmar(r["id"])

            if r["estado"] != "CONFIRMADA":
                raise FalloRemoto(502, "Estado de reserva inesperado")

            v.estado = "COMPLETADA"
            v.error_status = None
            v.error_detalle = None
            v.intentos = 0
            v.proximo_intento_utc = None

            # E18: Registro de evento Outbox en la misma transacción de la venta
            OutboxRepository(db).registrar_evento_venta(v, v.comprador.correo)

        except (FalloRemoto, ValueError, KeyError):
            v.estado = "EN_REVISION"
            v.error_detalle = "Pendiente de consultar y conciliar con Java"
            # S13: Espera progresiva para reintentos
            _aplicar_espera_progresiva(v)


def notificar(id):
    with SessionLocal.begin() as db:
        v = VentaRepository(db).bloquear(id)
        if v is None or v.estado != "COMPLETADA" or v.notificacion == "ENVIADA":
            return

        cid = get_correlation_id()
        try:
            r = httpx.post(
                NOTIF_URL + "/api/notificaciones",
                timeout=3,
                headers={
                    "X-Notification-Key": NOTIF_KEY,
                    "X-Correlation-Id": cid
                },
                json={
                    "vehiculoId": v.vehiculo_id,
                    "tipo": "VENTA",
                    "destinatario": v.comprador.correo,
                    "mensaje": f"Venta {v.id} operación {v.operacion_id} completada",
                }
            )
            if 200 <= r.status_code < 300:
                v.notificacion = "ENVIADA"
                v.intentos = 0
                v.proximo_intento_utc = None
            else:
                v.notificacion = "PENDIENTE"
                _aplicar_espera_progresiva(v)
        except httpx.RequestError:
            v.notificacion = "PENDIENTE"
            _aplicar_espera_progresiva(v)
