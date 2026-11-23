"""Entrada de la API FastAPI; documentación OpenAPI, health y middleware S14."""
import logging
from fastapi import FastAPI, Request
from app.errors import instalar
from app.routers.ventas import router
from app.correlation import set_correlation_id, get_correlation_id

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("ventas_api")

app = FastAPI(title="API de ventas de vehículos", version="1.0.0")

# S14: Middleware de trazabilidad transversal con Correlation ID
@app.middleware("http")
async def correlation_middleware(request: Request, call_next):
    cid = request.headers.get("X-Correlation-Id")
    cid_efectivo = set_correlation_id(cid)
    logger.info(f"[{cid_efectivo}] Solicitud entrante: {request.method} {request.url.path}")
    response = await call_next(request)
    response.headers["X-Correlation-Id"] = cid_efectivo
    logger.info(f"[{cid_efectivo}] Respuesta saliente: {response.status_code}")
    return response

instalar(app)
app.include_router(router)


@app.get("/health")
def health():
    return {"status": "UP"}
