using System;
using System.Text.Json.Serialization;

namespace Proyecto_Vehiculos.DTO
{
    public class CompradorDto
    {
        [JsonPropertyName("id")]
        public int? Id { get; set; }

        [JsonPropertyName("nombre")]
        public string Nombre { get; set; } = string.Empty;

        [JsonPropertyName("identificacion")]
        public string? Identificacion { get; set; }

        [JsonPropertyName("email")]
        public string? Email { get; set; }

        [JsonPropertyName("telefono")]
        public string? Telefono { get; set; }

        public override string ToString()
        {
            return $"[{Id}] {Nombre} ({Identificacion ?? Email})";
        }
    }
}

