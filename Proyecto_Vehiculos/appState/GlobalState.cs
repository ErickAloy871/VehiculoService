using System;

namespace Proyecto_Vehiculos.appState
{
    /// <summary>
    /// Administra el estado global de la sesión del cliente de escritorio:
    /// URLs de los servicios mediante NGINX (:8090), token JWT actual, rol, y usuario.
    /// </summary>
    public static class GlobalState
    {
        // Punto único de entrada REST en entorno local según la arquitectura
        public static string BaseUrl { get; set; } = "http://127.0.0.1:8090";
        public static string JavaUrl => BaseUrl;
        public static string PythonUrl => BaseUrl;

        // Token JWT de la sesión
        public static string? JwtToken { get; set; }

        // Última clave de idempotencia generada
        public static string? UltimaClaveIdempotencia { get; set; }

        // Último ID de venta consultada
        public static int? UltimoIdVenta { get; set; }

        // Usuario autenticado actual
        public static string UsuarioActual { get; set; } = "operador";

        public static string GenerarNuevaClaveIdempotencia()
        {
            UltimaClaveIdempotencia = "venta-" + Guid.NewGuid().ToString("N")[..8];
            return UltimaClaveIdempotencia;
        }

        public static bool TieneToken => !string.IsNullOrWhiteSpace(JwtToken);
    }
}
