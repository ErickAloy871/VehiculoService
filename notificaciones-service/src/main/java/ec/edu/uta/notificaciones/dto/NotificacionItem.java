package ec.edu.uta.notificaciones.dto;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

public class NotificacionItem {
    private Long id;
    private String eventoId;
    private String tipo;
    private Integer ventaId;
    private Integer vehiculoId;
    private String destinatario;
    private String mensaje;
    private String fechaHora;

    public NotificacionItem() {
    }

    public NotificacionItem(Long id, String eventoId, String tipo, Integer ventaId, Integer vehiculoId, String destinatario, String mensaje, String fechaHora) {
        this.id = id;
        this.eventoId = eventoId;
        this.tipo = tipo;
        this.ventaId = ventaId;
        this.vehiculoId = vehiculoId;
        this.destinatario = destinatario;
        this.mensaje = mensaje;
        this.fechaHora = fechaHora != null ? fechaHora : LocalDateTime.now().format(DateTimeFormatter.ISO_DATE_TIME);
    }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getEventoId() {
        return eventoId;
    }

    public void setEventoId(String eventoId) {
        this.eventoId = eventoId;
    }

    public String getTipo() {
        return tipo;
    }

    public void setTipo(String tipo) {
        this.tipo = tipo;
    }

    public Integer getVentaId() {
        return ventaId;
    }

    public void setVentaId(Integer ventaId) {
        this.ventaId = ventaId;
    }

    public Integer getVehiculoId() {
        return vehiculoId;
    }

    public void setVehiculoId(Integer vehiculoId) {
        this.vehiculoId = vehiculoId;
    }

    public String getDestinatario() {
        return destinatario;
    }

    public void setDestinatario(String destinatario) {
        this.destinatario = destinatario;
    }

    public String getMensaje() {
        return mensaje;
    }

    public void setMensaje(String mensaje) {
        this.mensaje = mensaje;
    }

    public String getFechaHora() {
        return fechaHora;
    }

    public void setFechaHora(String fechaHora) {
        this.fechaHora = fechaHora;
    }
}
