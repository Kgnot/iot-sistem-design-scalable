package org.iot.coreserver.controller;


import org.iot.coreserver.dto.SectorBatchDTO;
import org.iot.coreserver.service.SectorEventService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/sectors")
public class SectorIngestController {

    private final SectorEventService sectorEventService;

    public SectorIngestController(SectorEventService sectorEventService) {
        this.sectorEventService = sectorEventService;
    }

    @PostMapping("/batch")
    public ResponseEntity<Void> receiveBatch(@RequestBody SectorBatchDTO batch) {
        sectorEventService.broadcast(batch);
        return ResponseEntity.accepted().build();
    }
}