package ec.edu.uta.notificaciones.messaging;

import org.springframework.amqp.core.Queue;
import org.springframework.amqp.core.QueueBuilder;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class RabbitMQConfig {

    @Value("${app.rabbitmq.queue:notificaciones.ventas}")
    private String queueName;

    @Bean
    public Queue notificacionesVentasQueue() {
        // Cola durable para persistencia de mensajes
        return QueueBuilder.durable(queueName).build();
    }
}
