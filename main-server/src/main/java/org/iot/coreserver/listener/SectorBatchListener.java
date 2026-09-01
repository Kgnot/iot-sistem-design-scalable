package org.iot.coreserver.listener;


import org.iot.coreserver.config.RabbitMQConfig;
import org.iot.coreserver.dto.SectorBatchDTO;
import org.iot.coreserver.service.SectorEventService;
import org.springframework.amqp.rabbit.annotation.RabbitListener;
import org.springframework.stereotype.Component;
import tools.jackson.databind.ObjectMapper;

import java.util.logging.Logger;

@Component
public class SectorBatchListener {

    private static final Logger logger = Logger.getLogger(SectorBatchListener.class.getName());

    private final SectorEventService sectorEventService;
    private final ObjectMapper objectMapper;

    public SectorBatchListener(SectorEventService sectorEventService, ObjectMapper objectMapper) {
        this.sectorEventService = sectorEventService;
        this.objectMapper = objectMapper;
    }

    @RabbitListener(queues = RabbitMQConfig.SECTOR_BATCH_QUEUE)
    public void onSectorBatch(byte[] messageBody) throws Exception {
        logger.info("Mensaje crudo recibido de RabbitMQ (" + messageBody.length + " bytes)");
        SectorBatchDTO batch = objectMapper.readValue(messageBody, SectorBatchDTO.class);
        sectorEventService.broadcast(batch);
    }
}