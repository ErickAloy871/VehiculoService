# APE 04 - Arquitectura Multicanal de Vehículos, Compradores, Ventas y Notificaciones
**Universidad Técnica de Ambato - Facultad de Ingeniería en Sistemas, Electrónica e Industrial**  
**Carrera de Software - Sexto Semestre - Arquitectura Orientada a Servicios (SOA)**

---

## 1. Descripción de la Arquitectura
Sistema distribuido multicanal compuesto por 7 componentes integrados:
1. **NGINX Gateway & Reverse Proxy (Puerto 8090)**: Puerta de entrada REST única, balanceo de carga ponderado 3:1 entre instancias de vehículos y tolerancia a fallos.
2. **Servicio de Vehículos y Autenticación (Java Spring Boot)**:
   - Instancia A: `127.0.0.1:8080`
   - Instancia B: `127.0.0.1:8082`
   - Emisión y validación de tokens JWT (`/oauth/token`), CRUD de vehículos y consulta de catálogo.
3. **Servicio de Ventas y Compradores (Python FastAPI - Puerto 8000)**:
   - Gestión de compradores, registro idempotente de ventas (`Idempotency-Key`) y publicación de eventos en RabbitMQ.
4. **Servicio de Notificaciones (Java Spring Boot - Puerto 8081)**:
   - Consumidor RabbitMQ (`@RabbitListener(queues = "notificaciones.ventas")`), persistencia de avisos y endpoint REST de consulta para clientes.
5. **RabbitMQ Message Broker (Puertos 5672 AMQP / 15672 Management UI)**:
   - Cola durable `notificaciones.ventas`, entrega persistente de mensajes JSON.
6. **Bases de Datos MySQL/MariaDB (Puerto 3306)**:
   - Esquemas `venta_vehiculos` y `ventas_db`.
7. **Cuatro Aplicaciones Cliente**:
   - **Windows Forms (.NET 8)**: Administración de vehículos, compradores y consulta de ventas con JWT.
   - **PWA Móvil (HTML/JS/CSS - Puerto 5174)**: Login con credenciales, selector de vehículo/comprador y canal **exclusivo** de registro de ventas con `Idempotency-Key`.
   - **React Web (Vite + Fetch - Puerto 5173)**: Consulta de catálogo, filtro en tiempo real por marca y listado de ventas.
   - **JavaFX (Java 17)**: Monitor de escritorio con auto-sondeo cada 3 segundos a `/api/notificaciones`.

---

## 2. Mapa de Puertos y Enrutamiento NGINX (8090)

| Ruta NGINX | Destino Backend | Protocolo / Propósito |
|---|---|---|
| `/oauth/token` | Upstream `vehiculos_backend` (8080 peso 3, 8082 peso 1) | Autenticación y emisión de JWT |
| `/api/vehiculos` | Upstream `vehiculos_backend` (8080 peso 3, 8082 peso 1) | Catálogo y CRUD de vehículos |
| `/api/compradores` | `http://127.0.0.1:8000/api/compradores` | Gestión de compradores en FastAPI |
| `/api/ventas` | `http://127.0.0.1:8000/api/ventas` | Registro (PWA) y consulta de ventas |
| `/api/notificaciones` | `http://127.0.0.1:8081/api/notificaciones` | Historial de avisos para JavaFX |
| `/nginx-ping` | Interno NGINX (sin tocar backend) | Diagnóstico de Gateway (`HTTP 200 UP`) |

---

## 3. Requisitos de Entorno
- **Sistema Operativo**: Windows 10/11
- **Java**: JDK 17 o superior
- **.NET**: .NET SDK 8.0 o 10.0
- **Python**: 3.10 o superior con `pip` y entorno virtual
- **Node.js**: v18 o superior con `npm`
- **Docker Desktop**: Para el contenedor de RabbitMQ
- **XAMPP / MySQL / MariaDB**: Puerto 3306 activo
- **NGINX**: Instalado en `C:\nginx` (o portable)

---

## 4. Orden de Arranque Obligatorio

### Paso 1: Servicios de Infraestructura
1. **MySQL**: Iniciar servicio MySQL en el panel de control de XAMPP (Puerto 3306).
2. **RabbitMQ**: Iniciar el contenedor Docker:
   ```bash
   docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management
   ```
   *Acceso al panel web:* `http://localhost:15672` (usuario: `guest`, contraseña: `guest`).

### Paso 2: Backend y Gateway (Script Automatizado)
Ejecutar el script que levanta NGINX, ambas instancias de Spring Boot, FastAPI y Notificaciones:
```cmd
iniciar_servicios.bat
```

*O arranque manual por consola:*
- **NGINX**:
  ```cmd
  cd C:\nginx
  nginx.exe
  ```
- **Vehículos A (8080)**:
  ```cmd
  cd venta-vehiculos-api_security
  mvnw.cmd spring-boot:run
  ```
- **Vehículos B (8082)**:
  ```cmd
  cd venta-vehiculos-api_security
  mvnw.cmd spring-boot:run -Dspring-boot.run.arguments=--server.port=8082
  ```
- **FastAPI Ventas (8000)**:
  ```cmd
  cd ventas-api
  .\.venv\Scripts\activate
  uvicorn app.main:app --port 8000
  ```
- **Notificaciones (8081)**:
  ```cmd
  cd notificaciones-service
  mvnw.cmd spring-boot:run
  ```

### Paso 3: Aplicaciones Cliente (Script Automatizado)
Ejecutar:
```cmd
iniciar_clientes.bat
```

*O arranque manual de cada cliente:*
- **Windows Forms**:
  ```cmd
  cd Proyecto_Vehiculos
  dotnet run
  ```
- **PWA Móvil (Puerto 5174)**:
  ```cmd
  cd AplicacionMovilPWA
  node server.mjs
  ```
  Abrir navegador en `http://localhost:5174`
- **React Web (Puerto 5173)**:
  ```cmd
  cd react-fetch-vehiculos
  npm run dev
  ```
  Abrir navegador en `http://localhost:5173`
- **JavaFX**:
  ```cmd
  cd consultarvehiculosjavafx
  mvnw.cmd javafx:run
  ```

---

## 5. Batería de Pruebas Automatizada (P01 - P23)
Para validar la integración completa de extremo a extremo, ejecutar:
```cmd
cd ventas-api
.\.venv\Scripts\python.exe ..\bateria_ape04.py
```
El script reporta el 100% de cumplimiento en las pruebas de autenticación JWT, creación de datos, idempotencia de ventas, tolerancia a fallos y entrega de eventos RabbitMQ.
