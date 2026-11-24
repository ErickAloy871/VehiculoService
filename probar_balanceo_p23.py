import httpx
import json

# 1. Obtener token
r_tok = httpx.post(
    'http://127.0.0.1:8090/oauth/token',
    auth=('vehiculos-client', 'cliente-local-aula-2026-cambiar'),
    data={'grant_type': 'password', 'username': 'operador', 'password': 'operador123'},
    timeout=6
)
tok = r_tok.json()['access_token']

log_path = r'C:\nginx\logs\access.log'
with open(log_path, 'r', encoding='utf-8') as f:
    f.seek(0, 2)
    start_pos = f.tell()

print('Enviando 100 peticiones GET /api/vehiculos a NGINX (:8090)...')
client = httpx.Client(headers={'Authorization': f'Bearer {tok}', 'Connection': 'close'}, timeout=8)
success = 0
for i in range(100):
    r = client.get('http://127.0.0.1:8090/api/vehiculos')
    if r.status_code == 200:
        success += 1

print(f'Peticiones completadas: {success}/100 exitosas (HTTP 200)\n')

conteos = {'127.0.0.1:8080': 0, '127.0.0.1:8082': 0, 'otros': 0}
with open(log_path, 'r', encoding='utf-8') as f:
    f.seek(start_pos)
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
            if entry.get('uri') == '/api/vehiculos' and entry.get('status') == '200':
                addr = str(entry.get('upstream_addr', ''))
                if '8080' in addr:
                    conteos['127.0.0.1:8080'] += 1
                elif '8082' in addr:
                    conteos['127.0.0.1:8082'] += 1
                else:
                    conteos['otros'] += 1
        except Exception:
            pass

total_veh = conteos['127.0.0.1:8080'] + conteos['127.0.0.1:8082']
pct_a = (conteos['127.0.0.1:8080'] / total_veh * 100) if total_veh else 0
pct_b = (conteos['127.0.0.1:8082'] / total_veh * 100) if total_veh else 0

print('======================================================================')
print('EVIDENCIA P23: BALANCEO PONDERADO 3:1 CON 100 SOLICITUDES GET')
print('======================================================================')
print(f'Instancia A (:8080) [Peso 3] -> {conteos["127.0.0.1:8080"]} peticiones ({pct_a:.1f}%)')
print(f'Instancia B (:8082) [Peso 1] -> {conteos["127.0.0.1:8082"]} peticiones ({pct_b:.1f}%)')
print(f'Total de solicitudes balanceadas: {total_veh}')
if pct_b > 0:
    print(f'Proporcion real observada en logs: {pct_a/pct_b:.2f} : 1  (Esperado aproximado: 3.0 : 1)')
print('======================================================================')
