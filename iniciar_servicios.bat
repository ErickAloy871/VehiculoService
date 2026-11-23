@echo off
title Sistema APE 04 - Lanzador de Servicios Backend
echo ==============================================================
echo INICIANDO ARQUITECTURA DISTRIBUIDA - APE 04
echo ==============================================================

:: 1. NGINX (Puerto 8090)
echo [1/5] Iniciando NGINX en puerto 8090...
cd /d "C:\nginx"
start "NGINX (8090)" nginx.exe

:: 2. Spring Boot Vehiculos - Instancia A (Puerto 8080)
echo [2/5] Iniciando Vehiculos Instancia A en puerto 8080...
cd /d "C:\Users\USER\Desktop\UTA\Sexto Semestre\SOA\soaproyectos\venta-vehiculos-api_security"
start "Spring Boot Vehiculos - A (:8080)" cmd /k "mvnw.cmd spring-boot:run"

:: 3. Spring Boot Vehiculos - Instancia B (Puerto 8082)
echo [3/5] Iniciando Vehiculos Instancia B en puerto 8082...
cd /d "C:\Users\USER\Desktop\UTA\Sexto Semestre\SOA\soaproyectos\venta-vehiculos-api_security"
start "Spring Boot Vehiculos - B (:8082)" cmd /k "mvnw.cmd spring-boot:run -Dspring-boot.run.arguments=--server.port=8082"

:: 4. FastAPI Ventas (Puerto 8000)
echo [4/5] Iniciando Ventas FastAPI en puerto 8000...
cd /d "C:\Users\USER\Desktop\UTA\Sexto Semestre\SOA\soaproyectos\ventas-api"
start "FastAPI Ventas (:8000)" cmd /k ".\.venv\Scripts\python.exe -m uvicorn app.main:app --port 8000"

:: 5. Spring Boot Notificaciones (Puerto 8081)
echo [5/5] Iniciando Notificaciones en puerto 8081...
cd /d "C:\Users\USER\Desktop\UTA\Sexto Semestre\SOA\soaproyectos\notificaciones-service"
start "Notificaciones RabbitMQ (:8081)" cmd /k "mvnw.cmd spring-boot:run"

echo ==============================================================
echo TODOS LOS SERVICIOS LANZADOS EN SUS VENTANAS INDIVIDUALES
echo ==============================================================
pause
