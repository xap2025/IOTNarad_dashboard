import os
from influxdb_client import InfluxDBClient, Point, WritePrecision


def get_client() -> InfluxDBClient:
    url = os.getenv("INFLUXDB_URL", "http://localhost:8086")
    token = os.getenv("INFLUXDB_TOKEN", "token")
    org = os.getenv("INFLUXDB_ORG", "org")
    return InfluxDBClient(url=url, token=token, org=org)


def write_measurement(measurement: str, fields: dict, tags: dict | None = None):
    bucket = os.getenv("INFLUXDB_BUCKET", "telemetry")
    org = os.getenv("INFLUXDB_ORG", "org")
    client = get_client()
    write_api = client.write_api(write_options=None)

    point = Point(measurement)
    if tags:
        for k, v in tags.items():
            point = point.tag(k, v)
    for k, v in fields.items():
        point = point.field(k, v)
    point = point.time(write_precision=WritePrecision.S)
    write_api.write(bucket=bucket, org=org, record=point)

