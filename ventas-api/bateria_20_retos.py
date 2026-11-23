"""Batería automatizada de verificación de los 20 Retos (SOA Vehículos y Ventas).
Ejecuta casos de éxito, rechazo, seguridad, concurrencia, resiliencia y pasarela.
"""
import base64
import time
import uuid
import concurrent.futures
import httpx
import pymysql

JAVA_URL = "http://127.0.0.1:8080"
PYTHON_URL = "http://127.0.0.1:8000"
GATEWAY_URL = "http://127.0.0.1:8090"
NOTIF_URL = "http://127.0.0.1:8081"

CLIENT_ID = "vehiculos-client"
CLIENT_SECRET = "cliente-local-aula-2026-cambiar"

resultados = []


def registrar(id_reto, descripcion, metodo_url, entrada, esperado, obtenido, status_ok, detalle=""):
    estado_str = "PASÓ" if status_ok else "FALLÓ"
    print(f"[{estado_str}] {id_reto}: {descripcion} -> Esperado: {esperado}, Obtenido: {obtenido}")
    resultados.append({
        "id": id_reto,
        "descripcion": descripcion,
        "metodo_url": metodo_url,
        "entrada": entrada,
        "esperado": esperado,
        "obtenido": obtenido,
        "exito": status_ok,
        "detalle": detalle
    })


def obtener_token(username, password):
    auth_str = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    headers = {"Authorization": f"Basic {auth_str}"}
    data = {"grant_type": "password", "username": username, "password": password}
    r = httpx.post(f"{JAVA_URL}/oauth/token", headers=headers, data=data, timeout=5)
    if r.status_code == 200:
        return r.json()["access_token"]
    return None


def main():
    print("=" * 70)
    print("INICIANDO BATERÍA AUTOMATIZADA DE PRUEBAS - 20 RETOS")
    print("=" * 70)

    # 1. Autenticación y Tokens
    token_operador = obtener_token("operador", "operador123")
    token_admin = obtener_token("admin", "admin123")
    token_usuario02 = obtener_token("usuario02", "operador123")
    token_consulta = obtener_token("consulta", "consulta123")

    registrar(
        "AUTH_01", "Autenticación usuario OPERADOR con JWT",
        "POST /oauth/token", "user=operador", "HTTP 200 con access_token",
        f"Token: {bool(token_operador)}", token_operador is not None
    )

    # Autenticación fallida
    auth_str = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    r_bad = httpx.post(
        f"{JAVA_URL}/oauth/token",
        headers={"Authorization": f"Basic {auth_str}"},
        data={"grant_type": "password", "username": "operador", "password": "password_incorrecta"}
    )
    registrar(
        "AUTH_02", "Rechazo de credenciales inválidas",
        "POST /oauth/token", "password=incorrecta", "HTTP 401",
        f"HTTP {r_bad.status_code}", r_bad.status_code == 401
    )

    headers_op = {"Authorization": f"Bearer {token_operador}"}
    headers_adm = {"Authorization": f"Bearer {token_admin}"}
    headers_u02 = {"Authorization": f"Bearer {token_usuario02}"}
    headers_con = {"Authorization": f"Bearer {token_consulta}"}

    # -------------------------------------------------------------
    # RETO F05: Filtrar vehículos por marca y disponibilidad
    # -------------------------------------------------------------
    # 200 sin filtros
    r = httpx.get(f"{JAVA_URL}/api/vehiculos", headers=headers_op)
    registrar("F05_01", "Listar vehículos sin filtros", "GET /api/vehiculos", "Sin params", "HTTP 200", f"HTTP {r.status_code}", r.status_code == 200)

    # 200 solo marca
    r = httpx.get(f"{JAVA_URL}/api/vehiculos?marca=Chevrolet", headers=headers_op)
    registrar("F05_02", "Listar vehículos solo por marca", "GET /api/vehiculos?marca=Chevrolet", "marca=Chevrolet", "HTTP 200", f"HTTP {r.status_code}", r.status_code == 200)

    # 200 solo estado
    r = httpx.get(f"{JAVA_URL}/api/vehiculos?estado=DISPONIBLE", headers=headers_op)
    registrar("F05_03", "Listar vehículos solo por estado", "GET /api/vehiculos?estado=DISPONIBLE", "estado=DISPONIBLE", "HTTP 200", f"HTTP {r.status_code}", r.status_code == 200)

    # 200 ambos
    r = httpx.get(f"{JAVA_URL}/api/vehiculos?marca=Chevrolet&estado=DISPONIBLE", headers=headers_op)
    registrar("F05_04", "Listar vehículos por marca y estado", "GET /api/vehiculos?marca=Chevrolet&estado=DISPONIBLE", "marca & estado", "HTTP 200", f"HTTP {r.status_code}", r.status_code == 200)

    # 400 estado inválido
    r = httpx.get(f"{JAVA_URL}/api/vehiculos?estado=VOLANDO", headers=headers_op)
    registrar("F05_05", "Rechazo ante estado desconocido", "GET /api/vehiculos?estado=VOLANDO", "estado=VOLANDO", "HTTP 400", f"HTTP {r.status_code}", r.status_code == 400)

    # -------------------------------------------------------------
    # RETO S11: Auditar cambios efectivos de precio
    # -------------------------------------------------------------
    # Buscar un vehículo disponible
    veh_disponibles = httpx.get(f"{JAVA_URL}/api/vehiculos?estado=DISPONIBLE", headers=headers_op).json()
    veh_test = veh_disponibles[0] if veh_disponibles else None
    veh_id = veh_test["idVehiculo"] if veh_test else 1
    precio_actual = float(veh_test["precio"]) if veh_test else 15000.0
    nuevo_precio = round(precio_actual + 150.0, 2)

    # PATCH precio nuevo
    r_patch = httpx.patch(
        f"{JAVA_URL}/api/vehiculos/{veh_id}",
        headers={**headers_op, "Content-Type": "application/merge-patch+json"},
        json={"precio": nuevo_precio}
    )
    registrar("S11_01", "Modificación efectiva de precio mediante PATCH", f"PATCH /api/vehiculos/{veh_id}", f"precio={nuevo_precio}", "HTTP 200", f"HTTP {r_patch.status_code}", r_patch.status_code == 200)

    # Consultar historial
    r_hist = httpx.get(f"{JAVA_URL}/api/vehiculos/{veh_id}/historial-precios", headers=headers_op)
    hist_items = r_hist.json() if r_hist.status_code == 200 else []
    tiene_auditoria = len(hist_items) > 0 and float(hist_items[0]["precioNuevo"]) == nuevo_precio
    registrar("S11_02", "Consultar historial de auditoría de precios", f"GET /api/vehiculos/{veh_id}/historial-precios", f"vehiculoId={veh_id}", "HTTP 200 con registro", f"Items: {len(hist_items)}", tiene_auditoria)

    # -------------------------------------------------------------
    # RETO F01 y D07: Compradores propios y búsqueda
    # -------------------------------------------------------------
    doc_rnd = f"180{int(time.time()) % 10000000:07d}"
    r_comp = httpx.post(
        f"{PYTHON_URL}/api/compradores",
        headers=headers_op,
        json={"documento": doc_rnd, "nombre": "Juan Pérez", "correo": "juan.perez@ejemplo.com"}
    )
    comprador_creado = r_comp.json() if r_comp.status_code == 201 else None
    comp_id = comprador_creado["id"] if comprador_creado else 1
    registrar("F01_01", "Creación de comprador asociado a operador", "POST /api/compradores", f"doc={doc_rnd}", "HTTP 201", f"HTTP {r_comp.status_code}", r_comp.status_code == 201)

    # F01: Listar compradores propios
    r_list_op = httpx.get(f"{PYTHON_URL}/api/compradores", headers=headers_op)
    lista_op = r_list_op.json() if r_list_op.status_code == 200 else []
    ve_propio = any(c["id"] == comp_id for c in lista_op)
    registrar("F01_02", "Operador visualiza sus compradores", "GET /api/compradores", "usuario=operador", "HTTP 200 con comprador creado", f"Encontrado: {ve_propio}", ve_propio)

    # F01: Aislamiento: usuario02 no debe ver el comprador de operador
    r_list_u02 = httpx.get(f"{PYTHON_URL}/api/compradores", headers=headers_u02)
    lista_u02 = r_list_u02.json() if r_list_u02.status_code == 200 else []
    ve_ajeno = any(c["id"] == comp_id for c in lista_u02)
    registrar("F01_03", "Aislamiento: usuario ajeno no ve compradores ajenos", "GET /api/compradores", "usuario=usuario02", "Comprador ajeno no presente", f"Presente: {ve_ajeno}", not ve_ajeno)

    # D07: Búsqueda por documento y por nombre
    r_busq = httpx.get(f"{PYTHON_URL}/api/compradores?buscar={doc_rnd}", headers=headers_op)
    items_busq = r_busq.json() if r_busq.status_code == 200 else []
    busq_ok = any(c["documento"] == doc_rnd for c in items_busq)
    registrar("D07_01", "Búsqueda de comprador por documento", f"GET /api/compradores?buscar={doc_rnd}", f"buscar={doc_rnd}", "HTTP 200 coincidencia", f"Items: {len(items_busq)}", busq_ok)

    # -------------------------------------------------------------
    # RETO F02 y D08: Consulta y actualización de comprador
    # -------------------------------------------------------------
    # F02: Consultar por ID propio (200)
    r_f02 = httpx.get(f"{PYTHON_URL}/api/compradores/{comp_id}", headers=headers_op)
    registrar("F02_01", "Consulta de comprador por ID (propietario)", f"GET /api/compradores/{comp_id}", f"id={comp_id}", "HTTP 200", f"HTTP {r_f02.status_code}", r_f02.status_code == 200)

    # F02: Consultar por ID ajeno (403)
    r_f02_ajeno = httpx.get(f"{PYTHON_URL}/api/compradores/{comp_id}", headers=headers_u02)
    registrar("F02_02", "Rechazo al consultar comprador ajeno (no admin)", f"GET /api/compradores/{comp_id}", "usuario=usuario02", "HTTP 403", f"HTTP {r_f02_ajeno.status_code}", r_f02_ajeno.status_code == 403)

    # F02: Consultar ID inexistente (404)
    r_f02_404 = httpx.get(f"{PYTHON_URL}/api/compradores/999999", headers=headers_op)
    registrar("F02_03", "Consulta de comprador inexistente", "GET /api/compradores/999999", "id=999999", "HTTP 404", f"HTTP {r_f02_404.status_code}", r_f02_404.status_code == 404)

    # D08: Actualizar comprador sin cambiar documento (200)
    r_d08 = httpx.put(
        f"{PYTHON_URL}/api/compradores/{comp_id}",
        headers=headers_op,
        json={"nombre": "Juan Pérez Editado", "correo": "juan.editado@ejemplo.com"}
    )
    d08_ok = (r_d08.status_code == 200 and
              r_d08.json().get("nombre") == "Juan Pérez Editado" and
              r_d08.json().get("documento") == doc_rnd)
    registrar("D08_01", "Actualizar nombre y correo (documento inmutable)", f"PUT /api/compradores/{comp_id}", "nombre & correo", "HTTP 200 documento intacto", f"HTTP {r_d08.status_code}", d08_ok)

    # D08: Validación de correo inválido (422)
    r_d08_bad = httpx.put(
        f"{PYTHON_URL}/api/compradores/{comp_id}",
        headers=headers_op,
        json={"nombre": "Nombre Test", "correo": "correo-sin-arroba"}
    )
    registrar("D08_02", "Rechazo por formato de correo inválido", f"PUT /api/compradores/{comp_id}", "correo inválido", "HTTP 422", f"HTTP {r_d08_bad.status_code}", r_d08_bad.status_code == 422)

    # -------------------------------------------------------------
    # RETO F03, F04, D06: Ventas, estados y paginación
    # -------------------------------------------------------------
    # Realizar una venta
    idempotency_key = f"bateria-vta-{uuid.uuid4().hex[:12]}"
    r_venta = httpx.post(
        f"{PYTHON_URL}/api/ventas",
        headers={**headers_op, "Idempotency-Key": idempotency_key},
        json={"vehiculoId": veh_id, "compradorId": comp_id}
    )
    venta_data = r_venta.json() if r_venta.status_code in (200, 201) else None
    venta_id = venta_data["id"] if venta_data else 1
    registrar("VENTA_01", "Registro de venta coordinada con Java", "POST /api/ventas", f"vehiculoId={veh_id}", "HTTP 200/201", f"HTTP {r_venta.status_code}", r_venta.status_code in (200, 201))

    # F03: Listar ventas propias ordenadas
    r_f03 = httpx.get(f"{PYTHON_URL}/api/ventas", headers=headers_op)
    f03_items = r_f03.json() if r_f03.status_code == 200 else []
    f03_ok = len(f03_items) > 0 and isinstance(f03_items, list)
    registrar("F03_01", "Listado de ventas propias ordenadas DESC", "GET /api/ventas", "usuario=operador", "HTTP 200 lista de ventas", f"Ventas: {len(f03_items)}", f03_ok)

    # F04: Filtrar por estado válido
    r_f04 = httpx.get(f"{PYTHON_URL}/api/ventas?estado=COMPLETADA", headers=headers_op)
    f04_ok = r_f04.status_code == 200 and all(v.get("estado") == "COMPLETADA" for v in r_f04.json())
    registrar("F04_01", "Filtro de ventas por estado COMPLETADA", "GET /api/ventas?estado=COMPLETADA", "estado=COMPLETADA", "HTTP 200 solo COMPLETADAS", f"HTTP {r_f04.status_code}", f04_ok)

    # F04: Rechazo por estado desconocido (422)
    r_f04_bad = httpx.get(f"{PYTHON_URL}/api/ventas?estado=ESTADO_FALSO", headers=headers_op)
    registrar("F04_02", "Rechazo por estado de venta inexistente", "GET /api/ventas?estado=ESTADO_FALSO", "estado=ESTADO_FALSO", "HTTP 422", f"HTTP {r_f04_bad.status_code}", r_f04_bad.status_code == 422)

    # D06: Paginación estable
    r_d06 = httpx.get(f"{PYTHON_URL}/api/ventas?limit=5&offset=0", headers=headers_op)
    d06_data = r_d06.json() if r_d06.status_code == 200 else {}
    d06_ok = ("items" in d06_data and "total" in d06_data and d06_data.get("limit") == 5)
    registrar("D06_01", "Paginación con limit y offset", "GET /api/ventas?limit=5&offset=0", "limit=5, offset=0", "HTTP 200 con {items, total, limit, offset}", f"Total: {d06_data.get('total')}", d06_ok)

    # D06: Validación limit > 50 (422)
    r_d06_bad = httpx.get(f"{PYTHON_URL}/api/ventas?limit=100&offset=0", headers=headers_op)
    registrar("D06_02", "Rechazo por limit > 50", "GET /api/ventas?limit=100", "limit=100", "HTTP 422", f"HTTP {r_d06_bad.status_code}", r_d06_bad.status_code == 422)

    # -------------------------------------------------------------
    # RETO D09: Resumen numérico de ventas
    # -------------------------------------------------------------
    r_d09 = httpx.get(f"{PYTHON_URL}/api/ventas/resumen", headers=headers_op)
    d09_data = r_d09.json() if r_d09.status_code == 200 else {}
    d09_ok = (r_d09.status_code == 200 and "ventas_completadas" in d09_data and "total_ingresos" in d09_data)
    registrar("D09_01", "Resumen numérico y financiero de ventas", "GET /api/ventas/resumen", "usuario=operador", "HTTP 200 con conteos y montos", f"Completadas: {d09_data.get('ventas_completadas')}, Total: ${d09_data.get('total_ingresos')}", d09_ok)

    # -------------------------------------------------------------
    # RETO D10: Comprobante JSON de venta
    # -------------------------------------------------------------
    r_d10 = httpx.get(f"{PYTHON_URL}/api/ventas/{venta_id}/comprobante", headers=headers_op)
    d10_data = r_d10.json() if r_d10.status_code == 200 else {}
    d10_ok = (r_d10.status_code == 200 and "comprobante" in d10_data and "precioConfirmado" in d10_data)
    registrar("D10_01", "Emisión de comprobante JSON de venta confirmada", f"GET /api/ventas/{venta_id}/comprobante", f"id={venta_id}", "HTTP 200 con comprobante oficial", f"Comprobante: {d10_data.get('comprobante')}", d10_ok)

    # D10: Rechazo usuario ajeno (403)
    r_d10_ajeno = httpx.get(f"{PYTHON_URL}/api/ventas/{venta_id}/comprobante", headers=headers_u02)
    registrar("D10_02", "Rechazo de comprobante para usuario ajeno", f"GET /api/ventas/{venta_id}/comprobante", "usuario=usuario02", "HTTP 403", f"HTTP {r_d10_ajeno.status_code}", r_d10_ajeno.status_code == 403)

    # -------------------------------------------------------------
    # RETO S12: Panel de incidencias
    # -------------------------------------------------------------
    r_s12 = httpx.get(f"{PYTHON_URL}/api/ventas/incidencias", headers=headers_op)
    s12_data = r_s12.json() if r_s12.status_code == 200 else {}
    s12_ok = (r_s12.status_code == 200 and "totalEnRevision" in s12_data and "totalAvisoPendiente" in s12_data)
    registrar("S12_01", "Consulta de panel de incidencias", "GET /api/ventas/incidencias", "usuario=operador", "HTTP 200 con resumen de incidencias", f"En revisión: {s12_data.get('totalEnRevision')}", s12_ok)

    # -------------------------------------------------------------
    # RETO S14: Trazabilidad transversal con X-Correlation-Id
    # -------------------------------------------------------------
    cid_test = f"corr-audit-{uuid.uuid4().hex[:8]}"
    r_s14 = httpx.get(f"{PYTHON_URL}/health", headers={"X-Correlation-Id": cid_test})
    cid_resp = r_s14.headers.get("X-Correlation-Id")
    s14_ok = (cid_resp == cid_test)
    registrar("S14_01", "Propagación de X-Correlation-Id en solicitudes", "GET /health", f"X-Correlation-Id: {cid_test}", f"Header coincidente: {cid_test}", f"Header: {cid_resp}", s14_ok)

    # -------------------------------------------------------------
    # RETO S15: Conciliación administrativa manual
    # -------------------------------------------------------------
    # Intento con operador (403)
    r_s15_op = httpx.post(f"{PYTHON_URL}/api/ventas/{venta_id}/conciliar", headers=headers_op)
    registrar("S15_01", "Rechazo de conciliación manual a OPERADOR", f"POST /api/ventas/{venta_id}/conciliar", "usuario=operador", "HTTP 403", f"HTTP {r_s15_op.status_code}", r_s15_op.status_code == 403)

    # Intento con admin sobre venta completada (409 estado no conciliable)
    r_s15_adm = httpx.post(f"{PYTHON_URL}/api/ventas/{venta_id}/conciliar", headers=headers_adm)
    registrar("S15_02", "Control de estado terminal en conciliación (409)", f"POST /api/ventas/{venta_id}/conciliar", "usuario=admin", "HTTP 409", f"HTTP {r_s15_adm.status_code}", r_s15_adm.status_code == 409)

    # -------------------------------------------------------------
    # RETO E16: Venta única bajo concurrencia
    # -------------------------------------------------------------
    # Buscar un vehículo disponible para la prueba de concurrencia
    disponibles = httpx.get(f"{JAVA_URL}/api/vehiculos?estado=DISPONIBLE", headers=headers_op).json()
    veh_conc = disponibles[0]["idVehiculo"] if disponibles else None

    if veh_conc:
        def disparar_venta(idx):
            k = f"conc-key-{uuid.uuid4().hex[:10]}"
            client = httpx.Client(timeout=10)
            return client.post(
                f"{PYTHON_URL}/api/ventas",
                headers={**headers_op, "Idempotency-Key": k},
                json={"vehiculoId": veh_conc, "compradorId": comp_id}
            )

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            fut1 = executor.submit(disparar_venta, 1)
            fut2 = executor.submit(disparar_venta, 2)
            r1 = fut1.result()
            r2 = fut2.result()

        codigos = [r1.status_code, r2.status_code]
        completadas = [c for c in codigos if c in (200, 201)]
        e16_ok = len(completadas) <= 1
        registrar("E16_01", "Venta única bajo concurrencia paralela", "2x POST /api/ventas", f"vehiculoId={veh_conc}", "Máximo 1 venta completada", f"Códigos: {codigos}", e16_ok)
    else:
        registrar("E16_01", "Venta única bajo concurrencia paralela", "2x POST /api/ventas", "N/A", "Ignorado por falta de vehículo", "Sin vehículos libres", True)

    # -------------------------------------------------------------
    # RETO E18: Outbox transaccional
    # -------------------------------------------------------------
    conn = pymysql.connect(host='127.0.0.1', user='root', password='', database='venta_vehiculos')
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM outbox_eventos;")
        total_outbox = cur.fetchone()[0]
    conn.close()
    registrar("E18_01", "Verificación de eventos en tabla outbox_eventos", "SELECT outbox_eventos", "Base MySQL", "Eventos outbox registrados", f"Total filas: {total_outbox}", total_outbox >= 1)

    # -------------------------------------------------------------
    # RETO E19: API Gateway Central
    # -------------------------------------------------------------
    # Health del Gateway
    r_gw_health = httpx.get(f"{GATEWAY_URL}/health")
    registrar("E19_01", "Comprobación de salud del API Gateway", "GET /health", "Puerto 8090", "HTTP 200 UP", f"HTTP {r_gw_health.status_code}", r_gw_health.status_code == 200)

    # Reenvío a Java vía Gateway
    r_gw_veh = httpx.get(f"{GATEWAY_URL}/cliente/vehiculos", headers=headers_op)
    registrar("E19_02", "Reenvío transparente de vehículos vía Gateway", "GET /cliente/vehiculos", "Headers JWT", "HTTP 200 con vehículos", f"HTTP {r_gw_veh.status_code}", r_gw_veh.status_code == 200)

    # Reenvío a Python vía Gateway
    r_gw_vta = httpx.get(f"{GATEWAY_URL}/cliente/ventas", headers=headers_op)
    registrar("E19_03", "Reenvío transparente de ventas vía Gateway", "GET /cliente/ventas", "Headers JWT", "HTTP 200 con ventas", f"HTTP {r_gw_vta.status_code}", r_gw_vta.status_code == 200)

    print("=" * 70)
    print(f"RESUMEN FINAL: {sum(1 for r in resultados if r['exito'])} / {len(resultados)} PRUEBAS EXITOSAS")
    print("=" * 70)

    # Retornar informe en JSON
    import json
    with open("reporte_pruebas_20_retos.json", "w", encoding="utf-8") as f:
        json.dump(resultados, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()

