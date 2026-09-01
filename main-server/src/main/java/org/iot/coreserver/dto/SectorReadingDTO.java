package org.iot.coreserver.dto;

import java.time.Instant;

public record SectorReadingDTO(
        String deviceId,
        String sensorType,
        double value,
        String unit,
        Instant timestamp
) {}