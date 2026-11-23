package ec.edu.com;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.List;
import java.util.concurrent.CompletableFuture;

public final class NotificacionesApiClient {
    // Consulta las notificaciones a través de NGINX (:8090) o directo a Notificaciones (:8081)
    private static final String URL_API = "http://127.0.0.1:8090/api/notificaciones";

    private final HttpClient clienteHttp = HttpClient.newBuilder()
            .connectTimeout(Duration.ofSeconds(4))
            .build();

    private final ObjectMapper mapper = new ObjectMapper();

    public CompletableFuture<ResultadoNotificaciones> consultarNotificaciones() {
        HttpRequest solicitud = HttpRequest.newBuilder(URI.create(URL_API))
                .timeout(Duration.ofSeconds(6))
                .header("Accept", "application/json")
                .GET()
                .build();

        return clienteHttp.sendAsync(solicitud, HttpResponse.BodyHandlers.ofString())
                .thenApply(respuesta -> {
                    int codigo = respuesta.statusCode();
                    if (codigo != 200) {
                        return new ResultadoNotificaciones(codigo, List.of(), "Error HTTP " + codigo);
                    }

                    try {
                        List<Notificacion> lista = mapper.readValue(
                                respuesta.body(),
                                new TypeReference<List<Notificacion>>() {});
                        return new ResultadoNotificaciones(codigo, lista, null);
                    } catch (IOException e) {
                        return new ResultadoNotificaciones(codigo, List.of(), "Error al interpretar JSON: " + e.getMessage());
                    }
                })
                .exceptionally(ex -> new ResultadoNotificaciones(503, List.of(), "Servicio no disponible: " + ex.getMessage()));
    }

    public record ResultadoNotificaciones(int codigoHttp, List<Notificacion> notificaciones, String error) {
    }
}
