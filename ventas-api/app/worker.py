"""Procesador de operaciones pendientes, reintentos progresivos (S13) y outbox (E18)."""
import sys
import time
import json
import logging
from datetime import datetime, timezone
import httpx
from app.db import SessionLocal
from app.models import Venta
from app.repositories.venta_repository import VentaRepository
from app.repositories.outbox_repository import OutboxRepository
from app.services.venta_service import procesar, notificar
from app.config import NOTIF_URL, NOTIF_KEY
from app.correlation import get_correlation_id

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("worker")


def ciclo_ventas():
    """S13: Procesa ventas pendientes respetando ventanas de tiempo de reintentos."""
    with SessionLocal() as db:
        ids = VentaRepository(db).pendientes()

    for id in ids:
        try:
            logger.info("Reintentando conciliación de venta %s", id)
            procesar(id)
            notificar(id)
        except Exception:
            logger.exception("No se pudo conciliar venta %s", id)


def ciclo_outbox():
    """E18: Despacha eventos outbox transaccionales hacia notificaciones-service."""
    with SessionLocal.begin() as db:
        repo = OutboxRepository(db)
        eventos = repo.pendientes(limite=50)

        for ev in eventos:
            try:
                data = json.loads(ev.payload)
                venta_id = data.get("ventaId")
                if venta_id:
                    venta = db.get(Venta, venta_id)
                    if venta and venta.notificacion == "ENVIADA":
                        # Ya fue notificado exitosamente por venta_service; sincronizamos outbox sin duplicar aviso
                        ev.estado = "ENVIADA"
                        ev.enviado_en = datetime.now(timezone.utc).replace(tzinfo=None)
                        continue

                cid = get_correlation_id()
                headers = {
                    "X-Notification-Key": NOTIF_KEY,
                    "X-Correlation-Id": cid
                }
                logger.info("Despachando evento outbox %s (tipo: %s)", ev.evento_id, ev.tipo)
                r = httpx.post(
                    NOTIF_URL + "/api/notificaciones",
                    timeout=3,
                    headers=headers,
                    json={
                        "vehiculoId": data.get("vehiculoId"),
                        "tipo": data.get("tipo", "VENTA"),
                        "destinatario": data.get("destinatario"),
                        "mensaje": data.get("mensaje")
                    }
                )
                if 200 <= r.status_code < 300:
                    ev.estado = "ENVIADA"
                    ev.enviado_en = datetime.now(timezone.utc).replace(tzinfo=None)
                    ev.ultimo_error = None
                    # Si el evento pertenece a una venta, actualizamos su campo notificacion
                    venta_id = data.get("ventaId")
                    if venta_id:
                        venta = db.get(Venta, venta_id)
                        if venta:
                            venta.notificacion = "ENVIADA"
                    logger.info("Evento outbox %s despachado con éxito.", ev.evento_id)
                else:
                    ev.intentos += 1
                    ev.ultimo_error = f"HTTP {r.status_code}: {r.text[:200]}"
                    logger.warning("Fallo en outbox %s: %s", ev.evento_id, ev.ultimo_error)
            except Exception as ex:
                ev.intentos += 1
                ev.ultimo_error = f"Error conexión: {str(ex)[:200]}"
                logger.warning("Error de red en outbox %s: %s", ev.evento_id, ex)


def ciclo():
    ciclo_ventas()
    ciclo_outbox()


if __name__ == "__main__":
    while True:
        try:
            ciclo()
        except Exception:
            logger.exception("Fallo de ciclo de recuperación")

        if "--once" in sys.argv:
            break

        time.sleep(10)
