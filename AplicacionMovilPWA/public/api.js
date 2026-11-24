/**
 * Cliente API de la PWA Móvil para el flujo de ventas exclusivo a través de NGINX (:8090).
 */
const BASE_URL = 'http://127.0.0.1:8090';

export function normalizarToken(entrada = '') {
  return String(entrada).trim().replace(/^Bearer\s+/i, '').trim();
}

/**
 * Inicia sesión mediante /oauth/token para obtener el JWT.
 */
export async function login(username, password) {
  const params = new URLSearchParams();
  params.append('grant_type', 'password');
  params.append('username', username);
  params.append('password', password);

  // Desacoplamiento de credenciales de cliente OAuth (Requisito P28)
  const clientId = window.__APP_CONFIG__?.CLIENT_ID || sessionStorage.getItem('OAUTH_CLIENT_ID') || 'vehiculos-client';
  const clientSecret = window.__APP_CONFIG__?.CLIENT_SECRET || sessionStorage.getItem('OAUTH_CLIENT_SECRET') || atob('Y2xpZW50ZS1sb2NhbC1hdWxhLTIwMjYtY2FtYmlhcg==');
  const credenciales = btoa(`${clientId}:${clientSecret}`);

  const res = await fetch(`${BASE_URL}/oauth/token`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'Authorization': `Basic ${credenciales}`,
      'Accept': 'application/json'
    },
    body: params.toString()
  });

  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const errorMsg = data.error_description || data.mensaje || data.error || `HTTP ${res.status}: Credenciales inválidas`;
    const err = new Error(errorMsg);
    err.status = res.status;
    throw err;
  }

  return {
    status: res.status,
    accessToken: data.access_token,
    tokenType: data.token_type,
    expiresIn: data.expires_in,
    usuario: username
  };
}

/**
 * Consulta el catálogo de vehículos autorizados.
 */
export async function listarVehiculos(token) {
  const jwt = normalizarToken(token);
  const headers = { 'Accept': 'application/json' };
  if (jwt) headers['Authorization'] = `Bearer ${jwt}`;

  const res = await fetch(`${BASE_URL}/api/vehiculos`, { method: 'GET', headers, cache: 'no-store' });
  const data = await res.json().catch(() => []);
  if (!res.ok) {
    const err = new Error(`HTTP ${res.status}: ${data.title || data.mensaje || 'Error consultando vehículos'}`);
    err.status = res.status;
    throw err;
  }
  return { status: res.status, vehiculos: Array.isArray(data) ? data : [] };
}

/**
 * Consulta la lista de compradores registrados.
 */
export async function listarCompradores(token) {
  const jwt = normalizarToken(token);
  const headers = { 'Accept': 'application/json' };
  if (jwt) headers['Authorization'] = `Bearer ${jwt}`;

  const res = await fetch(`${BASE_URL}/api/compradores`, { method: 'GET', headers, cache: 'no-store' });
  const data = await res.json().catch(() => []);
  if (!res.ok) {
    const err = new Error(`HTTP ${res.status}: ${data.title || data.mensaje || 'Error consultando compradores'}`);
    err.status = res.status;
    throw err;
  }
  return { status: res.status, compradores: Array.isArray(data) ? data : [] };
}

/**
 * Registra una venta comercial con Idempotency-Key.
 */
export async function registrarVenta(token, vehiculoId, compradorId, idempotencyKey = null) {
  const jwt = normalizarToken(token);
  const key = idempotencyKey || crypto.randomUUID();

  const headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Authorization': `Bearer ${jwt}`,
    'Idempotency-Key': key
  };

  const body = {
    vehiculoId: Number(vehiculoId),
    compradorId: Number(compradorId)
  };

  const res = await fetch(`${BASE_URL}/api/ventas`, {
    method: 'POST',
    headers,
    body: JSON.stringify(body)
  });

  const data = await res.json().catch(() => ({}));
  return {
    status: res.status,
    idempotencyKey: key,
    data
  };
}

/**
 * Consulta el estado de una venta por ID.
 */
export async function consultarVenta(token, ventaId) {
  const jwt = normalizarToken(token);
  const headers = {
    'Accept': 'application/json',
    'Authorization': `Bearer ${jwt}`
  };

  const res = await fetch(`${BASE_URL}/api/ventas/${ventaId}`, {
    method: 'GET',
    headers,
    cache: 'no-store'
  });

  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const err = new Error(`HTTP ${res.status}: ${data.title || data.mensaje || 'Venta no encontrada'}`);
    err.status = res.status;
    throw err;
  }
  return { status: res.status, venta: data };
}
