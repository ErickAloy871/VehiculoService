@echo off
title Sistema APE 04 - Lanzador de Clientes
echo ==============================================================
echo INICIANDO LOS 4 CLIENTES DE LA ARQUITECTURA - APE 04
echo ==============================================================

:: 1. Windows Forms
echo [1/4] Iniciando Windows Forms (Administracion)...
cd /d "C:\Users\USER\Desktop\UTA\Sexto Semestre\SOA\soaproyectos\Proyecto_Vehiculos"
start "Windows Forms Administracion" cmd /k "dotnet run --project Proyecto_Vehiculos.csproj"

:: 2. PWA Movil
echo [2/4] Iniciando PWA Movil en puerto 5174...
cd /d "C:\Users\USER\Desktop\UTA\Sexto Semestre\SOA\soaproyectos\AplicacionMovilPWA"
start "PWA Movil (Puerto 5174)" cmd /k "node server.mjs --port=5174"

:: 3. React Vite Web
echo [3/4] Iniciando React Vite en puerto 5173...
cd /d "C:\Users\USER\Desktop\UTA\Sexto Semestre\SOA\soaproyectos\react-fetch-vehiculos"
start "React Web (Puerto 5173)" cmd /k "npm run dev"

:: 4. JavaFX Monitor Notificaciones
echo [4/4] Iniciando JavaFX Monitor Notificaciones...
cd /d "C:\Users\USER\Desktop\UTA\Sexto Semestre\SOA\soaproyectos\consultarvehiculosjavafx"
start "JavaFX Monitor Notificaciones" cmd /k "mvnw.cmd javafx:run"

echo ==============================================================
echo CLIENTES INICIADOS CON EXITO
echo ==============================================================
pause
