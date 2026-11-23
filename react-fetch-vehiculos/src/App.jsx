import { useState } from 'react';
import { listarVehiculos, listarVentas } from './api/vehiculosApi.js';
import './App.css';

const dinero = new Intl.NumberFormat('es-EC', {
  style: 'currency',
  currency: 'USD',
});

function mostrarPrecio(precio) {
  if (precio === null || precio === undefined || precio === '') return '—';
  const numero = Number(precio);
  return Number.isFinite(numero) ? dinero.format(numero) : String(precio);
}

export default function App() {
  const [token, setToken] = useState('');
  const [mostrarToken, setMostrarToken] = useState(false);
  const [pestaña, setPestaña] = useState('vehiculos'); // 'vehiculos' | 'ventas'

  // Estado de vehículos
  const [vehiculos, setVehiculos] = useState([]);
  const [marca, setMarca] = useState('');
  const [seleccionado, setSeleccionado] = useState(null);

  // Estado de ventas
  const [ventas, setVentas] = useState([]);

  // Estado común
  const [cargando, setCargando] = useState(false);
  const [mensaje, setMensaje] = useState('Listo para consultar.');
  const [error, setError] = useState('');
  const [codigoHttp, setCodigoHttp] = useState(null);

  const visibles = vehiculos.filter((v) =>
    String(v.marca ?? '').toLowerCase().includes(marca.trim().toLowerCase()),
  );

  // Consulta de vehículos (GET /api/vehiculos)
  async function consultarCatalogo(evento) {
    if (evento) evento.preventDefault();
    setCargando(true);
    setError('');
    setMensaje('Consultando catálogo vía NGINX (:8090)...');
    setCodigoHttp(null);
    setSeleccionado(null);

    try {
      const resultado = await listarVehiculos(token);
      setVehiculos(resultado.vehiculos);
      setCodigoHttp(resultado.codigoHttp);
      setMensaje(`Consulta correcta: ${resultado.vehiculos.length} vehículos recibidos.`);
    } catch (e) {
      setVehiculos([]);
      setCodigoHttp(e.status ?? null);
      setError(e.message);
      setMensaje('La consulta de vehículos no pudo completarse.');
    } finally {
      setCargando(false);
    }
  }

  // Consulta de ventas (GET /api/ventas)
  async function consultarListadoVentas(evento) {
    if (evento) evento.preventDefault();
    setCargando(true);
    setError('');
    setMensaje('Consultando ventas vía NGINX (:8090)...');
    setCodigoHttp(null);

    try {
      const resultado = await listarVentas(token);
      setVentas(resultado.ventas);
      setCodigoHttp(resultado.codigoHttp);
      setMensaje(`Consulta correcta: ${resultado.ventas.length} ventas registradas.`);
    } catch (e) {
      setVentas([]);
      setCodigoHttp(e.status ?? null);
      setError(e.message);
      setMensaje('La consulta de ventas no pudo completarse.');
    } finally {
      setCargando(false);
    }
  }

  return (
    <main className="contenedor">
      <header className="cabecera">
        <div className="marca-producto">PRÁCTICA WEB · REACT + VITE + FETCH</div>
        <h1>Portal de Consulta Comercial</h1>
        <p>Cliente de consulta de vehículos y ventas conectado a NGINX (:8090). <em>(No registra ventas)</em></p>
      </header>

      {/* Pestañas de Navegación */}
      <nav style={{ display: 'flex', gap: '8px', marginBottom: '16px' }}>
        <button
          type="button"
          onClick={() => setPestaña('vehiculos')}
          style={{
            background: pestaña === 'vehiculos' ? '#10597b' : '#e2edf3',
            color: pestaña === 'vehiculos' ? '#fff' : '#22516b',
            border: 'none', padding: '10px 18px', borderRadius: '8px', fontWeight: 'bold'
          }}
        >
          🚗 Catálogo de Vehículos
        </button>
        <button
          type="button"
          onClick={() => { setPestaña('ventas'); if (ventas.length === 0) consultarListadoVentas(); }}
          style={{
            background: pestaña === 'ventas' ? '#10597b' : '#e2edf3',
            color: pestaña === 'ventas' ? '#fff' : '#22516b',
            border: 'none', padding: '10px 18px', borderRadius: '8px', fontWeight: 'bold'
          }}
        >
          📋 Historial de Ventas
        </button>
      </nav>

      {/* Panel de Autenticación */}
      <section className="panel" aria-labelledby="titulo-acceso">
        <h2 id="titulo-acceso">Autenticación JWT</h2>
        <p className="ayuda">
          Las consultas protegidas envían la cabecera <code>Authorization: Bearer &lt;JWT&gt;</code> a través de NGINX en el puerto <strong>8090</strong>.
        </p>

        <form onSubmit={pestaña === 'vehiculos' ? consultarCatalogo : consultarListadoVentas}>
          <label htmlFor="jwt">Token JWT</label>
          <div className="linea-token">
            <input
              id="jwt"
              type={mostrarToken ? 'text' : 'password'}
              autoComplete="off"
              spellCheck="false"
              placeholder="Pegar token JWT (obtenido de PWA o Postman)"
              value={token}
              onChange={(e) => setToken(e.target.value)}
            />
            <button
              className="secundario"
              type="button"
              onClick={() => setMostrarToken((actual) => !actual)}
            >
              {mostrarToken ? 'Ocultar' : 'Mostrar'}
            </button>
          </div>

          <div className="acciones">
            <button type="submit" disabled={cargando}>
              {cargando ? 'Consultando...' : pestaña === 'vehiculos' ? 'Consultar Catálogo' : 'Consultar Ventas'}
            </button>
            <button
              className="secundario"
              type="button"
              disabled={cargando}
              onClick={() => { setToken(''); setMostrarToken(false); }}
            >
              Limpiar token
            </button>
          </div>
        </form>

        <div className={error ? 'estado estado-error' : 'estado estado-ok'} role="status" aria-live="polite">
          <span>{error || mensaje}</span>
          {codigoHttp !== null && <strong>HTTP {codigoHttp}</strong>}
        </div>
      </section>

      {/* VISTA 1: CATÁLOGO DE VEHÍCULOS */}
      {pestaña === 'vehiculos' && (
        <section className="panel" aria-labelledby="titulo-catalogo">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '8px' }}>
            <h2 id="titulo-catalogo">Catálogo de Vehículos</h2>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <input
                type="text"
                placeholder="Filtrar por marca (ej. Chevrolet)..."
                value={marca}
                onChange={(e) => setMarca(e.target.value)}
                style={{ padding: '6px 12px', borderRadius: '6px', border: '1px solid #ccc' }}
              />
              <span className="contador-items">{visibles.length} vehículos</span>
            </div>
          </div>

          {visibles.length === 0 ? (
            <p className="vacio" style={{ padding: '30px', textAlign: 'center', color: '#888' }}>
              No hay vehículos para mostrar. Ingrese un token y pulse &quot;Consultar Catálogo&quot;.
            </p>
          ) : (
            <div className="grilla-vehiculos" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))', gap: '12px', marginTop: '14px' }}>
              {visibles.map((v) => (
                <div
                  key={v.idVehiculo ?? v.id}
                  onClick={() => setSeleccionado(v)}
                  style={{
                    border: seleccionado?.idVehiculo === (v.idVehiculo ?? v.id) ? '2px solid #10597b' : '1px solid #d5e0e6',
                    background: '#fcfdfe', padding: '14px', borderRadius: '10px', cursor: 'pointer'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <strong>{v.marca} {v.modelo}</strong>
                    <span style={{ fontSize: '11px', fontWeight: 'bold', color: v.estado === 'DISPONIBLE' ? 'green' : '#b25e00' }}>
                      {v.estado}
                    </span>
                  </div>
                  <div style={{ fontSize: '12px', color: '#666', marginTop: '6px' }}>Placa: {v.placa} · Año: {v.anio} · Color: {v.color}</div>
                  <div style={{ fontSize: '15px', fontWeight: 'bold', color: '#10597b', marginTop: '8px' }}>{mostrarPrecio(v.precio)}</div>
                </div>
              ))}
            </div>
          )}

          {seleccionado && (
            <div style={{ marginTop: '18px', padding: '14px', background: '#f0f7fa', borderRadius: '8px', border: '1px solid #bce0ed' }}>
              <h3>Detalle del Vehículo #{seleccionado.idVehiculo ?? seleccionado.id}</h3>
              <p><strong>{seleccionado.marca} {seleccionado.modelo}</strong> ({seleccionado.anio}) - Chasis: {seleccionado.chasis} - Placa: {seleccionado.placa}</p>
              <p>Precio de catálogo: <strong>{mostrarPrecio(seleccionado.precio)}</strong> · Estado actual: <strong>{seleccionado.estado}</strong></p>
            </div>
          )}
        </section>
      )}

      {/* VISTA 2: HISTORIAL DE VENTAS */}
      {pestaña === 'ventas' && (
        <section className="panel" aria-labelledby="titulo-ventas">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h2 id="titulo-ventas">Historial de Ventas Registradas</h2>
            <span className="contador-items">{ventas.length} ventas</span>
          </div>
          <p className="ayuda">
            Datos reales consultados desde <code>GET /api/ventas</code> en el microservicio FastAPI.
          </p>

          {ventas.length === 0 ? (
            <p className="vacio" style={{ padding: '30px', textAlign: 'center', color: '#888' }}>
              No se han cargado ventas. Ingrese un JWT y pulse &quot;Consultar Ventas&quot;.
            </p>
          ) : (
            <div style={{ overflowX: 'auto', marginTop: '12px' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '13px' }}>
                <thead>
                  <tr style={{ background: '#eaf2f6', borderBottom: '2px solid #becdd5' }}>
                    <th style={{ padding: '10px' }}>ID Venta</th>
                    <th style={{ padding: '10px' }}>ID Vehículo</th>
                    <th style={{ padding: '10px' }}>ID Comprador</th>
                    <th style={{ padding: '10px' }}>Estado</th>
                    <th style={{ padding: '10px' }}>Notificación</th>
                    <th style={{ padding: '10px' }}>Precio Acordado</th>
                  </tr>
                </thead>
                <tbody>
                  {ventas.map((v) => (
                    <tr key={v.id} style={{ borderBottom: '1px solid #e1e9ee' }}>
                      <td style={{ padding: '9px 10px', fontWeight: 'bold' }}>#{v.id}</td>
                      <td style={{ padding: '9px 10px' }}>Vehículo #{v.vehiculoId ?? v.vehiculo_id}</td>
                      <td style={{ padding: '9px 10px' }}>Comprador #{v.compradorId ?? v.comprador_id}</td>
                      <td style={{ padding: '9px 10px' }}>
                        <span style={{
                          padding: '3px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: 'bold',
                          background: v.estado === 'COMPLETADA' ? '#d4edda' : '#fff3cd',
                          color: v.estado === 'COMPLETADA' ? '#155724' : '#856404'
                        }}>
                          {v.estado}
                        </span>
                      </td>
                      <td style={{ padding: '9px 10px' }}>{v.notificacion}</td>
                      <td style={{ padding: '9px 10px', fontWeight: 'bold', color: '#10597b' }}>
                        {mostrarPrecio(v.precioAcordado ?? v.precio_acordado)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      )}
    </main>
  );
}
