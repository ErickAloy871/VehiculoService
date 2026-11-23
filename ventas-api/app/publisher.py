"""Publicador de eventos de venta hacia RabbitMQ para la cola notificaciones.ventas."""
import json
import logging
import uuid
from datetime import datetime, timezone
import pika

logger = logging.getLogger(__name__)

RABBITMQ_HOST = "localhost"
RABBITMQ_PORT = 5672
QUEUE_NAME = "notificaciones.ventas"


def publicar_evento_venta(venta_id: int, vehiculo_id: int, mensaje: str | None = None) -> bool:
    """Publica un mensaje persistente en la cola durable de RabbitMQ."""
    connection = None
    try:
        credentials = pika.PlainCredentials("guest", "guest")
        parameters = pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            credentials=credentials,
            connection_attempts=3,
            retry_delay=1
        )
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()

        # Cola durable para no perder eventos ante caídas
        channel.queue_declare(queue=QUEUE_NAME, durable=True)

        evento = {
            "eventoId": str(uuid.uuid4()),
            "tipo": "VENTA",
            "ventaId": venta_id,
            "vehiculoId": vehiculo_id,
            "fechaHora": datetime.now(timezone.utc).isoformat(),
            "mensaje": mensaje or f"Venta #{venta_id} confirmada para el vehículo {vehiculo_id}"
        }

        channel.basic_publish(
            exchange="",
            routing_key=QUEUE_NAME,
            body=json.dumps(evento),
            properties=pika.BasicProperties(
                delivery_mode=pika.DeliveryMode.Persistent,
                content_type="application/json"
            )
        )
        logger.info("Evento VENTA publicado en RabbitMQ [Cola: %s, EventoId: %s, VentaId: %s]",
                    QUEUE_NAME, evento["eventoId"], venta_id)
        return True
    except Exception as e:
        logger.error("No se pudo publicar evento en RabbitMQ: %s", e)
        return False
    finally:
        if connection and not connection.is_closed:
            try:
                connection.close()
            except Exception:
                pass
