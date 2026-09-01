import os

from dataclasses import dataclass


@dataclass
class InfluxConfig:
    url: str = os.getenv("INFLUX_URL", "http://localhost:8086")
    token: str = os.getenv("INFLUX_TOKEN", "")
    org: str = os.getenv("INFLUX_ORG", "")
    bucket: str = os.getenv("INFLUX_BUCKET", "telemetry")
