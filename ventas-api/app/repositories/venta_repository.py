"""Consultas SQLAlchemy para el seguimiento e idempotencia de ventas."""
from decimal import Decimal
from sqlalchemy import select, or_, func, and_
from app.models import Venta


class VentaRepository:

    def __init__(self, db):
        self.db = db

    def por_clave(self, usuario, clave):
        return self.db.scalar(select(Venta).where(
            Venta.usuario == usuario, Venta.idempotency_key == clave))

    def por_id(self, id: int):
        return self.db.get(Venta, id)

    def bloquear(self, id):
        return self.db.scalar(select(Venta).where(Venta.id == id).with_for_update())

    def pendientes(self):
        return self.db.scalars(select(Venta.id).where(or_(
            Venta.estado.in_(["PENDIENTE", "EN_REVISION"]),
            (Venta.estado == "COMPLETADA") & (Venta.notificacion != "ENVIADA")
        )).order_by(Venta.id).limit(100)).all()

    def listar_propias(self, usuario: str, estado: str | None = None, limit: int | None = None, offset: int = 0) -> list[Venta]:
        """F03 / F04 / D06: Lista ventas del usuario autenticado ordenadas por fecha DESC e id DESC."""
        condiciones = [Venta.usuario == usuario]
        if estado:
            condiciones.append(Venta.estado == estado)

        stmt = select(Venta).where(and_(*condiciones)).order_by(Venta.fecha.desc(), Venta.id.desc())
        if limit is not None:
            stmt = stmt.offset(offset).limit(limit)
        return list(self.db.scalars(stmt).all())

    def contar_propias(self, usuario: str, estado: str | None = None) -> int:
        """D06: Conteo total de ventas propias (con filtro de estado opcional)."""
        condiciones = [Venta.usuario == usuario]
        if estado:
            condiciones.append(Venta.estado == estado)
        stmt = select(func.count(Venta.id)).where(and_(*condiciones))
        return self.db.scalar(stmt) or 0

    def resumen_usuario(self, usuario: str) -> dict:
        """D09: Resumen numérico de ventas para el usuario propietario."""
        # Cantidad de ventas por estado
        conteo_estados = {}
        for est in ["COMPLETADA", "PENDIENTE", "EN_REVISION", "FALLIDA"]:
            stmt = select(func.count(Venta.id)).where(Venta.usuario == usuario, Venta.estado == est)
            conteo_estados[est] = self.db.scalar(stmt) or 0

        # Suma de precio_acordado solo para COMPLETADAS (excluye FALLIDA y PENDIENTE/EN_REVISION)
        stmt_sum = select(func.coalesce(func.sum(Venta.precio_acordado), 0)).where(
            Venta.usuario == usuario,
            Venta.estado == "COMPLETADA"
        )
        total_ingresos = Decimal(str(self.db.scalar(stmt_sum) or 0))

        return {
            "usuario": usuario,
            "ventas_completadas": conteo_estados["COMPLETADA"],
            "total_ingresos": float(total_ingresos),
            "ventas_pendientes": conteo_estados["PENDIENTE"],
            "ventas_en_revision": conteo_estados["EN_REVISION"],
            "ventas_fallidas": conteo_estados["FALLIDA"],
            "total_ventas": sum(conteo_estados.values())
        }

    def listar_incidencias(self, usuario: str, es_admin: bool = False) -> dict:
        """S12: Panel de incidencias: EN_REVISION y COMPLETADAS con notificación PENDIENTE."""
        cond_revision = [Venta.estado == "EN_REVISION"]
        cond_aviso = [(Venta.estado == "COMPLETADA") & (Venta.notificacion == "PENDIENTE")]

        if not es_admin:
            cond_revision.append(Venta.usuario == usuario)
            cond_aviso.append(Venta.usuario == usuario)

        stmt_revision = select(Venta).where(and_(*cond_revision)).order_by(Venta.fecha.desc(), Venta.id.desc())
        stmt_aviso = select(Venta).where(and_(*cond_aviso)).order_by(Venta.fecha.desc(), Venta.id.desc())

        en_revision = list(self.db.scalars(stmt_revision).all())
        aviso_pendiente = list(self.db.scalars(stmt_aviso).all())

        return {
            "en_revision": en_revision,
            "aviso_pendiente": aviso_pendiente,
            "total_en_revision": len(en_revision),
            "total_aviso_pendiente": len(aviso_pendiente)
        }
