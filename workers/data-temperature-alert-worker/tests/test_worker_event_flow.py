from datetime import datetime, timezone

from config.worker_config import SectorWorkerConfig
from schemas.events import TelemetryEvent, deserialize_event
from sector_batch_buffer import SectorBatchBuffer


def test_worker_routing_pattern_matches_telemetry_key():
    cfg = SectorWorkerConfig()
    event = TelemetryEvent(
        device_id="esp32-c6-001",
        device_type="esp32-c6-mini",
        timestamp=datetime.now(timezone.utc),
        locality_id="18",
        sector="marruecos-1",
        sensor_type="temperature",
        value=20.7,
        unit="C",
        locality_name="Rafael Uribe Uribe",
    )

    assert cfg.routing_patterns == ["telemetry.#"]
    assert event.routing_key.startswith("telemetry.")
    assert event.routing_key.count(".") >= 3


def test_deserialize_event_accepts_sensor_type_and_locality_name():
    raw = (
        b'{"event_id":"evt-1","device_id":"esp32-c6-001","device_type":"esp32-c6-mini",'
        b'"timestamp":"2026-08-31T00:00:00+00:00","locality_id":"18","sector":"marruecos-1",'
        b'"category":"telemetry","sensor_type":"temperature","value":20.7,"unit":"C",'
        b'"locality_name":"Rafael Uribe Uribe"}'
    )

    event = deserialize_event(raw)

    assert isinstance(event, TelemetryEvent)
    assert event.sensor_type.value == "temperature"
    assert event.locality_name == "Rafael Uribe Uribe"


def test_sector_batch_buffer_builds_batch_when_limit_reached():
    buffer = SectorBatchBuffer(batch_size=2)

    event_1 = TelemetryEvent(
        device_id="esp32-c6-001",
        device_type="esp32-c6-mini",
        timestamp=datetime.now(timezone.utc),
        locality_id="18",
        sector="marruecos-1",
        sensor_type="temperature",
        value=20.7,
        unit="C",
        locality_name="Rafael Uribe Uribe",
    )
    event_2 = TelemetryEvent(
        device_id="esp32-c6-002",
        device_type="esp32-c6-mini",
        timestamp=datetime.now(timezone.utc),
        locality_id="18",
        sector="marruecos-1",
        sensor_type="temperature",
        value=21.2,
        unit="C",
        locality_name="Rafael Uribe Uribe",
    )

    assert buffer.add(event_1) is None
    batch = buffer.add(event_2)

    assert batch is not None
    assert len(batch) == 2
    assert batch[0].locality_id == "18"
