"""Manejo de X-Correlation-Id mediante contextvars (Reto S14)."""
import contextvars
from uuid import uuid4

_correlation_id_ctx = contextvars.ContextVar("correlation_id", default=None)


def set_correlation_id(cid: str | None = None) -> str:
    """Asigna o genera un Correlation ID para la solicitud actual."""
    val = cid.strip() if cid and cid.strip() else str(uuid4())
    _correlation_id_ctx.set(val)
    return val


def get_correlation_id() -> str:
    """Obtiene el Correlation ID del contexto actual o genera uno nuevo si no existe."""
    val = _correlation_id_ctx.get()
    if not val:
        val = str(uuid4())
        _correlation_id_ctx.set(val)
    return val

