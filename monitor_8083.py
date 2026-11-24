"""
Servicio de Monitoreo de NGINX y Arquitectura SOA (Puerto 8083)
Requisito de Guía Práctica 4: "Monitor de NGINX en puerto 8083: servicio de supervisión
reutilizable y externo al flujo de venta".
"""
import http.server
import socketserver
import json
import urllib.request
import time
from datetime import datetime

PORT = 8083

HTML_PAGE = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="5">
    <title>Monitor de Arquitectura SOA - Puerto 8083</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background: #0b132b; color: #e0e1dd; margin: 0; padding: 24px; }
        .container { max-width: 960px; margin: 0 auto; }
        header { display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #1c2541; padding-bottom: 18px; margin-bottom: 24px; }
        h1 { margin: 0; color: #48cae4; font-size: 22px; font-weight: 700; }
        p.subtitle { color: #8d99ae; margin: 6px 0 0 0; font-size: 13px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; margin-bottom: 24px; }
        .card { background: #1c2541; border-radius: 8px; padding: 18px; border: 1px solid #3a506b; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
        .card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
        .card-title { font-weight: 600; font-size: 15px; color: #ffffff; }
        .badge { font-size: 11px; font-weight: 700; padding: 4px 10px; border-radius: 4px; letter-spacing: 0.5px; }
        .badge-up { background: #065f46; color: #34d399; }
        .badge-down { background: #7f1d1d; color: #f87171; }
        .card-body { font-size: 13px; color: #cbd5e1; line-height: 1.6; }
        .metric { display: flex; justify-content: space-between; margin: 4px 0; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 2px; }
        .metric-label { color: #8d99ae; }
        .metric-val { font-weight: 600; color: #e0e1dd; }
        .footer { text-align: center; color: #64748b; font-size: 12px; margin-top: 30px; border-top: 1px solid #1c2541; padding-top: 15px; }
        .btn-refresh { background: #0077b6; color: white; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-weight: 600; font-size: 13px; text-decoration: none; }
        .btn-refresh:hover { background: #023e8a; }
        .summary-banner { background: #14213d; border-left: 4px solid #48cae4; padding: 14px 18px; border-radius: 4px; margin-bottom: 20px; font-size: 14px; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div>
                <h1>Monitor de Arquitectura SOA & NGINX (:8083)</h1>
                <p class="subtitle">Guía Práctica 4 · Supervisión de balanceo 3:1, tolerancia a fallos y microservicios</p>
            </div>
            <a href="/" class="btn-refresh">Actualizar Ahora</a>
        </header>

        <div class="summary-banner">
            <strong>Estado del Gateway NGINX:</strong> __NGINX_MSG__ &nbsp;|&nbsp; 
            <strong>Balanceo 3:1:</strong> Instancia A (75%) : Instancia B (25%) &nbsp;|&nbsp; 
            <strong>Última verificación:</strong> __TIMESTAMP__
        </div>

        <div class="grid">
            <!-- NGINX Gateway -->
            <div class="card">
                <div class="card-header">
                    <span class="card-title">NGINX Gateway (:8090)</span>
                    <span class="badge __NGINX_BADGE__">__NGINX_STATUS__</span>
                </div>
                <div class="card-body">
                    <div class="metric"><span class="metric-label">Healthcheck:</span><span class="metric-val">GET /nginx-ping</span></div>
                    <div class="metric"><span class="metric-label">Latencia:</span><span class="metric-val">__NGINX_LAT__ ms</span></div>
                    <div class="metric"><span class="metric-label">Política Upstream:</span><span class="metric-val">Round-Robin Ponderado (3:1)</span></div>
                    <div class="metric"><span class="metric-label">Failover:</span><span class="metric-val">proxy_next_upstream (1s timeout)</span></div>
                </div>
            </div>

            <!-- Spring Boot A -->
            <div class="card">
                <div class="card-header">
                    <span class="card-title">Spring Boot - Instancia A (:8080)</span>
                    <span class="badge __A_BADGE__">__A_STATUS__</span>
                </div>
                <div class="card-body">
                    <div class="metric"><span class="metric-label">Rol de Carga:</span><span class="metric-val">Principal (Peso = 3 / 75%)</span></div>
                    <div class="metric"><span class="metric-label">Latencia:</span><span class="metric-val">__A_LAT__ ms</span></div>
                    <div class="metric"><span class="metric-label">Servicio:</span><span class="metric-val">Catálogo Vehículos & Auth JWT</span></div>
                    <div class="metric"><span class="metric-label">Base de Datos:</span><span class="metric-val">MySQL (3306)</span></div>
                </div>
            </div>

            <!-- Spring Boot B -->
            <div class="card">
                <div class="card-header">
                    <span class="card-title">Spring Boot - Instancia B (:8082)</span>
                    <span class="badge __B_BADGE__">__B_STATUS__</span>
                </div>
                <div class="card-body">
                    <div class="metric"><span class="metric-label">Rol de Carga:</span><span class="metric-val">Secundario (Peso = 1 / 25%)</span></div>
                    <div class="metric"><span class="metric-label">Latencia:</span><span class="metric-val">__B_LAT__ ms</span></div>
                    <div class="metric"><span class="metric-label">Tolerancia Fallos:</span><span class="metric-val">Respaldo automático si A/B falla</span></div>
                    <div class="metric"><span class="metric-label">Base de Datos:</span><span class="metric-val">MySQL (3306)</span></div>
                </div>
            </div>

            <!-- FastAPI Ventas -->
            <div class="card">
                <div class="card-header">
                    <span class="card-title">FastAPI - Ventas & Compradores (:8000)</span>
                    <span class="badge __V_BADGE__">__V_STATUS__</span>
                </div>
                <div class="card-body">
                    <div class="metric"><span class="metric-label">Rutas:</span><span class="metric-val">/api/ventas, /api/compradores</span></div>
                    <div class="metric"><span class="metric-label">Latencia:</span><span class="metric-val">__V_LAT__ ms</span></div>
                    <div class="metric"><span class="metric-label">Idempotencia:</span><span class="metric-val">Clave SHA-256 + Idempotency-Key</span></div>
                    <div class="metric"><span class="metric-label">Mensajería:</span><span class="metric-val">Publicador RabbitMQ + Outbox</span></div>
                </div>
            </div>

            <!-- Notificaciones Java -->
            <div class="card">
                <div class="card-header">
                    <span class="card-title">Notificaciones Java (:8081)</span>
                    <span class="badge __N_BADGE__">__N_STATUS__</span>
                </div>
                <div class="card-body">
                    <div class="metric"><span class="metric-label">Endpoint:</span><span class="metric-val">GET /api/notificaciones</span></div>
                    <div class="metric"><span class="metric-label">Latencia:</span><span class="metric-val">__N_LAT__ ms</span></div>
                    <div class="metric"><span class="metric-label">Consumidor:</span><span class="metric-val">RabbitMQ (notificaciones.ventas)</span></div>
                    <div class="metric"><span class="metric-label">Consumo JavaFX:</span><span class="metric-val">Sondeo periódico cada 3s</span></div>
                </div>
            </div>

            <!-- RabbitMQ -->
            <div class="card">
                <div class="card-header">
                    <span class="card-title">RabbitMQ Broker (:15672)</span>
                    <span class="badge __RAB_BADGE__">__RAB_STATUS__</span>
                </div>
                <div class="card-body">
                    <div class="metric"><span class="metric-label">Cola Principal:</span><span class="metric-val">notificaciones.ventas</span></div>
                    <div class="metric"><span class="metric-label">Mensajes Listos (Ready):</span><span class="metric-val">__RAB_READY__</span></div>
                    <div class="metric"><span class="metric-label">Consumidores Activos:</span><span class="metric-val">__RAB_CONS__</span></div>
                    <div class="metric"><span class="metric-label">Durabilidad:</span><span class="metric-val">durable: true</span></div>
                </div>
            </div>
        </div>

        <div class="footer">
            Universidad Técnica de Ambato · Arquitectura SOA (Sexto Semestre) · Servicio Monitor Autónomo en Puerto 8083<br>
            Auto-recarga cada 5 segundos · Para API JSON: <a href="/api/status" style="color:#48cae4;">/api/status</a>
        </div>
    </div>
</body>
</html>
"""

def probe(url, headers=None, timeout=1.5):
    t0 = time.time()
    try:
        req = urllib.request.Request(url, headers=headers or {"User-Agent": "Monitor8083"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            lat = int((time.time() - t0) * 1000)
            return True, resp.status, lat
    except urllib.error.HTTPError as e:
        # 401/403 significa que el servicio responde
        lat = int((time.time() - t0) * 1000)
        return True, e.code, lat
    except Exception:
        return False, 0, 0

def check_rabbitmq():
    try:
        req = urllib.request.Request(
            "http://127.0.0.1:15672/api/queues/%2F/notificaciones.ventas",
            headers={"Authorization": "Basic Z3Vlc3Q6Z3Vlc3Q="}
        )
        with urllib.request.urlopen(req, timeout=1.5) as resp:
            data = json.loads(resp.read().decode())
            ready = data.get("messages_ready", 0)
            cons = data.get("consumers", 0)
            return True, ready, cons
    except Exception:
        return False, 0, 0

class MonitorHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Evitar saturar la consola

    def do_GET(self):
        # 1. Sondear servicios
        ng_ok, ng_code, ng_lat = probe("http://127.0.0.1:8090/nginx-ping")
        a_ok, a_code, a_lat = probe("http://127.0.0.1:8080/api/vehiculos")
        b_ok, b_code, b_lat = probe("http://127.0.0.1:8082/api/vehiculos")
        v_ok, v_code, v_lat = probe("http://127.0.0.1:8000/api/compradores")
        n_ok, n_code, n_lat = probe("http://127.0.0.1:8081/api/notificaciones")
        rab_ok, rab_ready, rab_cons = check_rabbitmq()

        # Endpoint JSON
        if self.path == "/api/status":
            data = {
                "timestamp": datetime.now().isoformat(),
                "nginx_8090": {"up": ng_ok, "status_code": ng_code, "latency_ms": ng_lat},
                "vehiculos_8080": {"up": a_ok, "status_code": a_code, "latency_ms": a_lat},
                "vehiculos_8082": {"up": b_ok, "status_code": b_code, "latency_ms": b_lat},
                "ventas_8000": {"up": v_ok, "status_code": v_code, "latency_ms": v_lat},
                "notificaciones_8081": {"up": n_ok, "status_code": n_code, "latency_ms": n_lat},
                "rabbitmq_15672": {"up": rab_ok, "messages_ready": rab_ready, "consumers": rab_cons}
            }
            body = json.dumps(data, indent=2).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        # Renderizar HTML con reemplazos seguros de variables
        html = HTML_PAGE
        replacements = {
            "__NGINX_STATUS__": "UP (200)" if ng_ok else "DOWN",
            "__NGINX_BADGE__": "badge-up" if ng_ok else "badge-down",
            "__NGINX_LAT__": str(ng_lat),
            "__NGINX_MSG__": "Operativo · 200 OK" if ng_ok else "Fallo de conexión",
            "__A_STATUS__": "UP" if a_ok else "DOWN",
            "__A_BADGE__": "badge-up" if a_ok else "badge-down",
            "__A_LAT__": str(a_lat),
            "__B_STATUS__": "UP" if b_ok else "DOWN",
            "__B_BADGE__": "badge-up" if b_ok else "badge-down",
            "__B_LAT__": str(b_lat),
            "__V_STATUS__": "UP" if v_ok else "DOWN",
            "__V_BADGE__": "badge-up" if v_ok else "badge-down",
            "__V_LAT__": str(v_lat),
            "__N_STATUS__": "UP" if n_ok else "DOWN",
            "__N_BADGE__": "badge-up" if n_ok else "badge-down",
            "__N_LAT__": str(n_lat),
            "__RAB_STATUS__": "UP" if rab_ok else "DOWN",
            "__RAB_BADGE__": "badge-up" if rab_ok else "badge-down",
            "__RAB_READY__": str(rab_ready),
            "__RAB_CONS__": str(rab_cons),
            "__TIMESTAMP__": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        for placeholder, value in replacements.items():
            html = html.replace(placeholder, value)

        body = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

def run():
    with ReusableTCPServer(("127.0.0.1", PORT), MonitorHandler) as httpd:
        print(f"Servicio Monitor de Supervisión iniciado en http://127.0.0.1:{PORT}")
        httpd.serve_forever()

if __name__ == "__main__":
    run()
