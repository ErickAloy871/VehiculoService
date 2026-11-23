"""Endpoints REST de compradores y ventas."""
from typing import Annotated
from fastapi import APIRouter, Depends, Header, Response, Query
from app.db import SessionLocal
from app.models import Venta, Comprador
from app.schemas import CrearVenta, CrearComprador, ActualizarComprador
from app.repositories.comprador_repository import CompradorRepository
from app.repositories.venta_repository import VentaRepository
from app.security import identidad, vendedor, propietario
from app.errors import ApiError
from app.services import venta_service as service

router = APIRouter(prefix="/api")

ESTADOS_VENTA_VALIDOS = {"PENDIENTE", "EN_REVISION", "COMPLETADA", "FALLIDA"}


# -------------------------------------------------------------
# COMPRADORES (F01, F02, D07, D08)
# -------------------------------------------------------------

@router.get("/compradores")
def listar_compradores(
    buscar: str | None = Query(default=None, description="Búsqueda parcial por nombre o documento (D07)"),
    u=Depends(identidad)
):
    """F01 / D07: Lista compradores del usuario autenticado con búsqueda opcional."""
    vendedor(u)
    with SessionLocal() as db:
        repo = CompradorRepository(db)
        if buscar is not None and buscar.strip():
            compradores = repo.buscar(u["usuario"], buscar)
        else:
            compradores = repo.listar_por_usuario(u["usuario"])

        return [
            {
                "id": c.id,
                "documento": c.documento,
                "nombre": c.nombre,
                "correo": c.correo
            }
            for c in compradores
        ]


@router.post("/compradores", status_code=201)
def crear_comprador(d: CrearComprador, u=Depends(identidad)):
    """Crea un nuevo comprador asociado al usuario autenticado."""
    vendedor(u)
    with SessionLocal.begin() as db:
        c = Comprador(usuario=u["usuario"], **d.model_dump())
        db.add(c)
        db.flush()
        return {"id": c.id, "documento": c.documento, "nombre": c.nombre, "correo": c.correo}


@router.get("/compradores/{id}")
def obtener_comprador(id: int, u=Depends(identidad)):
    """F02: Consulta un comprador por ID protegido frente a usuarios ajenos."""
    vendedor(u)
    with SessionLocal() as db:
        repo = CompradorRepository(db)
        c = repo.por_id(id)
        if c is None:
            raise ApiError(404, "COMPRADOR_NO_EXISTE", "Comprador inexistente")
        propietario(u, c.usuario)
        return {
            "id": c.id,
            "documento": c.documento,
            "nombre": c.nombre,
            "correo": c.correo
        }


@router.put("/compradores/{id}")
def actualizar_comprador(id: int, d: ActualizarComprador, u=Depends(identidad)):
    """D08: Actualiza únicamente nombre y correo; el documento permanece inmutable."""
    vendedor(u)
    with SessionLocal.begin() as db:
        repo = CompradorRepository(db)
        c = repo.por_id(id)
        if c is None:
            raise ApiError(404, "COMPRADOR_NO_EXISTE", "Comprador inexistente")
        propietario(u, c.usuario)
        c.nombre = d.nombre
        c.correo = d.correo
        db.flush()
        return {
            "id": c.id,
            "documento": c.documento,
            "nombre": c.nombre,
            "correo": c.correo
        }


# -------------------------------------------------------------
# RUTAS ESTÁTICAS DE VENTAS (D09, S12)
# Registradas antes de /ventas/{id} para evitar colisión de rutas.
# -------------------------------------------------------------

@router.get("/ventas/resumen")
def resumen_ventas(u=Depends(identidad)):
    """D09: Resumen numérico de ventas del usuario autenticado."""
    vendedor(u)
    with SessionLocal() as db:
        return VentaRepository(db).resumen_usuario(u["usuario"])


@router.get("/ventas/incidencias")
def incidencias_ventas(u=Depends(identidad)):
    """S12: Panel de incidencias: ventas EN_REVISION y avisos PENDIENTE."""
    vendedor(u)
    es_admin = "ROLE_ADMIN" in u["roles"]
    with SessionLocal() as db:
        data = VentaRepository(db).listar_incidencias(u["usuario"], es_admin=es_admin)
        return {
            "usuario": u["usuario"],
            "esAdmin": es_admin,
            "totalEnRevision": data["total_en_revision"],
            "totalAvisoPendiente": data["total_aviso_pendiente"],
            "enRevision": [service.salida(v) for v in data["en_revision"]],
            "avisoPendiente": [service.salida(v) for v in data["aviso_pendiente"]]
        }


# -------------------------------------------------------------
# VENTAS (F03, F04, D06, POST base)
# -------------------------------------------------------------

@router.get("/ventas")
def listar_ventas(
    estado: str | None = Query(default=None, description="Filtro opcional por estado (F04)"),
    limit: int | None = Query(default=None, description="Límite para paginación 1..50 (D06)"),
    offset: int = Query(default=0, description="Offset para paginación >= 0 (D06)"),
    u=Depends(identidad)
):
    """F03 / F04 / D06: Listado de ventas propias, con filtro de estado y paginación opcional."""
    vendedor(u)

    if estado is not None and estado not in ESTADOS_VENTA_VALIDOS:
        raise ApiError(422, "ESTADO_INVALIDO", f"Estado desconocido: {estado}")

    with SessionLocal() as db:
        repo = VentaRepository(db)

        # Si se especifica limit o offset > 0, activamos formato paginado (D06)
        if limit is not None or offset > 0:
            if limit is not None and not (1 <= limit <= 50):
                raise ApiError(422, "LIMITE_INVALIDO", "limit debe estar entre 1 y 50")
            if offset < 0:
                raise ApiError(422, "OFFSET_INVALIDO", "offset no puede ser negativo")

            limite_efectivo = limit if limit is not None else 50
            total = repo.contar_propias(u["usuario"], estado=estado)
            ventas = repo.listar_propias(u["usuario"], estado=estado, limit=limite_efectivo, offset=offset)
            return {
                "items": [service.salida(v) for v in ventas],
                "total": total,
                "limit": limite_efectivo,
                "offset": offset
            }

        # Listado plano sin paginar (F03 / F04)
        ventas = repo.listar_propias(u["usuario"], estado=estado)
        return [service.salida(v) for v in ventas]


@router.post("/ventas")
def crear_venta(
    d: CrearVenta,
    response: Response,
    idempotency_key: Annotated[str, Header(min_length=8, max_length=100, pattern=r"^[A-Za-z0-9_-]+$")],
    u=Depends(identidad)
):
    """Crea una nueva venta coordinada con Java y notificaciones."""
    vendedor(u)
    resultado, codigo = service.crear(d, idempotency_key, u)
    response.status_code = codigo
    response.headers["Location"] = f"/api/ventas/{resultado['id']}"
    return resultado


# -------------------------------------------------------------
# RUTAS DE VENTA POR ID (F03 base, D10 comprobante, S15 conciliar)
# -------------------------------------------------------------

@router.get("/ventas/{id}/comprobante")
def emitir_comprobante(id: int, u=Depends(identidad)):
    """D10: Emite comprobante JSON solo para venta propia COMPLETADA."""
    vendedor(u)
    with SessionLocal() as db:
        v = db.get(Venta, id)
        if v is None:
            raise ApiError(404, "VENTA_NO_EXISTE", "Venta inexistente")
        propietario(u, v.usuario)

        if v.estado != "COMPLETADA":
            raise ApiError(409, "VENTA_NO_COMPLETADA", f"Solo se emite comprobante para ventas COMPLETADAS (estado: {v.estado})")

        return {
            "comprobante": f"CMP-{v.id:06d}",
            "ventaId": v.id,
            "operacionId": v.operacion_id,
            "fecha": v.fecha.isoformat() + "Z",
            "precioConfirmado": str(v.precio_acordado),
            "moneda": v.moneda or "USD",
            "comprador": {
                "id": v.comprador.id,
                "documento": v.comprador.documento,
                "nombre": v.comprador.nombre,
                "correo": v.comprador.correo
            },
            "vehiculoId": v.vehiculo_id
        }


@router.post("/ventas/{id}/conciliar")
def conciliar_venta(id: int, response: Response, u=Depends(identidad)):
    """S15: Conciliación administrativa manual (exclusivo para ADMIN)."""
    if "ROLE_ADMIN" not in u["roles"]:
        raise ApiError(403, "SIN_PERMISO", "Solo administradores pueden conciliar manualmente")

    with SessionLocal() as db:
        v = db.get(Venta, id)
        if v is None:
            raise ApiError(404, "VENTA_NO_EXISTE", "Venta inexistente")

        if v.estado in ("COMPLETADA", "FALLIDA"):
            raise ApiError(409, "ESTADO_NO_CONCILIABLE", f"No se puede conciliar una venta en estado terminal: {v.estado}")

    # Ejecuta el procesamiento de conciliación con Java
    service.procesar(id)
    service.notificar(id)

    with SessionLocal() as db:
        v_actualizada = db.get(Venta, id)
        codigo = 200 if v_actualizada.estado in ("COMPLETADA", "FALLIDA") else 202
        response.status_code = codigo
        return service.salida(v_actualizada)


@router.get("/ventas/{id}")
def obtener_venta(id: int, u=Depends(identidad)):
    """Consulta la venta por ID y restringe al propietario o ADMIN."""
    vendedor(u)
    with SessionLocal() as db:
        v = db.get(Venta, id)
        if v is None:
            raise ApiError(404, "VENTA_NO_EXISTE", "Venta inexistente")
        propietario(u, v.usuario)
        return service.salida(v)
