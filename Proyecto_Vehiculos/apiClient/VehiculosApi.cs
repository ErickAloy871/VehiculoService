using System;
using System.Collections.Generic;
using System.Net;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Text.Json;
using System.Threading.Tasks;
using Proyecto_Vehiculos.appState;
using Proyecto_Vehiculos.DTO;

namespace Proyecto_Vehiculos.apiClient
{
    public class VehiculosApi
    {
        private static readonly HttpClient _http = new() { Timeout = TimeSpan.FromSeconds(10) };
        private static readonly JsonSerializerOptions _jsonOptions = new()
        {
            PropertyNameCaseInsensitive = true
        };

        public async Task<ApiResponse<List<VehiculoDto>>> ListarVehiculosAsync(string? marca = null, string? jwt = null)
        {
            try
            {
                string token = jwt ?? GlobalState.JwtToken ?? string.Empty;
                string url = $"{GlobalState.JavaUrl.TrimEnd('/')}/api/vehiculos";
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
            catch (HttpRequestException ex)
            {
                return ApiResponse<List<VehiculoDto>>.Fail(HttpStatusCode.ServiceUnavailable, $"No conecta con Java (:8080): {ex.Message}");
            }
            catch (Exception ex)
            {
                return ApiResponse<List<VehiculoDto>>.Fail(HttpStatusCode.InternalServerError, ex.Message);
            }
        }

        public async Task<ApiResponse<VehiculoDto>> ObtenerVehiculoPorIdAsync(int id, string? jwt = null)
        {
            try
            {
                string token = jwt ?? GlobalState.JwtToken ?? string.Empty;
                string url = $"{GlobalState.JavaUrl.TrimEnd('/')}/api/vehiculos/{id}";

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
            catch (HttpRequestException ex)
            {
                return ApiResponse<VehiculoDto>.Fail(HttpStatusCode.ServiceUnavailable, $"No conecta con Java (:8080): {ex.Message}");
            }
            catch (Exception ex)
            {
                return ApiResponse<VehiculoDto>.Fail(HttpStatusCode.InternalServerError, ex.Message);
            }
        }

        public async Task<ApiResponse<VentaResponseDto>> ConsultarVentaAsync(int idVenta, string? jwt = null)
        {
            try
            {
                string token = jwt ?? GlobalState.JwtToken ?? string.Empty;
                string url = $"{GlobalState.PythonUrl.TrimEnd('/')}/api/ventas/{idVenta}";

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
            catch (HttpRequestException ex)
            {
                return ApiResponse<VentaResponseDto>.Fail(HttpStatusCode.ServiceUnavailable, $"No conecta con Python (:8002): {ex.Message}");
            }
            catch (Exception ex)
            {
                return ApiResponse<VentaResponseDto>.Fail(HttpStatusCode.InternalServerError, ex.Message);
            }
        }

        public async Task<ApiResponse<int>> ProbarPermisosCompradoresAsync(string? jwt = null)
        {
            try
            {
                string token = jwt ?? GlobalState.JwtToken ?? string.Empty;
                string url = $"{GlobalState.PythonUrl.TrimEnd('/')}/api/compradores";

                using var req = new HttpRequestMessage(HttpMethod.Get, url);
                if (!string.IsNullOrWhiteSpace(token))
                {
                    req.Headers.Authorization = new AuthenticationHeaderValue("Bearer", token);
                }

                using var res = await _http.SendAsync(req);
                var rawJson = await res.Content.ReadAsStringAsync();

                if (res.IsSuccessStatusCode)
                {
                    var lista = JsonSerializer.Deserialize<List<CompradorDto>>(rawJson, _jsonOptions);
                    int count = lista?.Count ?? 0;
                    return ApiResponse<int>.Success(count, res.StatusCode, rawJson);
                }

                return ApiResponse<int>.Fail(res.StatusCode, $"Error {(int)res.StatusCode}: {res.ReasonPhrase}", rawJson);
            }
            catch (HttpRequestException ex)
            {
                return ApiResponse<int>.Fail(HttpStatusCode.ServiceUnavailable, $"No conecta con Python (:8002): {ex.Message}");
            }
            catch (Exception ex)
            {
                return ApiResponse<int>.Fail(HttpStatusCode.InternalServerError, ex.Message);
            }
        }
    }
}
