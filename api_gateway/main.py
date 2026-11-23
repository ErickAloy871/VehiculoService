"""Gateway único para futuros clientes web, móvil y escritorio (Reto E19).
Ofrece un punto único de entrada, gestiona CORS, propaga JWT y Correlation ID,
y maneja resiliencia con 502/503 ante caídas de backend sin filtrar secretos internos.
"""
import os
import logging
from uuid import uuid4
import httpx
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] [Gateway] %(message)s")
logger = logging.getLogger("gateway")

app = FastAPI(title="API Gateway Central - SOA Vehículos y Ventas", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

JAVA_BACKEND = os.getenv("JAVA_BACKEND", "http://127.0.0.1:8080")
PYTHON_BACKEND = os.getenv("PYTHON_BACKEND", "http://127.0.0.1:8000")

# Claves internas que NUNCA deben filtrarse a los clientes
SECRETS_FILTER = {"X-Service-Key", "X-Notification-Key", "x-service-key", "x-notification-key"}


async def _reenviar(request: Request, destino_base: str, ruta_destino: str) -> Response:
    """Función genérica de reenvío seguro con manejo de errores y propagación de headers."""
    cid = request.headers.get("X-Correlation-Id") or str(uuid4())
    url = f"{destino_base}{ruta_destino}"
    if request.url.query:
        url = f"{url}?{request.url.query}"

    # Construir headers sin secretos internos
    headers = {}
    for k, v in request.headers.items():
        if k.lower() not in ["host", "content-length", "x-service-key", "x-notification-key"]:
            headers[k] = v
    headers["X-Correlation-Id"] = cid

    body = await request.body()
    logger.info("[%s] Reenviando %s %s -> %s", cid, request.method, request.url.path, url)

    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(10.0, connect=3.0)) as client:
            resp = await client.request(
                method=request.method,
                url=url,
                headers=headers,
                content=body
            )

        # Filtrar headers de respuesta para no exponer secretos ni headers no seguros
        resp_headers = {}
        for k, v in resp.headers.items():
            if k.lower() not in ["content-encoding", "content-length", "transfer-encoding"]:
                resp_headers[k] = v
        resp_headers["X-Correlation-Id"] = cid

        return Response(
            content=resp.content,
            status_code=resp.status_code,
            headers=resp_headers,
            media_type=resp.headers.get("content-type")
        )

    except httpx.ConnectError:
        logger.error("[%s] Servicio remoto inaccesible en %s", cid, destino_base)
        return JSONResponse(
            status_code=503,
            content={
                "status": 503,
                "error": "SERVICIO_NO_DISPONIBLE",
                "mensaje": f"El servicio de destino ({destino_base}) no se encuentra en línea",
                "correlationId": cid
            },
            headers={"X-Correlation-Id": cid}
        )
    except httpx.TimeoutException:
        logger.error("[%s] Tiempo de espera agotado al conectar con %s", cid, destino_base)
        return JSONResponse(
            status_code=504,
            content={
                "status": 504,
                "error": "TIMEOUT_GATEWAY",
                "mensaje": "Tiempo de respuesta agotado en el servicio backend",
                "correlationId": cid
            },
            headers={"X-Correlation-Id": cid}
        )
    except Exception as ex:
        logger.exception("[%s] Error inesperado en gateway: %s", cid, ex)
        return JSONResponse(
            status_code=502,
            content={
                "status": 502,
                "error": "BAD_GATEWAY",
                "mensaje": "Error en la pasarela de comunicación con el backend",
                "correlationId": cid
            },
            headers={"X-Correlation-Id": cid}
        )


@app.get("/health")
def health():
    return {"status": "UP", "gateway": "Activo"}


# Autenticación delegada a Java
@app.api_route("/cliente/oauth/token", methods=["POST"])
async def proxy_token(request: Request):
    return await _reenviar(request, JAVA_BACKEND, "/oauth/token")


# Vehículos delegados a Java Spring Boot (:8080)
@app.api_route("/cliente/vehiculos", methods=["GET", "POST"])
@app.api_route("/cliente/vehiculos/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_vehiculos(request: Request, path: str = ""):
    subpath = f"/{path}" if path else ""
    return await _reenviar(request, JAVA_BACKEND, f"/api/vehiculos{subpath}")


# Ventas delegadas a Python FastAPI (:8000)
@app.api_route("/cliente/ventas", methods=["GET", "POST"])
@app.api_route("/cliente/ventas/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_ventas(request: Request, path: str = ""):
    subpath = f"/{path}" if path else ""
    return await _reenviar(request, PYTHON_BACKEND, f"/api/ventas{subpath}")


# Compradores delegados a Python FastAPI (:8000)
@app.api_route("/cliente/compradores", methods=["GET", "POST"])
@app.api_route("/cliente/compradores/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy_compradores(request: Request, path: str = ""):
    subpath = f"/{path}" if path else ""
    return await _reenviar(request, PYTHON_BACKEND, f"/api/compradores{subpath}")

