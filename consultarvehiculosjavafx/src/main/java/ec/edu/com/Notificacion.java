package ec.edu.com;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;

@JsonIgnoreProperties(ignoreUnknown = true)
public record Notificacion(
        Long id,
        String eventoId,
        String tipo,
        Integer ventaId,
        Integer vehiculoId,
        String destinatario,
        String mensaje,
        String fechaHora) {
}
