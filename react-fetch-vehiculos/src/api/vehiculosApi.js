/**
 * Cliente HTTP para la API de vehículos y consulta de ventas vía NGINX (:8090).
 */
export async function listarVehiculos(token) {
  const headers = new Headers({ Accept: 'application/json' });

  if (token && token.trim()) {
    headers.set('Authorization', `Bearer ${token.trim()}`);
  }

  let respuesta;
  try {
    respuesta = await fetch('/api/vehiculos', {
      method: 'GET',
      headers,
      cache: 'no-store',
    });
  } catch {
    throw new Error('No se pudo conectar con el Gateway NGINX (:8090).');
  }

  if (!respuesta.ok) {
    const error = new Error(`HTTP ${respuesta.status}: Fallo al consultar vehículos.`);
    error.status = respuesta.status;
    throw error;
  }

  if (respuesta.status === 204) {
    return { vehiculos: [], codigoHttp: 204 };
  }

  let datos;
  try {
    datos = await respuesta.json();
  } catch {
    throw new Error('La API respondió, pero el JSON no pudo interpretarse.');
  }

  if (!Array.isArray(datos)) {
    throw new Error('Se esperaba una lista JSON de vehículos.');
  }

  return { vehiculos: datos, codigoHttp: respuesta.status };
}

/**
 * Consulta el listado de ventas confirmadas desde GET /api/ventas.
 * No implementa métodos POST de venta (exclusivo de PWA).
 */
export async function listarVentas(token) {
  const headers = new Headers({ Accept: 'application/json' });

  if (token && token.trim()) {
    headers.set('Authorization', `Bearer ${token.trim()}`);
  }

  let respuesta;
  try {
    respuesta = await fetch('/api/ventas', {
      method: 'GET',
      headers,
      cache: 'no-store',
    });
  } catch {
    throw new Error('No se pudo conectar con el servicio de ventas (:8000 vía NGINX).');
  }

  if (!respuesta.ok) {
    const error = new Error(`HTTP ${respuesta.status}: Error al consultar ventas.`);
    error.status = respuesta.status;
    throw error;
  }

  let datos;
  try {
    datos = await respuesta.json();
  } catch {
    throw new Error('La respuesta de ventas no es un JSON válido.');
  }

  const items = Array.isArray(datos) ? datos : (Array.isArray(datos.items) ? datos.items : []);
  return {
    ventas: items,
    codigoHttp: respuesta.status,
    total: datos.total ?? items.length
  };
}
