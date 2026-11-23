using System;
using System.Text.Json.Serialization;

namespace Proyecto_Vehiculos.DTO
{
    public class VentaRequestDto
    {
        [JsonPropertyName("vehiculoId")]
        public int VehiculoId { get; set; }

        [JsonPropertyName("compradorId")]
        public int CompradorId { get; set; }
    }

    public class VentaResponseDto
    {
        [JsonPropertyName("id")]
        public int? Id { get; set; }

        [JsonPropertyName("vehiculoId")]
        public int? VehiculoId { get; set; }

        [JsonPropertyName("compradorId")]
        public int? CompradorId { get; set; }

        [JsonPropertyName("estado")]
        public string Estado { get; set; } = string.Empty; // COMPLETADA, EN_REVISION, FALLIDA

        [JsonPropertyName("notificacion")]
        public string Notificacion { get; set; } = string.Empty; // ENVIADA, PENDIENTE

        [JsonPropertyName("precioAcordado")]
        public object? PrecioAcordadoRaw { get; set; }

        [JsonIgnore]
        public string PrecioAcordado => PrecioAcordadoRaw?.ToString() ?? "0.00";

        [JsonPropertyName("mensaje")]
        public string? Mensaje { get; set; }
    }
}

