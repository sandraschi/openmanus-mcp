# Architecture and workflows

## High-level components

```text
┌─────────────────┐     stdio      ┌──────────────────┐
│  MCP client     │◄──────────────►│  openmanus_mcp   │
│  (Cursor, etc.)  │                │  FastMCP server  │
└─────────────────┘                └────────┬─────────┘
                                          │
                     ┌────────────────────┼────────────────────┐
                     │                    │                    │
                     ▼                    ▼                    ▼
            ┌──────────────┐    ┌─────────────────┐   ┌──────────────┐
            │  .env /      │    │  FastAPI        │   │  Future:     │
            │  OPENMANUS_  │    │  :10768         │   │  subprocess  │
            │  ROOT probe  │    │  /api/v1/*      │   │  OpenManus   │
            └──────────────┘    └────────┬────────┘   └──────────────┘
                                         │ HTTP (proxy /api)
                                         ▼
                                ┌─────────────────┐
                                │  Vite React     │
                                │  :10769         │
                                │  Dashboard+Fleet│
                                └─────────────────┘
```

## Request flows

1. **MCP tool call** — Client sends JSON-RPC over stdio → **`openmanus_bridge`** → reads **settings** / **`describe_openmanus`** → returns structured dict (success / errors / timings).
2. **Dashboard** — Browser loads UI from **10769**; XHR to **`/api/v1/*`** proxied to **10768**.
3. **Fleet onboard** — UI or POST **`/api/v1/fleet/onboard`** → **`fleet/service`**: `git clone` / `pull` under **`fleet/`** (or **`OPENMANUS_FLEET_ROOT`**), optional **`uv`** install recipe → **`.fleet_state.json`**.

## Data on disk

| Path | Role |
|------|------|
| **`fleet/`** | Cloned member repos (default layout); gitignored except **`.gitkeep`** |
| **`fleet/.fleet_state.json`** | Onboard metadata + install logs (gitignored) |
| **`src/openmanus_mcp/data/fleet_catalog.json`** | Curated catalog (versioned) |

## Composable fleet (desktop-class use)

For **Win32 automation**, agents typically combine **OpenManus** (reasoning) + **pywinauto-mcp** (UI actions) + optional OCR / ops MCPs. This repo **onboards** some of those clones but does **not** merge their tool namespaces into one process. See [FLEET.md](FLEET.md) and [SAFETY.md](SAFETY.md).

## Roadmap (informal)

- **Subprocess runner** for upstream OpenManus with streaming logs into the webapp.
- **Cursor snippet generation** from onboarded `fleet/` paths.
- Stronger **health** aggregation across fleet members (optional).

← [Documentation index](README.md) · [TECH.md](TECH.md)
