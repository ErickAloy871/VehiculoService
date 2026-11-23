"""Consultas y persistencia para el patrón Outbox Transaccional (E18)."""
import json
from datetime import datetime, timezone
from uuid import uuid4
from sqlalchemy import select
from app.models import OutboxEvento, Venta


class OutboxRepository:

    def __init__(self, db):
        self.db = db

    def registrar_evento_venta(self, venta: Venta, destinatario: str) -> OutboxEvento:
        """Registra un evento outbox dentro de la misma transacción local de la venta."""
        payload = json.dumps({
            "vehiculoId": venta.vehiculo_id,
            "tipo": "VENTA",
            "destinatario": destinatario,
            "mensaje": f"Venta {venta.id} operacion {venta.operacion_id} completada",
            "ventaId": venta.id,
            "operacionId": venta.operacion_id
        })
        evento = OutboxEvento(
            evento_id=str(uuid4()),
            tipo="VENTA",
            payload=payload,
            estado="PENDIENTE",
            intentos=0,
            creado_en=datetime.now(timezone.utc).replace(tzinfo=None)
        )
        self.db.add(evento)
        return evento

    def pendientes(self, limite: int = 50) -> list[OutboxEvento]:
        """Obtiene eventos outbox pendientes de despacho."""
        stmt = (
            select(OutboxEvento)
            .where(OutboxEvento.estado == "PENDIENTE")
            .order_by(OutboxEvento.id.asc())
            .limit(limite)
        )
        return list(self.db.scalars(stmt).all())

