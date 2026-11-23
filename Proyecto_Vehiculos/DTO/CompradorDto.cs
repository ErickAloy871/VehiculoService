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

        [JsonPropertyName("documento")]
        public string Documento { get; set; } = string.Empty;

        [JsonPropertyName("correo")]
        public string Correo { get; set; } = string.Empty;

        public override string ToString()
        {
            return $"[{Id}] {Nombre} (Doc: {Documento})";
        }
    }

    public class CompradorCrearDto
    {
        [JsonPropertyName("documento")]
        public string Documento { get; set; } = string.Empty;

        [JsonPropertyName("nombre")]
        public string Nombre { get; set; } = string.Empty;

        [JsonPropertyName("correo")]
        public string Correo { get; set; } = string.Empty;
    }

    public class VehiculoCrearDto
    {
        [JsonPropertyName("marca")]
        public string Marca { get; set; } = string.Empty;

        [JsonPropertyName("modelo")]
        public string Modelo { get; set; } = string.Empty;

        [JsonPropertyName("placa")]
        public string Placa { get; set; } = string.Empty;

        [JsonPropertyName("chasis")]
        public string Chasis { get; set; } = string.Empty;

        [JsonPropertyName("anio")]
        public int Anio { get; set; }

        [JsonPropertyName("color")]
        public string Color { get; set; } = string.Empty;

        [JsonPropertyName("precio")]
        public decimal Precio { get; set; }
    }
}
