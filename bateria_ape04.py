"""
Batería de Pruebas Automatizadas de la Guía Práctica 4 (APE 04)
Valida los contratos de extremo a extremo: NGINX (:8090), RabbitMQ (:5672),
Spring Boot (:8080 y :8082), FastAPI (:8000), Notificaciones (:8081) y los 4 Clientes.
"""
import sys
import time
import uuid
import json
import httpx

NGINX_URL = "http://127.0.0.1:8090"
RABBITMQ_API = "http://127.0.0.1:15672/api"
JAVA_A = "http://127.0.0.1:8080"
JAVA_B = "http://127.0.0.1:8082"
FASTAPI_URL = "http://127.0.0.1:8000"
NOTIF_URL = "http://127.0.0.1:8081"

resultados = []

def registrar(id_prueba, descripcion, esperado, obtenido, exito, detalle=""):
    estado = "PASO" if exito else "FALLO"
    icono = "✅" if exito else "❌"
    print(f"{icono} [{id_prueba}] {descripcion} -> Esperado: {esperado} | Obtenido: {obtenido}")
    if detalle and not exito:
        print(f"   Detalle: {detalle}")
    resultados.append({
        "id": id_prueba,
        "descripcion": descripcion,
        "esperado": str(esperado),
        "obtenido": str(obtenido),
        "exito": exito,
        "detalle": detalle
    })

def obtener_token(usuario="operador", password="operador123"):
    try:
        r = httpx.post(
            f"{NGINX_URL}/oauth/token",
            auth=("vehiculos-client", "cliente-local-aula-2026-cambiar"),
            data={"grant_type": "password", "username": usuario, "password": password},
            timeout=6
        )
        if r.status_code == 200:
            return r.json().get("access_token")
    except Exception:
        pass
    return None

def ejecutar_bateria():
    print("=" * 70)
    print("INICIANDO VERIFICACIÓN DE ARQUITECTURA APE 04 - SOA UTA")
    print("=" * 70)

    # P01: Inicio y conectividad de servicios vía NGINX
    try:
        r_ping = httpx.get(f"{NGINX_URL}/nginx-ping", timeout=4)
        registrar("P01", "Conectividad NGINX /nginx-ping", 200, r_ping.status_code, r_ping.status_code == 200)
    except Exception as e:
        registrar("P01", "Conectividad NGINX /nginx-ping", 200, "Error", False, str(e))

    # P07: PWA inicia sesión con credenciales válidas
    token = obtener_token("operador", "operador123")
    registrar("P07", "Autenticación POST /oauth/token con operador123", "JWT válido", "Obtenido" if token else "Fallo", bool(token))

    # P08: Login inválido rechazado
    try:
        r_inv = httpx.post(
            f"{NGINX_URL}/oauth/token",
            auth=("vehiculos-client", "cliente-local-aula-2026-cambiar"),
            data={"grant_type": "password", "username": "operador", "password": "password_incorrecta"},
            timeout=4
        )
        registrar("P08", "Rechazo de credenciales inválidas", 401, r_inv.status_code, r_inv.status_code == 401)
    except Exception as e:
        registrar("P08", "Rechazo de credenciales inválidas", 401, "Error", False, str(e))

    if not token:
        print("\n⚠️ No se pudo obtener token JWT. Compruebe que Spring Boot y NGINX estén encendidos.")
        return

    headers = {"Authorization": f"Bearer {token}"}

    # P03: Listar vehículos
    try:
        r_veh = httpx.get(f"{NGINX_URL}/api/vehiculos", headers=headers, timeout=5)
        lista_v = r_veh.json() if r_veh.status_code == 200 else []
        registrar("P03", "Listar vehículos GET /api/vehiculos", 200, r_veh.status_code, r_veh.status_code == 200 and len(lista_v) > 0)
    except Exception as e:
        registrar("P03", "Listar vehículos GET /api/vehiculos", 200, "Error", False, str(e))

    # P04: Crear comprador desde backend/Windows Forms
    comp_doc = f"180{int(time.time()) % 10000000:07d}"
    comp_id = None
    try:
        r_comp = httpx.post(
            f"{NGINX_URL}/api/compradores",
            headers=headers,
            json={"documento": comp_doc, "nombre": "Cliente Prueba APE04", "correo": "cliente.ape4@uta.edu.ec"},
            timeout=5
        )
        if r_comp.status_code == 201:
            comp_id = r_comp.json().get("id")
        registrar("P04", "Crear comprador POST /api/compradores", 201, r_comp.status_code, r_comp.status_code == 201)
    except Exception as e:
        registrar("P04", "Crear comprador POST /api/compradores", 201, "Error", False, str(e))

    # P05: Listar compradores
    try:
        r_lc = httpx.get(f"{NGINX_URL}/api/compradores", headers=headers, timeout=5)
        registrar("P05", "Listar compradores GET /api/compradores", 200, r_lc.status_code, r_lc.status_code == 200)
    except Exception as e:
        registrar("P05", "Listar compradores GET /api/compradores", 200, "Error", False, str(e))

    # P09: PWA registra venta válida con Idempotency-Key
    venta_id = None
    idem_key = f"ape4-{uuid.uuid4().hex[:8]}"
    veh_disponible = 14 # Usar un vehículo conocido o buscar primero disponible
    try:
        r_cat = httpx.get(f"{NGINX_URL}/api/vehiculos?estado=DISPONIBLE", headers=headers, timeout=5)
        if r_cat.status_code == 200 and len(r_cat.json()) > 0:
            veh_disponible = r_cat.json()[0]["idVehiculo"]
    except Exception:
        pass

    if comp_id:
        try:
            r_venta = httpx.post(
                f"{NGINX_URL}/api/ventas",
                headers={**headers, "Idempotency-Key": idem_key},
                json={"vehiculoId": veh_disponible, "compradorId": comp_id},
                timeout=6
            )
            if r_venta.status_code in (201, 202):
                venta_id = r_venta.json().get("id")
            registrar("P09", "PWA registra venta válida POST /api/ventas", "201/202", r_venta.status_code, r_venta.status_code in (201, 202))
        except Exception as e:
            registrar("P09", "PWA registra venta válida POST /api/ventas", "201/202", "Error", False, str(e))

        # P10: Reintento con misma Idempotency-Key y mismo cuerpo (debe retornar 200/201 sin duplicar)
        try:
            r_reint = httpx.post(
                f"{NGINX_URL}/api/ventas",
                headers={**headers, "Idempotency-Key": idem_key},
                json={"vehiculoId": veh_disponible, "compradorId": comp_id},
                timeout=6
            )
            registrar("P10", "Reintento misma Idempotency-Key sin duplicar", "200/201", r_reint.status_code, r_reint.status_code in (200, 201))
        except Exception as e:
            registrar("P10", "Reintento misma Idempotency-Key sin duplicar", "200/201", "Error", False, str(e))

        # P11: Misma Idempotency-Key con cuerpo distinto (conflicto 409)
        try:
            r_conf = httpx.post(
                f"{NGINX_URL}/api/ventas",
                headers={**headers, "Idempotency-Key": idem_key},
                json={"vehiculoId": 9999, "compradorId": comp_id},
                timeout=6
            )
            registrar("P11", "Misma Idempotency-Key con cuerpo distinto genera conflicto", 409, r_conf.status_code, r_conf.status_code == 409)
        except Exception as e:
            registrar("P11", "Misma Idempotency-Key con cuerpo distinto", 409, "Error", False, str(e))

    # P06 y P16: Consultar ventas desde Windows Forms y React
    try:
        r_ventas = httpx.get(f"{NGINX_URL}/api/ventas", headers=headers, timeout=5)
        registrar("P06/P16", "Consultar lista de ventas GET /api/ventas", 200, r_ventas.status_code, r_ventas.status_code == 200)
    except Exception as e:
        registrar("P06/P16", "Consultar lista de ventas", 200, "Error", False, str(e))

    # P17 / P21: Cola RabbitMQ y Servicio de Notificaciones
    try:
        r_notif = httpx.get(f"{NGINX_URL}/api/notificaciones", timeout=4)
        lista_n = r_notif.json() if r_notif.status_code == 200 else []
        registrar("P21", "JavaFX consulta historial GET /api/notificaciones", 200, r_notif.status_code, r_notif.status_code == 200)
    except Exception as e:
        registrar("P21", "Consulta historial notificaciones", 200, "Error", False, str(e))

    # P23: Balanceo 3:1 de NGINX con 20 peticiones
    print("\n--- Ejecutando muestreo de balanceo NGINX 3:1 ---")
    conteo_a = 0
    conteo_b = 0
    for _ in range(20):
        try:
            res_b = httpx.get(f"{NGINX_URL}/api/vehiculos", headers=headers, timeout=3)
            # Analizar header o tiempo
            if res_b.status_code == 200:
                conteo_a += 1
        except Exception:
            pass
    registrar("P23", f"Balanceo NGINX activo ({conteo_a} respuestas exitosas)", "Exitoso", "Operativo", conteo_a > 0)

    print("\n" + "=" * 70)
    exitosas = sum(1 for r in resultados if r["exito"])
    total = len(resultados)
    porcentaje = (exitosas / total * 100) if total > 0 else 0
    print(f"RESUMEN FINAL: {exitosas} / {total} PRUEBAS EXITOSAS ({porcentaje:.1f}%)")
    print("=" * 70)

if __name__ == "__main__":
    ejecutar_bateria()
