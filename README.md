# IOTNarad_dashboard

Dockerized starter for a universal IoT dashboard using Flask + Plotly Dash + Flask‑SocketIO, Mosquitto MQTT, and InfluxDB v2.

## Prerequisites
- Docker Desktop (WSL2 enabled on Windows)

## First run
1. Create env file
   - Copy `.env.example` to `.env`
   - Edit `.env` and set at least: `FLASK_SECRET_KEY`, `INFLUXDB_TOKEN`, `INFLUXDB_ORG`, `INFLUXDB_BUCKET`
2. Start services
   - `docker compose up --build`
3. Open the app: `http://localhost:8050`

## MQTT quick test
Publish a message to see it in the dashboard:

```
docker exec -it iotnarad_mqtt sh -c 'mosquitto_pub -h localhost -p 1883 -t devices/test/uplink -m "{\"temp\":25}"'
```

You should see the payload appear under "Live MQTT messages".

## Layout
- `app/` Flask server, Dash pages and services
- `infra/mosquitto/` Mosquitto config (1883 + WebSocket 9001)
- `infra/influxdb/` Optional notes/config for InfluxDB v2

## Dev tips
- Rebuild after code changes: `docker compose up --build`
- View logs: `docker compose logs -f app`
- `.env` is ignored by Git; only commit `.env.example`.

## Next steps
- Replace dummy login with real authentication
- Add device configuration UI and persist to DB
- Ingest MQTT payloads into InfluxDB using `app/services/influx.py`
- Build customizable charts per-tenant/theme with Plotly Dash
