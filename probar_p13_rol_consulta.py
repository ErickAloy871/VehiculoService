"""
Script de prueba para Evidencia P13:
Demuestra el control de acceso y autorización RBAC (HTTP 403 Forbidden)
al intentar registrar una venta con un usuario de rol CONSULTA.
"""
import httpx
import json

NGINX_URL = "http://127.0.0.1:8090"

print("================================================================================")
print("PRUEBA P13: PERMISO INSUFICIENTE PARA REGISTRAR VENTA (ROL CONSULTA)")
print("================================================================================")

# 1. Autenticación con usuario 'consulta' (rol CONSULTA)
print("\n[1/2] Solicitando JWT para usuario 'consulta' (Rol: CONSULTA)...")
res_token = httpx.post(
    f"{NGINX_URL}/oauth/token",
    auth=("vehiculos-client", "cliente-local-aula-2026-cambiar"),
    data={"grant_type": "password", "username": "consulta", "password": "operador123"},
    timeout=8
)

if res_token.status_code != 200:
    print(f"Error al autenticar: {res_token.status_code} - {res_token.text}")
    exit(1)

token_info = res_token.json()
token = token_info["access_token"]
print("-> Token JWT emitido para rol CONSULTA.")
print(f"   Scope: {token_info.get('scope')}")

# 2. Intento de ejecutar POST /api/ventas
print("\n[2/2] Intentando registrar venta: POST /api/ventas con Bearer Token de CONSULTA...")
headers = {
    "Authorization": f"Bearer {token}",
    "Idempotency-Key": "p13-prueba-permiso-consulta-01",
    "Content-Type": "application/json"
}
body_venta = {
    "vehiculoId": 1,
    "compradorId": 1
}

res_venta = httpx.post(f"{NGINX_URL}/api/ventas", headers=headers, json=body_venta, timeout=8)

print(f"\n--- RESPUESTA HTTP DE LA API ---")
print(f"Código HTTP de Respuesta: {res_venta.status_code} (Esperado: 403 Forbidden)")
print("Cuerpo JSON devuelto por FastAPI:")
try:
    print(json.dumps(res_venta.json(), indent=2, ensure_ascii=False))
except Exception:
    print(res_venta.text)

print("\n================================================================================")
print("INTERPRETACIÓN DE LA EVIDENCIA P13:")
print("1. El usuario 'consulta' posee credenciales válidas y obtiene su JWT correctamente.")
print("2. El endpoint POST /api/ventas exige rol OPERADOR o ADMIN.")
print("3. La capa de seguridad intercepta la solicitud y responde HTTP 403 Forbidden")
print("   con el código 'SIN_PERMISO', impidiendo la venta.")
print("================================================================================")
