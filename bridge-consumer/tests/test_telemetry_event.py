from schema.events import TelemetryEvent, SensorType


def test_telemetry_event_has_sensor_and_locality_metadata():
    event = TelemetryEvent(
        device_id="esp32-c6-001",
        device_type="esp32-c6-mini",
        sensor_type=SensorType.TEMPERATURE,
        value=20.7,
        unit="C",
        locality_id="18",
        locality_name="Rafael Uribe Uribe",
        sector="marruecos-1",
    )

    assert event.sensor_type == SensorType.TEMPERATURE
    assert event.locality_name == "Rafael Uribe Uribe"
    assert event.routing_key == "telemetry.esp32-c6-001.esp32-c6-mini.temperature"
