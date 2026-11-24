using System;
using System.Collections.Generic;
using System.Net;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Text;
using System.Text.Json;
using System.Threading.Tasks;
using Proyecto_Vehiculos.appState;
using Proyecto_Vehiculos.DTO;

namespace Proyecto_Vehiculos.apiClient
{
    public class VehiculosApi
    {
        private static readonly HttpClient _http = new() { Timeout = TimeSpan.FromSeconds(30) };
        private static readonly JsonSerializerOptions _jsonOptions = new()
        {
            PropertyNameCaseInsensitive = true
        };

        // 1. VEHÍCULOS: LISTAR (GET /api/vehiculos)
        public async Task<ApiResponse<List<VehiculoDto>>> ListarVehiculosAsync(string? marca = null, string? jwt = null)
        {
            try
            {
                string token = jwt ?? GlobalState.JwtToken ?? string.Empty;
                string url = $"{GlobalState.BaseUrl.TrimEnd('/')}/api/vehiculos";
                if (!string.IsNullOrWhiteSpace(marca))
                {
                    url += $"?marca={Uri.EscapeDataString(marca.Trim())}";
                }

                using var req = new HttpRequestMessage(HttpMethod.Get, url);
                if (!string.IsNullOrWhiteSpace(token))
                {
                    req.Headers.Authorization = new AuthenticationHeaderValue("Bearer", token);
                }

                using var res = await _http.SendAsync(req);
                var rawJson = await res.Content.ReadAsStringAsync();

                if (res.IsSuccessStatusCode)
                {
                    var lista = JsonSerializer.Deserialize<List<VehiculoDto>>(rawJson, _jsonOptions) ?? new List<VehiculoDto>();
                    return ApiResponse<List<VehiculoDto>>.Success(lista, res.StatusCode, rawJson);
                }

                return ApiResponse<List<VehiculoDto>>.Fail(res.StatusCode, $"Error {(int)res.StatusCode}: {res.ReasonPhrase}", rawJson);
            }
            catch (Exception ex)
            {
                return ApiResponse<List<VehiculoDto>>.Fail(HttpStatusCode.ServiceUnavailable, $"No se pudo conectar con NGINX (:8090): {ex.Message}");
            }
        }

        // 2. VEHÍCULOS: CREAR (POST /api/vehiculos)
        public async Task<ApiResponse<VehiculoDto>> CrearVehiculoAsync(VehiculoCrearDto dto, string? jwt = null)
        {
            try
            {
                string token = jwt ?? GlobalState.JwtToken ?? string.Empty;
                string url = $"{GlobalState.BaseUrl.TrimEnd('/')}/api/vehiculos";

                using var req = new HttpRequestMessage(HttpMethod.Post, url);
                if (!string.IsNullOrWhiteSpace(token))
                {
                    req.Headers.Authorization = new AuthenticationHeaderValue("Bearer", token);
                }

                string jsonBody = JsonSerializer.Serialize(dto, _jsonOptions);
                req.Content = new StringContent(jsonBody, Encoding.UTF8, "application/json");

                using var res = await _http.SendAsync(req);
                var rawJson = await res.Content.ReadAsStringAsync();

                if (res.IsSuccessStatusCode)
                {
                    var creado = JsonSerializer.Deserialize<VehiculoDto>(rawJson, _jsonOptions);
                    return ApiResponse<VehiculoDto>.Success(creado, res.StatusCode, rawJson);
                }

                return ApiResponse<VehiculoDto>.Fail(res.StatusCode, $"Error {(int)res.StatusCode}: {res.ReasonPhrase}", rawJson);
            }
            catch (Exception ex)
            {
                return ApiResponse<VehiculoDto>.Fail(HttpStatusCode.ServiceUnavailable, $"Error de conexión con NGINX: {ex.Message}");
            }
        }

        // 3. VEHÍCULOS: CONSULTAR POR ID (GET /api/vehiculos/{id})
        public async Task<ApiResponse<VehiculoDto>> ObtenerVehiculoPorIdAsync(int id, string? jwt = null)
        {
            try
            {
                string token = jwt ?? GlobalState.JwtToken ?? string.Empty;
                string url = $"{GlobalState.BaseUrl.TrimEnd('/')}/api/vehiculos/{id}";

                using var req = new HttpRequestMessage(HttpMethod.Get, url);
                if (!string.IsNullOrWhiteSpace(token))
                {
                    req.Headers.Authorization = new AuthenticationHeaderValue("Bearer", token);
                }

                using var res = await _http.SendAsync(req);
                var rawJson = await res.Content.ReadAsStringAsync();

                if (res.IsSuccessStatusCode)
                {
                    var v = JsonSerializer.Deserialize<VehiculoDto>(rawJson, _jsonOptions);
                    return ApiResponse<VehiculoDto>.Success(v, res.StatusCode, rawJson);
                }

                return ApiResponse<VehiculoDto>.Fail(res.StatusCode, $"Error {(int)res.StatusCode}: {res.ReasonPhrase}", rawJson);
            }
            catch (Exception ex)
            {
                return ApiResponse<VehiculoDto>.Fail(HttpStatusCode.ServiceUnavailable, $"Error de conexión con NGINX: {ex.Message}");
            }
        }

        // 4. COMPRADORES: LISTAR (GET /api/compradores)
        public async Task<ApiResponse<List<CompradorDto>>> ListarCompradoresAsync(string? jwt = null)
        {
            try
            {
                string token = jwt ?? GlobalState.JwtToken ?? string.Empty;
                string url = $"{GlobalState.BaseUrl.TrimEnd('/')}/api/compradores";

                using var req = new HttpRequestMessage(HttpMethod.Get, url);
                if (!string.IsNullOrWhiteSpace(token))
                {
                    req.Headers.Authorization = new AuthenticationHeaderValue("Bearer", token);
                }

                using var res = await _http.SendAsync(req);
                var rawJson = await res.Content.ReadAsStringAsync();

                if (res.IsSuccessStatusCode)
                {
                    var lista = JsonSerializer.Deserialize<List<CompradorDto>>(rawJson, _jsonOptions) ?? new List<CompradorDto>();
                    return ApiResponse<List<CompradorDto>>.Success(lista, res.StatusCode, rawJson);
                }

                return ApiResponse<List<CompradorDto>>.Fail(res.StatusCode, $"Error {(int)res.StatusCode}: {res.ReasonPhrase}", rawJson);
            }
            catch (Exception ex)
            {
                return ApiResponse<List<CompradorDto>>.Fail(HttpStatusCode.ServiceUnavailable, $"Error conectando con NGINX: {ex.Message}");
            }
        }

        // 5. COMPRADORES: CREAR (POST /api/compradores)
        public async Task<ApiResponse<CompradorDto>> CrearCompradorAsync(CompradorCrearDto dto, string? jwt = null)
        {
            try
            {
                string token = jwt ?? GlobalState.JwtToken ?? string.Empty;
                string url = $"{GlobalState.BaseUrl.TrimEnd('/')}/api/compradores";

                using var req = new HttpRequestMessage(HttpMethod.Post, url);
                if (!string.IsNullOrWhiteSpace(token))
                {
                    req.Headers.Authorization = new AuthenticationHeaderValue("Bearer", token);
                }

                string jsonBody = JsonSerializer.Serialize(dto, _jsonOptions);
                req.Content = new StringContent(jsonBody, Encoding.UTF8, "application/json");

                using var res = await _http.SendAsync(req);
                var rawJson = await res.Content.ReadAsStringAsync();

                if (res.IsSuccessStatusCode)
                {
                    var creado = JsonSerializer.Deserialize<CompradorDto>(rawJson, _jsonOptions);
                    return ApiResponse<CompradorDto>.Success(creado, res.StatusCode, rawJson);
                }

                return ApiResponse<CompradorDto>.Fail(res.StatusCode, $"Error {(int)res.StatusCode}: {res.ReasonPhrase}", rawJson);
            }
            catch (Exception ex)
            {
                return ApiResponse<CompradorDto>.Fail(HttpStatusCode.ServiceUnavailable, $"Error de conexión con NGINX: {ex.Message}");
            }
        }

        // 6. VENTAS: LISTAR (GET /api/ventas)
        public async Task<ApiResponse<List<VentaResponseDto>>> ListarVentasAsync(string? jwt = null)
        {
            try
            {
                string token = jwt ?? GlobalState.JwtToken ?? string.Empty;
                string url = $"{GlobalState.BaseUrl.TrimEnd('/')}/api/ventas";

                using var req = new HttpRequestMessage(HttpMethod.Get, url);
                if (!string.IsNullOrWhiteSpace(token))
                {
                    req.Headers.Authorization = new AuthenticationHeaderValue("Bearer", token);
                }

                using var res = await _http.SendAsync(req);
                var rawJson = await res.Content.ReadAsStringAsync();

                if (res.IsSuccessStatusCode)
                {
                    var lista = JsonSerializer.Deserialize<List<VentaResponseDto>>(rawJson, _jsonOptions) ?? new List<VentaResponseDto>();
                    return ApiResponse<List<VentaResponseDto>>.Success(lista, res.StatusCode, rawJson);
                }

                return ApiResponse<List<VentaResponseDto>>.Fail(res.StatusCode, $"Error {(int)res.StatusCode}: {res.ReasonPhrase}", rawJson);
            }
            catch (Exception ex)
            {
                return ApiResponse<List<VentaResponseDto>>.Fail(HttpStatusCode.ServiceUnavailable, $"Error conectando con NGINX: {ex.Message}");
            }
        }

        // 7. VENTAS: CONSULTAR INDIVIDUAL (GET /api/ventas/{id})
        public async Task<ApiResponse<VentaResponseDto>> ConsultarVentaAsync(int idVenta, string? jwt = null)
        {
            try
            {
                string token = jwt ?? GlobalState.JwtToken ?? string.Empty;
                string url = $"{GlobalState.BaseUrl.TrimEnd('/')}/api/ventas/{idVenta}";

                using var req = new HttpRequestMessage(HttpMethod.Get, url);
                if (!string.IsNullOrWhiteSpace(token))
                {
                    req.Headers.Authorization = new AuthenticationHeaderValue("Bearer", token);
                }

                using var res = await _http.SendAsync(req);
                var rawJson = await res.Content.ReadAsStringAsync();

                if (res.IsSuccessStatusCode)
                {
                    var venta = JsonSerializer.Deserialize<VentaResponseDto>(rawJson, _jsonOptions);
                    return ApiResponse<VentaResponseDto>.Success(venta, res.StatusCode, rawJson);
                }

                return ApiResponse<VentaResponseDto>.Fail(res.StatusCode, $"Error {(int)res.StatusCode}: {res.ReasonPhrase}", rawJson);
            }
            catch (Exception ex)
            {
                return ApiResponse<VentaResponseDto>.Fail(HttpStatusCode.ServiceUnavailable, $"Error de conexión con NGINX: {ex.Message}");
            }
        }
    }
}
