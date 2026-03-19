# Supervisor & connectors (OpenClaw-style spine)

See also [ARCHITECTURE.md](ARCHITECTURE.md#openclaw-style-features-shipped--planned) for how this fits the rest of the API.

Phase-1 **process-local** automation: a background asyncio loop ticks on an interval, evaluates **interval schedules**, and queues **async OpenManus runs** (same job store as `POST /api/v1/run/async`).

## Enable

- `OPENMANUS_SUPERVISOR_ENABLED=true` — start tick loop on API startup.
- `OPENMANUS_SUPERVISOR_TICK_S=30` — seconds between ticks (5–3600).

Default is **off** so tests and dev shells do not spawn background work.

## REST

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/v1/supervisor/heartbeat` | Tick count, uptime, last error, `supervisor_enabled` |
| GET | `/api/v1/supervisor/schedules` | List schedules |
| POST | `/api/v1/supervisor/schedules` | Create (`name`, `interval_s`, `prompt`, `entry_point`, `enabled`, optional `connector_kind`) |
| DELETE | `/api/v1/supervisor/schedules/{id}` | Remove |
| PATCH | `/api/v1/supervisor/schedules/{id}/enabled` | `{"enabled": bool}` |
| GET | `/api/v1/connectors` | Catalog: `email`, `yahboom`, `calibre` (metadata + proactive prompt hints) |
| GET | `/api/v1/connectors/{kind}` | One connector |

Schedules are **in-memory** (lost on restart). `connector_kind` prepends a short hint to the prompt so OpenManus steers toward the right MCP tools when the user has them enabled in the IDE.

## Connectors

No outbound MCP calls from this API: **connectors** document how fleet MCPs (email-mcp, yahboom-mcp, calibre-mcp) align with proactive activities. The Run page includes **comms / robots / media** activities that reference those servers.

## Status

`GET /api/v1/status` includes `supervisor_enabled`, `supervisor_tick_s`, `supervisor_schedules`, and `supervisor_heartbeat`.
