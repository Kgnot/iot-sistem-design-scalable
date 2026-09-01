package org.iot.coreserver.config;

import org.springframework.amqp.core.Binding;
import org.springframework.amqp.core.BindingBuilder;
import org.springframework.amqp.core.Queue;
import org.springframework.amqp.core.TopicExchange;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class RabbitMQConfig {

    public static final String EXCHANGE_NAME = "events";
    public static final String SECTOR_BATCH_QUEUE = "sector.batch.spring-consumer";
    public static final String SECTOR_BATCH_ROUTING_KEY = "sector.batch.completed";

    @Bean
    public TopicExchange eventsExchange() {
        return new TopicExchange(EXCHANGE_NAME, true, false);
    }

    @Bean
    public Queue sectorBatchQueue() {
        return new Queue(SECTOR_BATCH_QUEUE, true); // durable
    }

    @Bean
    public Binding sectorBatchBinding(Queue sectorBatchQueue, TopicExchange eventsExchange) {
        return BindingBuilder.bind(sectorBatchQueue)
                .to(eventsExchange)
                .with(SECTOR_BATCH_ROUTING_KEY);
    }
}