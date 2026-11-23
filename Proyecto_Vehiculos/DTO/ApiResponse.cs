using System.Net;

namespace Proyecto_Vehiculos.DTO
{
    public class ApiResponse<T>
    {
        public bool IsSuccess { get; set; }
        public HttpStatusCode StatusCode { get; set; }
        public int StatusCodeNumber => (int)StatusCode;
        public string? StatusMessage { get; set; }
        public T? Data { get; set; }
        public string? RawJson { get; set; }
        public string? LocationHeader { get; set; }
        public string? ErrorMessage { get; set; }

        public static ApiResponse<T> Success(T? data, HttpStatusCode code, string? rawJson = null, string? location = null)
        {
            return new ApiResponse<T>
            {
                IsSuccess = true,
                StatusCode = code,
                StatusMessage = $"{((int)code)} {code}",
                Data = data,
                RawJson = rawJson,
                LocationHeader = location
            };
        }

        public static ApiResponse<T> Fail(HttpStatusCode code, string errorMessage, string? rawJson = null)
        {
            return new ApiResponse<T>
            {
                IsSuccess = false,
                StatusCode = code,
                StatusMessage = $"{((int)code)} {code}",
                ErrorMessage = errorMessage,
                RawJson = rawJson
            };
        }
    }
}

