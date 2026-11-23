import { login, listarVehiculos, listarCompradores, registrarVenta, consultarVenta } from './api.js';

// Estado de sesión en memoria volátil (nunca persistido en disco)
let tokenEnMemoria = null;
let usuarioEnMemoria = null;

// Elementos del DOM
const formLogin = document.querySelector('#form-login');
const inputUsuario = document.querySelector('#login-usuario');
const inputPassword = document.querySelector('#login-password');
const btnLogin = document.querySelector('#btn-login');
const btnLogout = document.querySelector('#btn-logout');
const mensajeLogin = document.querySelector('#mensaje-login');
const badgeSesion = document.querySelector('#badge-sesion');
const labelUsuarioSesion = document.querySelector('#usuario-sesion');

const btnRecargarDatos = document.querySelector('#btn-recargar-datos');
const contadorVehiculos = document.querySelector('#contador-vehiculos');
const contadorCompradores = document.querySelector('#contador-compradores');
const listaVehiculosDisp = document.querySelector('#lista-vehiculos-disponibles');

const formVenta = document.querySelector('#form-venta');
const selectVehiculo = document.querySelector('#select-vehiculo');
const selectComprador = document.querySelector('#select-comprador');
const inputIdempotency = document.querySelector('#input-idempotency');
const btnGenerarUuid = document.querySelector('#btn-generar-uuid');
const resultadoVenta = document.querySelector('#resultado-venta');
const ventaHttpBadge = document.querySelector('#venta-http-badge');
const ventaEstadoBadge = document.querySelector('#venta-estado-badge');
const ventaDetalle = document.querySelector('#venta-detalle');

const inputVentaId = document.querySelector('#input-venta-id');
const btnConsultarVenta = document.querySelector('#btn-consultar-venta');
const resultadoConsultaVenta = document.querySelector('#resultado-consulta-venta');
const consultaVentaDetalle = document.querySelector('#consulta-venta-detalle');
const conexion = document.querySelector('#conexion');

// Formato de moneda
const moneda = new Intl.NumberFormat('es-EC', { style: 'currency', currency: 'USD' });

function setMensajeLogin(texto, tipo = 'neutro') {
  mensajeLogin.textContent = texto;
  mensajeLogin.className = `mensaje ${tipo}`;
}

function generarUuid() {
  const uuid = crypto.randomUUID();
  inputIdempotency.value = uuid;
  return uuid;
}

// Inicializar UUID para idempotencia
generarUuid();
btnGenerarUuid.addEventListener('click', () => generarUuid());

// 1. GESTIÓN DE SESIÓN Y LOGIN
formLogin.addEventListener('submit', async (e) => {
  e.preventDefault();
  const u = inputUsuario.value.trim();
  const p = inputPassword.value;

  if (!u || !p) {
    setMensajeLogin('Ingrese usuario y contraseña.', 'error');
    return;
  }

  btnLogin.disabled = true;
  setMensajeLogin('Autenticando con /oauth/token…', 'neutro');

  try {
    const res = await login(u, p);
    tokenEnMemoria = res.accessToken;
    usuarioEnMemoria = res.usuario;

    setMensajeLogin(`HTTP ${res.status}: Sesión iniciada con éxito. Token emitido.`, 'exito');
    badgeSesion.style.display = 'block';
    labelUsuarioSesion.textContent = usuarioEnMemoria;
    btnLogin.style.display = 'none';
    btnLogout.style.display = 'inline-block';

    // Cargar datos automáticamente tras login
    await cargarDatos();
  } catch (error) {
    tokenEnMemoria = null;
    usuarioEnMemoria = null;
    setMensajeLogin(error.message, 'error');
    badgeSesion.style.display = 'none';
  } finally {
    btnLogin.disabled = false;
  }
});

btnLogout.addEventListener('click', () => {
  tokenEnMemoria = null;
  usuarioEnMemoria = null;
  badgeSesion.style.display = 'none';
  btnLogin.style.display = 'inline-block';
  btnLogout.style.display = 'none';
  setMensajeLogin('Sesión cerrada. Token eliminado de la memoria.', 'neutro');

  // Limpiar listas
  selectVehiculo.innerHTML = '<option value="">Inicie sesión para cargar vehículos...</option>';
  selectComprador.innerHTML = '<option value="">Inicie sesión para cargar compradores...</option>';
  contadorVehiculos.textContent = '0 vehículos disponibles';
  contadorCompradores.textContent = '0 compradores';
  listaVehiculosDisp.innerHTML = '';
});

// 2. CARGA DE CATÁLOGO Y COMPRADORES
async function cargarDatos() {
  if (!tokenEnMemoria) {
    setMensajeLogin('Se requiere iniciar sesión antes de cargar datos.', 'error');
    return;
  }

  btnRecargarDatos.disabled = true;
  btnRecargarDatos.textContent = 'Cargando…';

  try {
    const [resVeh, resComp] = await Promise.all([
      listarVehiculos(tokenEnMemoria).catch((err) => ({ status: err.status || 500, vehiculos: [] })),
      listarCompradores(tokenEnMemoria).catch((err) => ({ status: err.status || 500, compradores: [] }))
    ]);

    // Filtrar solo vehículos disponibles para venta
    const disponibles = resVeh.vehiculos.filter(v => String(v.estado).toUpperCase() === 'DISPONIBLE');
    contadorVehiculos.textContent = `${disponibles.length} disponibles (de ${resVeh.vehiculos.length})`;
    contadorCompradores.textContent = `${resComp.compradores.length} compradores`;

    // Llenar selectores
    selectVehiculo.innerHTML = '<option value="">-- Seleccione un vehículo disponible --</option>';
    disponibles.forEach(v => {
      const opt = document.createElement('option');
      opt.value = v.idVehiculo ?? v.id;
      opt.textContent = `ID #${v.idVehiculo ?? v.id} - ${v.marca} ${v.modelo} (${v.color}) - ${moneda.format(v.precio || 0)}`;
      selectVehiculo.appendChild(opt);
    });

    selectComprador.innerHTML = '<option value="">-- Seleccione un comprador --</option>';
    resComp.compradores.forEach(c => {
      const opt = document.createElement('option');
      opt.value = c.id;
      opt.textContent = `ID #${c.id} - ${c.nombre} (Doc: ${c.documento})`;
      selectComprador.appendChild(opt);
    });

    // Renderizar tarjetas compactas
    listaVehiculosDisp.innerHTML = '';
    disponibles.slice(0, 4).forEach(v => {
      const card = document.createElement('div');
      card.className = 'card-mini';
      card.innerHTML = `<strong>#${v.idVehiculo ?? v.id} ${v.marca} ${v.modelo}</strong><span>${moneda.format(v.precio || 0)}</span>`;
      card.addEventListener('click', () => {
        selectVehiculo.value = v.idVehiculo ?? v.id;
      });
      listaVehiculosDisp.appendChild(card);
    });

  } finally {
    btnRecargarDatos.disabled = false;
    btnRecargarDatos.textContent = 'Recargar';
  }
}

btnRecargarDatos.addEventListener('click', cargarDatos);

// 3. REGISTRO EXCLUSIVO DE VENTAS (POST /api/ventas)
formVenta.addEventListener('submit', async (e) => {
  e.preventDefault();

  if (!tokenEnMemoria) {
    alert('Debe iniciar sesión primero en el Paso 01.');
    return;
  }

  const vId = selectVehiculo.value;
  const cId = selectComprador.value;
  const key = inputIdempotency.value.trim() || generarUuid();

  if (!vId || !cId) {
    alert('Seleccione un vehículo y un comprador para realizar la venta.');
    return;
  }

  const btnVenta = document.querySelector('#btn-registrar-venta');
  btnVenta.disabled = true;
  btnVenta.textContent = 'Procesando venta con NGINX…';
  resultadoVenta.style.display = 'none';

  try {
    const res = await registrarVenta(tokenEnMemoria, vId, cId, key);

    resultadoVenta.style.display = 'block';
    ventaHttpBadge.textContent = `HTTP ${res.status}`;
    ventaHttpBadge.className = `http-badge http-${res.status}`;

    const estado = res.data?.estado || (res.status === 201 ? 'COMPLETADA' : res.status === 202 ? 'EN_REVISION' : 'RECHAZADA');
    ventaEstadoBadge.textContent = estado;
    ventaEstadoBadge.className = `estado-badge estado-${estado.toLowerCase()}`;

    ventaDetalle.textContent = JSON.stringify({
      httpStatus: res.status,
      idempotencyKeyEnviada: res.idempotencyKey,
      respuestaServicio: res.data
    }, null, 2);

    // Si la venta fue exitosa, actualizar ID para consulta y refrescar catálogo
    if (res.status === 201 || res.status === 202) {
      if (res.data?.id) inputVentaId.value = res.data.id;
      await cargarDatos();
    }
  } catch (err) {
    resultadoVenta.style.display = 'block';
    ventaHttpBadge.textContent = 'ERROR';
    ventaHttpBadge.className = 'http-badge http-500';
    ventaDetalle.textContent = String(err.message);
  } finally {
    btnVenta.disabled = false;
    btnVenta.textContent = 'Completar Venta';
  }
});

// 4. CONSULTA INDIVIDUAL DE VENTA (GET /api/ventas/{id})
btnConsultarVenta.addEventListener('click', async () => {
  if (!tokenEnMemoria) {
    alert('Debe iniciar sesión primero para consultar ventas.');
    return;
  }
  const vId = inputVentaId.value.trim();
  if (!vId) {
    alert('Ingrese un ID de venta.');
    return;
  }

  btnConsultarVenta.disabled = true;
  try {
    const res = await consultarVenta(tokenEnMemoria, vId);
    resultadoConsultaVenta.style.display = 'block';
    consultaVentaDetalle.textContent = JSON.stringify(res.venta, null, 2);
  } catch (err) {
    resultadoConsultaVenta.style.display = 'block';
    consultaVentaDetalle.textContent = `Error: ${err.message}`;
  } finally {
    btnConsultarVenta.disabled = false;
  }
});

// Estado de conexión a red
function actualizarConexion() {
  conexion.textContent = navigator.onLine ? 'Navegador en línea' : 'Sin conexión de red';
}
window.addEventListener('online', actualizarConexion);
window.addEventListener('offline', actualizarConexion);
actualizarConexion();

// Registro del Service Worker
if ('serviceWorker' in navigator && window.isSecureContext) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js').catch(() => {});
  });
}
