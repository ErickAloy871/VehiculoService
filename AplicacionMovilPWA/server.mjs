/**
 * Servidor de desarrollo local sin dependencias externas.
 * Sirve la PWA y reenvía únicamente GET /api/vehiculos hacia Spring Boot.
 * La URL pública siempre es del mismo origen para evitar problemas CORS.
 */
import { createServer } from 'node:http';
import { readFile, stat } from 'node:fs/promises';
import { resolve, extname, sep } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = resolve(fileURLToPath(new URL('.', import.meta.url)));
const TIPOS = {
  '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8', '.png': 'image/png',
  '.webmanifest': 'application/manifest+json; charset=utf-8',
  '.json': 'application/json; charset=utf-8', '.svg': 'image/svg+xml',
};

export function crearServidor({
  directorio = resolve(ROOT, 'public'),
  apiBase = process.env.API_BASE_URL || 'http://127.0.0.1:8090',
} = {}) {
  const carpeta = resolve(directorio);

  return createServer(async (peticion, respuesta) => {
    const url = new URL(peticion.url || '/', 'http://localhost');
    respuesta.setHeader('X-Content-Type-Options', 'nosniff');
    respuesta.setHeader('Referrer-Policy', 'no-referrer');
    respuesta.setHeader('Cache-Control', 'no-store');

    // Reenvío de llamadas REST hacia NGINX (:8090)
    if (url.pathname.startsWith('/api/') || url.pathname === '/oauth/token') {
      const abortador = new AbortController();
      const temporizador = setTimeout(() => abortador.abort(), 15000);
      try {
        const encabezados = {};
        for (const [k, v] of Object.entries(peticion.headers)) {
          if (!['host', 'connection'].includes(k.toLowerCase())) {
            encabezados[k] = v;
          }
        }

        let cuerpo = undefined;
        if (['POST', 'PUT', 'PATCH'].includes(peticion.method)) {
          const chunks = [];
          for await (const chunk of peticion) chunks.push(chunk);
          cuerpo = Buffer.concat(chunks);
        }

        const remoto = await fetch(`${apiBase.replace(/\/$/, '')}${url.pathname}${url.search}`, {
          method: peticion.method,
          headers: encabezados,
          body: cuerpo,
          signal: abortador.signal,
          cache: 'no-store',
        });

        respuesta.writeHead(remoto.status, {
          'Content-Type': remoto.headers.get('content-type') || 'application/json; charset=utf-8',
          'Cache-Control': 'no-store',
        });
        respuesta.end(Buffer.from(await remoto.arrayBuffer()));
      } catch (error) {
        const tiempoAgotado = error.name === 'AbortError';
        respuesta.writeHead(tiempoAgotado ? 504 : 502, { 'Content-Type': 'application/json; charset=utf-8' });
        respuesta.end(JSON.stringify({ error: tiempoAgotado ? 'Tiempo de espera agotado' : 'Gateway NGINX no disponible' }));
      } finally {
        clearTimeout(temporizador);
      }
      return;
    }

    if (peticion.method !== 'GET' && peticion.method !== 'HEAD') {
      respuesta.writeHead(405); respuesta.end(); return;
    }

    let ruta;
    try { ruta = decodeURIComponent(url.pathname); }
    catch { respuesta.writeHead(400); respuesta.end(); return; }
    const archivo = resolve(carpeta, '.' + (ruta === '/' ? '/index.html' : ruta));
    if (!(archivo === carpeta || archivo.startsWith(carpeta + sep))) {
      respuesta.writeHead(403); respuesta.end(); return;
    }
    try {
      const detalle = await stat(archivo);
      if (!detalle.isFile()) throw new Error('Archivo no encontrado');
      respuesta.setHeader('Content-Type', TIPOS[extname(archivo)] || 'application/octet-stream');
      if (peticion.method === 'HEAD') { respuesta.writeHead(200); respuesta.end(); return; }
      respuesta.writeHead(200);
      respuesta.end(await readFile(archivo));
    } catch {
      respuesta.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
      respuesta.end('Recurso no encontrado');
    }
  });
}

// Se habilita uso como módulo para pruebas, sin iniciar puerto al importarlo.
if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const argPuerto = process.argv.find((arg) => arg.startsWith('--port='));
  const argCarpeta = process.argv.find((arg) => arg.startsWith('--dir='));
  const puerto = Number(argPuerto?.split('=')[1] || process.env.PORT || 5173);
  const host = process.env.HOST || '127.0.0.1';
  const carpeta = resolve(ROOT, argCarpeta?.split('=')[1] || 'public');
  crearServidor({ directorio: carpeta }).listen(puerto, host, () => {
    console.log(`PWA disponible: http://localhost:${puerto}`);
    console.log(`Proxy de consulta: /api/vehiculos -> ${process.env.API_BASE_URL || 'http://127.0.0.1:8080'}/api/vehiculos`);
    console.log('Para cerrar: Ctrl + C');
  });
}
