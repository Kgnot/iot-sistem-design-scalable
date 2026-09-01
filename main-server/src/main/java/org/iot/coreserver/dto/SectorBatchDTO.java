package org.iot.coreserver.dto;


import java.util.List;

public record SectorBatchDTO(
        String localityId,
        String localityName,
        String sector,
        List<SectorReadingDTO> readings
) {}