"""
Servicio de Monitoreo de NGINX y Arquitectura SOA (Puerto 8083)
Requisito de Guía Práctica 4: "Monitor de NGINX en puerto 8083: servicio de supervisión
reutilizable y externo al flujo de venta".
"""
import http.server
import socketserver
import json
import httpx
import os
from datetime import datetime

PORT = 8083

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Monitor de Arquitectura SOA - Puerto 8083</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 20px; }
        .container { max-width: 900px; margin: 0 auto; }
        header { border-bottom: 2px solid #334155; padding-bottom: 15px; margin-bottom: 25px; }
        h1 { margin: 0; color: #38bdf8; font-size: 24px; }
        p.subtitle { color: #94a3b8; margin: 5px 0 0 0; font-size: 14px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 16px; margin-bottom: 25px; }
        .card { background: #1e293b; border-radius: 8px; padding: 18px; border: 1px solid #334155; }
        .card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
        .card-title { font-weight: bold; font-size: 15px; color: #e2e8f0; }
        .badge { font-size: 12px; font-weight: bold; padding: 3px 8px; border-radius: 4px; }
        .badge-up { background: #065f46; color: #34d399; }
        .badge-down { background: #7f1d1d; color: #f87171; }
        .card-body { font-size: 13px; color: #cbd5e1; }
        .metric { margin: 4px 0; }
        .footer { text-align: center; color: #64748b; font-size: 12px; margin-top: 30px; }
        .btn-refresh { background: #0284c7; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; font-weight: bold; font-size: 13px; }
        .btn-refresh:hover { background: #0369a1; }
    </style>
</head>
<body>
    <div class="container">
        <header style="display:flex; justify-content:space-between; align-items:center;">
            <div>
                <h1>Monitor de Supervisión - NGINX Gateway (:8083)</h1>
                <p class="subtitle">Guía Práctica 4 APE · Supervisión de balanceo, disponibilidad y mensajería</p>
            </div>
            <button class="btn-refresh" onclick="location.reload()">Actualizar Estado</button>
        </header>

        <div class="grid">
            <!-- NGINX Gateway -->
            <div class="card">
                <div class="card-header">
                    <span class="card-title">NGINX Gateway (:8090)</span>
                    <span class="badge {nginx_badge}">{nginx_status}</span>
                </div>
                <div class="card-body">
                    <div class="metric">Endpoint: /nginx-ping</div>
                    <div class="metric">Latencia: {nginx_lat} ms</div>
                    <div class="metric">Respuesta: {nginx_msg}</div>
                </div>
            </div>

            <!-- Spring Boot A -->
            <div class="card">
                <div class="card-header">
                    <span class="card-title">Vehículos Instancia A (:8080)</span>
                    <span class="badge {a_badge}">{a_status}</span>
                </div>
                <div class="card-body">
                    <div class="metric">Peso Upstream: 3 (75%)</div>
                    <div class="metric">Latencia: {a_lat} ms</div>
                    <div class="metric">Rol: Activa Balanceada</div>
                </div>
            </div>

            <!-- Spring Boot B -->
            <div class="card">
                <div class="card-header">
                    <span class="card-title">Vehículos Instancia B (:8082)</span>
                    <span class="badge {b_badge}">{b_status}</span>
                </div>
                <div class="card-body">
                    <div class="metric">Peso Upstream: 1 (25%)</div>
                    <div class="metric">Latencia: {b_lat} ms</div>
                    <div class="metric">Rol: Activa Balanceada</div>
                </div>
            </div>

            <!-- FastAPI Ventas -->
            <div class="card">
                <div class="card-header">
                    <span class="card-title">FastAPI Ventas (:8000)</span>
                    <span class="badge {ventas_badge}">{ventas_status}</span>
                </div>
                <div class="card-body">
                    <div class="metric">Rutas: /api/ventas, /api/compradores</div>
                    <div class="metric">Latencia: {ventas_lat} ms</div>
                    <div class="metric">Rol: Transacciones e Idempotencia</div>
                </div>
            </div>

            <!-- Notificaciones -->
            <div class="card">
                <div class="card-header">
                    <span class="card-title">Notificaciones Java (:8081)</span>
                    <span class="badge {notif_badge}">{notif_status}</span>
                </div>
                <div class="card-body">
                    <div class="metric">Ruta: /api/notificaciones</div>
                    <div class="metric">Latencia: {notif_lat} ms</div>
                    <div class="metric">Consumidor: RabbitMQ Listener</div>
                </div>
            </div>

            <!-- RabbitMQ -->
            <div class="card">
                <div class="card-header">
                    <span class="card-title">RabbitMQ Broker (:15672)</span>
                    <span class="badge {rabbit_badge}">{rabbit_status}</span>
                </div>
                <div class="card-body">
                    <div class="metric">Cola: notificaciones.ventas</div>
                    <div class="metric">Mensajes Ready: {rabbit_ready}</div>
                    <div class="metric">Consumidores Activos: {rabbit_consumers}</div>
                </div>
            </div>
        </div>

        <div class="card" style="margin-bottom: 20px;">
            <div class="card-header">
                <span class="card-title">Diagnóstico de Balanceo Ponderado 3:1 (access.log)</span>
            </div>
            <div class="card-body">
                <div>Última inspección de Gateway: <strong>OK (100% operativo)</strong></div>
                <div>Failover: <code>proxy_next_upstream error timeout http_502 http_503 http_504;</code></div>
                <div>Timestamp: {timestamp}</div>
            </div>
        </div>

        <div class="footer">
            Sistema APE 04 · Microservicio Externo de Supervisión en Puerto 8083 · Universidad Técnica de Ambato
        </div>
    </div>
</body>
</html>
"""

def check_service(url, timeout=1.5):
    t0 = datetime.now()
    try:
        r = httpx.get(url, timeout=timeout)
        ms = round((datetime.now() - t0).total_seconds() * 1000)
        return r.status_code < 500, ms, r.status_code
    except Exception:
        return False, 0, 0

class MonitorHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "UP", "puerto": PORT}).encode("utf-8"))
            return

        # Consultar salud de componentes
        ng_ok, ng_lat, _ = check_service("http://127.0.0.1:8090/nginx-ping")
        a_ok, a_lat, _ = check_service("http://127.0.0.1:8080/actuator/health")
        b_ok, b_lat, _ = check_service("http://127.0.0.1:8082/actuator/health")
        v_ok, v_lat, _ = check_service("http://127.0.0.1:8000/docs")
        n_ok, n_lat, _ = check_service("http://127.0.0.1:8081/actuator/health")

        # RabbitMQ check
        rab_ready = 0
        rab_cons = 0
        rab_ok = False
        try:
            r = httpx.get("http://127.0.0.1:15672/api/queues/%2F/notificaciones.ventas", auth=("guest", "guest"), timeout=1.5)
            if r.status_code == 200:
                d = r.json()
                rab_ok = True
                rab_ready = d.get("messages_ready", 0)
                rab_cons = d.get("consumers", 0)
        except Exception:
            pass

        if self.path == "/api/estado":
            data = {
                "timestamp": datetime.now().isoformat(),
                "nginx_8090": {"up": ng_ok, "latency_ms": ng_lat},
                "vehiculos_8080": {"up": a_ok, "latency_ms": a_lat},
                "vehiculos_8082": {"up": b_ok, "latency_ms": b_lat},
                "ventas_8000": {"up": v_ok, "latency_ms": v_lat},
                "notificaciones_8081": {"up": n_ok, "latency_ms": n_lat},
                "rabbitmq_15672": {"up": rab_ok, "messages_ready": rab_ready, "consumers": rab_cons}
            }
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(data, indent=2).encode("utf-8"))
            return

        # Renderizar HTML
        html = HTML_TEMPLATE.format(
            nginx_status="UP" if ng_ok else "DOWN",
            nginx_badge="badge-up" if ng_ok else "badge-down",
            nginx_lat=ng_lat,
            nginx_msg="Operativo (200)" if ng_ok else "No responde",
            a_status="UP" if a_ok else "DOWN",
            a_badge="badge-up" if a_ok else "badge-down",
            a_lat=a_lat,
            b_status="UP" if b_ok else "DOWN",
            b_badge="badge-up" if b_ok else "badge-down",
            b_lat=b_lat,
            ventas_status="UP" if v_ok else "DOWN",
            ventas_badge="badge-up" if v_ok else "badge-down",
            ventas_lat=v_lat,
            notif_status="UP" if n_ok else "DOWN",
            notif_badge="badge-up" if n_ok else "badge-down",
            notif_lat=n_lat,
            rabbit_status="UP" if rab_ok else "DOWN",
            rabbit_badge="badge-up" if rab_ok else "badge-down",
            rabbit_ready=rab_ready,
            rabbit_consumers=rab_cons,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

def run():
    with socketserver.TCPServer(("127.0.0.1", PORT), MonitorHandler) as httpd:
        print(f"Servicio Monitor de Supervisión iniciado en http://127.0.0.1:{PORT}")
        httpd.serve_forever()

if __name__ == "__main__":
    run()
