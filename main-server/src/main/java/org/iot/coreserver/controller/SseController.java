package org.iot.coreserver.controller;


import org.iot.coreserver.service.SectorEventService;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

@RestController
@CrossOrigin(origins = "*")
public class SseController {

    private final SectorEventService sectorEventService;

    public SseController(SectorEventService sectorEventService) {
        this.sectorEventService = sectorEventService;
    }

    @GetMapping("/api/sectors/stream")
    public SseEmitter stream() {
        return sectorEventService.subscribe();
    }
}