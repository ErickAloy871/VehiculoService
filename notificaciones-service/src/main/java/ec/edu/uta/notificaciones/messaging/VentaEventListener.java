package ec.edu.uta.notificaciones.messaging;

import ec.edu.uta.notificaciones.service.NotificacionService;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.stereotype.Component;

@Component
public class VentaEventListener {

    private final NotificacionService notificacionService;

    public VentaEventListener(NotificacionService notificacionService) {
        this.notificacionService = notificacionService;
    }

    @RabbitListener(queues = "${app.rabbitmq.queue:notificaciones.ventas}")
    public void recibirEventoVenta(String mensajeJson) {
        notificacionService.procesarMensajeRabbitMQ(mensajeJson);
    }
}
