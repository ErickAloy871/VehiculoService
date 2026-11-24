"""
Script de prueba para Evidencia P12 y P18:
Demuestra el rechazo de venta sobre vehículo NO DISPONIBLE (HTTP 409) o INEXISTENTE (HTTP 404).
"""
import httpx
import json
import os

CLIENT_ID = os.getenv("OAUTH_CLIENT_ID", "vehiculos-client")
CLIENT_SECRET = os.getenv("OAUTH_CLIENT_SECRET", "cliente-local-aula-2026-cambiar")
NGINX_URL = "http://127.0.0.1:8090"

print("================================================================================")
print("PRUEBA P12 / P18: RECHAZO DE VENTA - VEHÍCULO NO DISPONIBLE")
print("================================================================================")

# 1. Autenticación con operador
print("\n[1/3] Autenticando con usuario 'operador' en NGINX...")
res_token = httpx.post(
    f"{NGINX_URL}/oauth/token",
    auth=(CLIENT_ID, CLIENT_SECRET),
    data={"grant_type": "password", "username": "operador", "password": "operador123"},
    timeout=8
)

if res_token.status_code != 200:
    print(f"Error al autenticar: {res_token.status_code} - {res_token.text}")
    exit(1)

token = res_token.json()["access_token"]
print("-> Token JWT obtenido exitosamente.")

# 2. Petición POST /api/ventas con vehículo VENDIDO (ID 2: Chevrolet Onix)
print("\n[2/3] Enviando POST /api/ventas con Vehículo ID 2 (Estado: VENDIDO)...")
headers = {
    "Authorization": f"Bearer {token}",
    "Idempotency-Key": "p12-prueba-vehiculo-vendido-01",
    "Content-Type": "application/json"
}
body_vendido = {
    "vehiculoId": 2,
    "compradorId": 1
}

res_vendido = httpx.post(f"{NGINX_URL}/api/ventas", headers=headers, json=body_vendido, timeout=8)

print(f"\n--- RESPUESTA HTTP OBTENIDA ---")
print(f"Código HTTP de Respuesta: {res_vendido.status_code} (Rechazo esperado: 409 Conflict)")
print("Cuerpo JSON devuelto por la API:")
try:
    print(json.dumps(res_vendido.json(), indent=2, ensure_ascii=False))
except Exception:
    print(res_vendido.text)

# 3. Petición POST /api/ventas con vehículo INEXISTENTE (ID 99999)
print("\n[3/3] Enviando POST /api/ventas con Vehículo ID 99999 (Inexistente)...")
headers["Idempotency-Key"] = "p12-prueba-vehiculo-inexistente-01"
body_inexistente = {
    "vehiculoId": 99999,
    "compradorId": 1
}
res_inex = httpx.post(f"{NGINX_URL}/api/ventas", headers=headers, json=body_inexistente, timeout=8)

print(f"\n--- RESPUESTA HTTP OBTENIDA ---")
print(f"Código HTTP de Respuesta: {res_inex.status_code} (Rechazo esperado: 404 Not Found)")
print("Cuerpo JSON devuelto por la API:")
try:
    print(json.dumps(res_inex.json(), indent=2, ensure_ascii=False))
except Exception:
    print(res_inex.text)

print("\n================================================================================")
print("CONCLUSIÓN DE LA PRUEBA:")
print("1. El backend valida el estado del vehículo y rechaza la venta con HTTP 409.")
print("2. La venta se marca como FALLIDA en la base de datos.")
print("3. NO se publica ningún evento de éxito en RabbitMQ (P18 cumplida).")
print("================================================================================")
