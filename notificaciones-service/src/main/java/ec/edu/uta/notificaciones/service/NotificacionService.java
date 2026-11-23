package ec.edu.uta.notificaciones.service;

import ec.edu.uta.notificaciones.dto.NotificacionItem;
import ec.edu.uta.notificaciones.dto.NotificacionRequest;
import ec.edu.uta.notificaciones.dto.NotificacionResponse;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.concurrent.atomic.AtomicLong;

@Service
public class NotificacionService {

    private static final Set<String> TIPOS_PERMITIDOS =
            Set.of("REGISTRO", "ACTUALIZACION", "ELIMINACION", "VENTA");

    private final List<NotificacionItem> historial = new CopyOnWriteArrayList<>();
    private final Set<String> eventosProcesados = ConcurrentHashMap.newKeySet();
    private final AtomicLong contadorId = new AtomicLong(1);
    private final ObjectMapper objectMapper = new ObjectMapper();

    public NotificacionResponse procesar(NotificacionRequest request) {
        if (request.getVehiculoId() == null || request.getVehiculoId() <= 0) {
            throw new IllegalArgumentException("vehiculoId debe estar presente y ser válido");
        }
        if (request.getDestinatario() == null || request.getDestinatario().trim().isEmpty()) {
            throw new IllegalArgumentException("El destinatario no puede estar vacío");
        }
        if (request.getMensaje() == null || request.getMensaje().trim().isEmpty()) {
            throw new IllegalArgumentException("El mensaje no puede estar vacío");
        }
        if (request.getTipo() == null || !TIPOS_PERMITIDOS.contains(request.getTipo().toUpperCase())) {
            throw new IllegalArgumentException("Tipo de notificación no válido");
        }

        // Registrar en historial en memoria
        NotificacionItem item = new NotificacionItem(
                contadorId.getAndIncrement(),
                null,
                request.getTipo(),
                null,
                request.getVehiculoId(),
                request.getDestinatario(),
                request.getMensaje(),
                LocalDateTime.now().format(DateTimeFormatter.ISO_DATE_TIME)
        );
        historial.add(0, item);

        System.out.println("=================================");
        System.out.println("NOTIFICACIÓN HTTP RECIBIDA");
        System.out.println("Vehículo: " + request.getVehiculoId());
        System.out.println("Tipo: " + request.getTipo());
        System.out.println("Mensaje: " + request.getMensaje());
        System.out.println("=================================");

        return new NotificacionResponse(
                true,
                "ENVIADA",
                "Notificación procesada correctamente"
        );
    }

    public boolean procesarMensajeRabbitMQ(String payload) {
        try {
            JsonNode node = objectMapper.readTree(payload);
            String eventoId = node.has("eventoId") ? node.get("eventoId").asText() : null;

            // Idempotencia: evitar duplicados por eventoId
            if (eventoId != null && !eventosProcesados.add(eventoId)) {
                System.out.println("Evento RabbitMQ ya procesado anteriormente: " + eventoId);
                return true;
            }

            Integer ventaId = node.has("ventaId") ? node.get("ventaId").asInt() : null;
            Integer vehiculoId = node.has("vehiculoId") ? node.get("vehiculoId").asInt() : null;
            String tipo = node.has("tipo") ? node.get("tipo").asText() : "VENTA";
            String mensaje = node.has("mensaje") ? node.get("mensaje").asText() : "Venta confirmada";
            String fechaHora = node.has("fechaHora") ? node.get("fechaHora").asText() : LocalDateTime.now().format(DateTimeFormatter.ISO_DATE_TIME);

            NotificacionItem item = new NotificacionItem(
                    contadorId.getAndIncrement(),
                    eventoId,
                    tipo,
                    ventaId,
                    vehiculoId,
                    "cliente@ejemplo.com",
                    mensaje,
                    fechaHora
            );
            historial.add(0, item);

            System.out.println("=================================");
            System.out.println("EVENTO RABBITMQ CONSUMIDO CON ÉXITO");
            System.out.println("EventoId: " + eventoId);
            System.out.println("VentaId: " + ventaId);
            System.out.println("VehículoId: " + vehiculoId);
            System.out.println("Mensaje: " + mensaje);
            System.out.println("=================================");
            return true;
        } catch (Exception e) {
            System.err.println("Error procesando mensaje RabbitMQ: " + e.getMessage());
            return false;
        }
    }

    public List<NotificacionItem> obtenerHistorial() {
        return new ArrayList<>(historial);
    }
}
