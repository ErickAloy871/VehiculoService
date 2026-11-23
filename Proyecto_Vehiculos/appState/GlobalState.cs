using System;

namespace Proyecto_Vehiculos.appState
{
    /// <summary>
    /// Administra el estado global de la sesión del cliente de escritorio:
    /// URLs de los servicios, token JWT actual, rol, y clave de idempotencia activa.
    /// </summary>
    public static class GlobalState
    {
        // URLs base de los servicios según la arquitectura (Slide 3 y 5)
        public static string JavaUrl { get; set; } = "http://127.0.0.1:8080";
        public static string PythonUrl { get; set; } = "http://127.0.0.1:8002";

        // Token JWT de la sesión
        public static string? JwtToken { get; set; }

        // Última clave de idempotencia generada para operaciones de venta
        public static string? UltimaClaveIdempotencia { get; set; }

        // Último ID de venta registrada o consultada
        public static int? UltimoIdVenta { get; set; }

        // Usuario autenticado actual
        public static string UsuarioActual { get; set; } = "operador";

        /// <summary>
        /// Genera una nueva clave única de idempotencia con prefijo identificativo.
        /// </summary>
        public static string GenerarNuevaClaveIdempotencia()
        {
            UltimaClaveIdempotencia = "venta-" + Guid.NewGuid().ToString("N")[..8];
            return UltimaClaveIdempotencia;
        }

        /// <summary>
        /// Indica si hay un token JWT configurado.
        /// </summary>
        public static bool TieneToken => !string.IsNullOrWhiteSpace(JwtToken);
    }
}
