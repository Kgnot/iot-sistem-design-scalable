package org.iot.coreserver.service;


import org.iot.coreserver.dto.SectorBatchDTO;
import org.springframework.stereotype.Service;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.logging.Level;
import java.util.logging.Logger;

@Service
public class SectorEventService {

    private static final Logger logger = Logger.getLogger(SectorEventService.class.getName());

//    private static final long EMITTER_TIMEOUT_MS = 30 * 60 * 1000L; // 30 min

    private final List<SseEmitter> emitters = new CopyOnWriteArrayList<>();

    public SseEmitter subscribe() {
        SseEmitter emitter = new SseEmitter(0L); // sin timeout
        emitters.add(emitter);
        logger.info("Nuevo emitter suscripto. Total emitters activos: " + emitters.size());

        emitter.onCompletion(() -> {
            emitters.remove(emitter);
            logger.info("Emitter completado y removido. Total emitters activos: " + emitters.size());
        });
        emitter.onTimeout(() -> {
            emitters.remove(emitter);
            logger.warning("Emitter en timeout y removido. Total emitters activos: " + emitters.size());
        });
        emitter.onError((e) -> {
            emitters.remove(emitter);
            logger.log(Level.WARNING, "Emitter en error y removido. Total emitters activos: " + emitters.size(), e);
        });

        try {
            // esto fuerza el commit de la respuesta -> dispara onopen en el navegador
            emitter.send(SseEmitter.event()
                    .comment("connected"));
            logger.info("Comentario 'connected' enviado para forzar el flush inicial");
        } catch (IOException e) {
            logger.log(Level.SEVERE, "Error al enviar el evento inicial 'connected'", e);
            emitter.completeWithError(e);
        }

        return emitter;
    }

    public void broadcast(SectorBatchDTO batch) {
        logger.info("Iniciando broadcast a " + emitters.size() + " emitter(s)");

        List<SseEmitter> deadEmitters = new ArrayList<>();

        for (SseEmitter emitter : emitters) {
            try {
                emitter.send(SseEmitter.event()
                        .name("sector-batch")
                        .data(batch));
                logger.fine("Evento sector-batch enviado a un emitter");
            } catch (IOException e) {
                logger.log(Level.WARNING,
                        "Cliente SSE desconectado o socket cerrado. Removiendo emitter. Detalle: " + e.getMessage(),
                        e);
                deadEmitters.add(emitter);
                try {
                    emitter.complete();
                } catch (Exception ignored) {
                    // el cliente ya se desconectó; no es necesario hacer más
                }
            }
        }

        emitters.removeAll(deadEmitters);
        logger.info("Broadcast terminado. Emitters removidos: " + deadEmitters.size()
                + " | Emitters activos restantes: " + emitters.size());
    }
}