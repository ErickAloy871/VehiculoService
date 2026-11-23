package ec.edu.uta.venta_vehiculos_api.dto;

import ec.edu.uta.venta_vehiculos_api.model.HistorialPrecio;
import java.math.BigDecimal;
import java.time.LocalDateTime;

public record HistorialPrecioResponse(
        Integer id,
        Integer vehiculoId,
        BigDecimal precioAnterior,
        BigDecimal precioNuevo,
        String usuario,
        LocalDateTime fecha
) {
    public static HistorialPrecioResponse de(HistorialPrecio h) {
        return new HistorialPrecioResponse(
                h.getId(),
                h.getVehiculo().getIdVehiculo(),
                h.getPrecioAnterior(),
                h.getPrecioNuevo(),
                h.getUsuario(),
                h.getFecha()
        );
    }
}

