# VENTAS-API — Proyecto Python completo, comentado para clase


## Archivos principales

```text
ventas_api_python_comentada/
├─ README.md                         <-- estas instrucciones
├─ requirements.txt                 <-- dependencias de ejecución
├─ requirements-dev.txt             <-- tests opcionales
├─ .env.example                     <-- variables de conexión, SIN secretos
├─ .gitignore
├─ alembic.ini                      <-- configuración de migraciones
├─ alembic/
│  ├─ env.py                         <-- solo las tablas Python
│  ├─ script.py.mako
│  └─ versions/0001_ventas.py       <-- crea compradores y ventas
├─ app/
│  ├─ __init__.py
│  ├─ config.py                      <-- lee .env
│  ├─ db.py                          <-- SQLAlchemy + MySQL
│  ├─ models.py                      <-- ORM Comprador, Venta
│  ├─ schemas.py                     <-- Pydantic: JSON válido
│  ├─ errors.py                      <-- errores 4xx / 5xx
│  ├─ security.py                    <-- consulta JWT y roles en Java
│  ├─ main.py                        <-- instancia FastAPI y /health
│  ├─ worker.py                      <-- reintentos pendientes
│  ├─ clients/vehiculos_client.py    <-- GET/POST/PUT hacia Java
│  ├─ repositories/venta_repository.py
│  ├─ services/venta_service.py      <-- idempotencia, reserva, venta, aviso
│  └─ routers/ventas.py             <-- endpoints REST
├─ CAMBIO_EN_JAVA/                   <-- reemplazo puntual de filtro Java
└─ tests/test_integracion_simulada.py
```

## 0. Antes de comenzar, CORRIGE el receptor Java

En el ZIP original `notificaciones-service/.../security/NotificacionKeyFilter.java` lee **`X-Notificacion-Key`**, mientras que Java emisor y Python envían **`X-Notification-Key`**. De lo contrario los avisos retornan **401**.

En `CAMBIO_EN_JAVA/notificaciones-service/src/main/java/ec/edu/uta/notificaciones/security/NotificacionKeyFilter.java` está el **filtro completo corregido**. Copia ese archivo a la misma ruta de tu proyecto Java `notificaciones-service`, sustituyendo solo el archivo anterior, **recompila y reinicia** el servicio. El archivo de `CAMBIO_EN_JAVA` no forma parte del proyecto Python.

No cambies el valor de la clave que ya usan tus dos aplicaciones Java: `app.notificacion-key` en el receptor y `servicios.notificaciones.key` en el emisor. Ambos deben coincidir con `NOTIFICACIONES_KEY` de Python. La otra clave, `app.security.ventas-key`, coincide con `VENTAS_SERVICE_KEY` de Python.

## 1. Prerrequisitos

- Windows + PowerShell, Python 3.13(o la ultima) instalado (`py -3.13 --version`). Adapta `py` si usas una versión compatible distinta.
- Java `venta-vehiculos-api_security` arrancado y funcional en `http://127.0.0.1:8080`.
- Java `notificaciones-service` arrancado en `http://127.0.0.1:8081` con el filtro corregido.
- XAMPP/MySQL funcionando en puerto 3306; base `venta_vehiculos` **ya creada** con las tablas Java originales.
- Postman para ejecutar las solicitudes.
- Una cuenta de Java con rol `OPERADOR` o `ADMIN`, y su token de acceso (`access_token`).

## 2. Abrir el proyecto y crear el entorno Python

Extrae el ZIP en una carpeta, por ejemplo `C:\proyectos\ventas_api_python_comentada`. Dentro de PowerShell:

```powershell
Set-Location 'C:\proyectos\ventas_api_python'
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Si las dependencias se instalaron sin error, **no ejecutes** `alembic init` y **no crees manualmente** los 17 archivos. Ambos ya están completos en el ZIP.

## 3. Configurar las claves y puertos

```powershell
Copy-Item .env.example .env
notepad .env
```

En `.env` sustituye los dos valores de ejemplo:

```ini
# MISMA clave que app.security.ventas-key en Java de vehículos
VENTAS_SERVICE_KEY=<pegar el valor real, sin los símbolos <> >

# MISMA clave que app.notificacion-key en Java de notificaciones
NOTIFICACIONES_KEY=<pegar el valor real, sin los símbolos <> >
```

La primera cabecera es `X-Service-Key` y la segunda `X-Notification-Key` **después de corregir Java**. Copia el valor exacto (mínimo 32 caracteres). No confundas dichas claves con el JWT del usuario. Si XAMPP utiliza contraseña, añade `DB_PASSWORD=...`; no asumas que siempre es vacía. Mantén el archivo `.env` privado; `.gitignore` lo excluye.

## 4. Verificar la base y crear SOLO las tablas Python

Haz antes un respaldo de la base de datos si tiene información importante. En phpMyAdmin, sobre `venta_vehiculos` ejecuta:

```sql
USE venta_vehiculos;
SHOW TABLES;
SELECT COUNT(*) FROM vehiculos;
SELECT COUNT(*) FROM usuarios_api;
```

Confirma que `compradores`, `ventas` y `alembic_version` **aún no existen**; si existen, **no repitas** la migración sin revisar versiones y estructura. Si no existen, desde PowerShell:

```powershell
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m alembic current
```

La migración `0001_ventas.py` crea `compradores` y `ventas`, junto con la FK comprador_id. **No borra ni reemplaza** `vehiculos`, `usuarios_api` o `reservas`. Evita `alembic revision --autogenerate` para esta primera migración, porque ya está escrita.

## 5. Ejecutar Python y comprobar la documentación automática

```powershell
.\.venv\Scripts\python.exe -m compileall app alembic
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8002 --reload
```

Abre:

- `http://127.0.0.1:8002/health` → debe responder `{"status":"UP"}`. **Esto solo prueba que FastAPI arrancó**; no demuestra conexión a Java o MySQL.
- `http://127.0.0.1:8002/docs` → documentación Swagger/OpenAPI con los endpoints.

## 6. Pruebas Postman paso a paso

**Paso A.** Obtén el `access_token` mediante tu autenticación Java, por ejemplo `POST http://127.0.0.1:8080/oauth/token`, con el cliente Basic y el usuario válidos, siguiendo las credenciales y parámetros originales del proyecto. Copia el `access_token` (no el refresh token).

**Paso B.** Importa `POSTMAN/Ventas_Python_Java.postman_collection.json` en Postman. En Variables de la colección, escribe `token` con el JWT real, sin prefijo `Bearer` y mantén `python_url` como `http://127.0.0.1:8002`.

**Paso C.** Prueba el endpoint de comprador:

```http
POST http://127.0.0.1:8002/api/compradores
Authorization: Bearer <access_token>
Content-Type: application/json
```

```json
{"documento":"1801234567","nombre":"Comprador de prueba","correo":"comprador@example.com"}
```

Debes obtener **201**. Guarda el `id` real devuelto. No copies un ID inventado.

**Paso D.** Registra una venta con vehículo **DISPONIBLE** en Java:

```http
POST http://127.0.0.1:8002/api/ventas
Authorization: Bearer <access_token>
Idempotency-Key: venta-aula-0001
Content-Type: application/json
```

```json
{"vehiculoId":1,"compradorId":1}
```

Cambia ambos números por identificadores **reales** (el ID del comprador creado y el ID de un vehículo disponible). Python pide la reserva a Java, Java confirma el vehículo y Python guarda el resultado. La respuesta es **201** al completarse, **202** si queda pendiente de conciliación, **404** ante comprador inexistente, o **409** si Java confirma que el vehículo no se puede vender.

**Paso E.** Consulta `GET http://127.0.0.1:8002/api/ventas/{id}` con el mismo JWT.

**Paso F.** Repite la venta con el mismo cuerpo y la misma `Idempotency-Key`: si está completada debe devolver **200 y el mismo ID**, sin duplicar la venta.

**Paso G.** Cambia `vehiculoId` y conserva la misma clave: debe devolver **409 CLAVE_REUTILIZADA**. Si omites la clave, FastAPI debe devolver **422**.

**Paso H.** Apaga el receptor de notificaciones, realiza una venta nueva con otro vehículo disponible, y verifica `notificacion=PENDIENTE`. Enciende el receptor, ejecuta una vez:

```powershell
.\.venv\Scripts\python.exe -m app.worker --once
```

La notificación pendiente debe pasar a `ENVIADA` si Java acepta el aviso. El worker no está obligado a ejecutarse durante las pruebas iniciales: déjalo para comprobar tolerancia a fallos.

## 7. SQL para comprobar que los resultados son reales

```sql
USE venta_vehiculos;
SELECT id, documento, nombre, correo FROM compradores ORDER BY id DESC LIMIT 10;
SELECT id, operacion_id, vehiculo_id, comprador_id, estado, precio_acordado, notificacion FROM ventas ORDER BY id DESC LIMIT 10;
SELECT id_vehiculo, placa, estado, precio FROM vehiculos ORDER BY id_vehiculo DESC LIMIT 10;
SELECT id, operacion_id, vehiculo_id, estado, precio FROM reservas ORDER BY id DESC LIMIT 10;
SELECT * FROM alembic_version;
```

La venta `COMPLETADA` debe corresponder a reserva `CONFIRMADA` y vehículo `VENDIDO` en Java. Si el receptor está apagado, la venta puede estar completada y la notificación continuar pendiente.

## 8. Pruebas automáticas opcionales (SIN tocar MySQL)

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q tests\test_integracion_simulada.py
```

Comprueban reglas centrales usando SQLite temporal y sustitutos de las llamadas a Java; no envían solicitudes reales a los servicios del docente. Para una práctica docente esto permite demostrar cómo separar pruebas unitarias/de integración simulada de la **integración real con servicios**.

## 9. Errores habituales

| Síntoma | Revisión |
|---|---|
| 401 desde Python | JWT de acceso ausente o inválido; revisar `Authorization: Bearer` |
| 403 desde Python | El usuario no tiene `ROLE_OPERADOR` ni `ROLE_ADMIN`, o intenta consultar recursos ajenos |
| 422 | JSON incompleto, campo extra o falta `Idempotency-Key` |
| 503 identidad | Java :8080 apagado o inaccesible |
| 202/EN_REVISION | Ruta/clave incorrecta de reservas o timeout Java; no repetir con clave distinta |
| Notificación PENDIENTE | Receptor 8081 apagado, clave errónea o cabecera sin corregir en Java |
| Error Alembic | Base apagada, credenciales incorrectas o las tablas Python ya existen |
| Error PyMySQL | Reinstala con el Python del `.venv`: `python.exe -m pip install -r requirements.txt` |


