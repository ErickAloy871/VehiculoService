using System.Text.Json.Serialization;

namespace Proyecto_Vehiculos.DTO
{
    public class VehiculoDto
    {
        [JsonPropertyName("idVehiculo")]
        public int IdVehiculo { get; set; }

        [JsonPropertyName("id")]
        public int? IdAlias { set => IdVehiculo = value ?? IdVehiculo; }

        [JsonPropertyName("marca")]
        public string Marca { get; set; } = string.Empty;

        [JsonPropertyName("modelo")]
        public string Modelo { get; set; } = string.Empty;

        [JsonPropertyName("placa")]
        public string Placa { get; set; } = string.Empty;

        [JsonPropertyName("chasis")]
        public string Chasis { get; set; } = string.Empty;

        [JsonPropertyName("anio")]
        public int? Anio { get; set; }

        [JsonPropertyName("color")]
        public string Color { get; set; } = string.Empty;

        [JsonPropertyName("precio")]
        public decimal? Precio { get; set; }

        [JsonPropertyName("estado")]
        public string Estado { get; set; } = string.Empty;
    }
}
