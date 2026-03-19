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

For **Win32 automation**, agents typically combine **OpenManus** (reasoning) + **pywinauto-mcp** (UI actions) + optional OCR / ops MCPs. This repo **onboards** some of those clones but does **not** merge their tool namespaces into one process. See [FLEET.md](FLEET.md) and [SAFETY.md](SAFETY.md). Bigger picture (sandraschi repos, months of MCP + React work): [FLEET_CONTEXT.md](FLEET_CONTEXT.md).

## Roadmap (informal)

- **My robots (planned)** — **“My robots”** functions spanning the stack: **Yahboom**-style toy / edu robocars, **Dreame** / **Xiaomi** robot hoovers (and similar LDS/VSLAM vacuums), **Noetix** / **Bumi**-style Android humanoids, etc. Design goals:
  - **Parallel tracks:** **virtual bots** (simulation, replay, CI sandboxes, “digital twin” state) and **real bots** (live hardware, rate limits, estop) with explicit mode switching and shared task schemas where safe.
  - **Same agent surface:** OpenManus + MCP fleet can target either track; physical actions require **hard gates** (human confirm, geofence, power/state checks) — see [SAFETY.md](SAFETY.md).
  - **Integration shape:** likely via dedicated MCP servers (e.g. existing **yahboom-mcp** patterns in your ecosystem) and dashboard **fleet** rows for robot classes, not a single monolithic driver in this repo.
- **Subprocess runner** for upstream OpenManus with streaming logs into the webapp.
- **Cursor snippet generation** from onboarded `fleet/` paths.
- Stronger **health** aggregation across fleet members (optional).

## OpenClaw OpenFang and hierarchical agents (planned)

**Stepwise** adoption — no big-bang rewrite. Names align with ecosystem usage elsewhere (e.g. **OpenClaw** as *comms / message-routing* idioms, **OpenFang** as *hand + skill bundle* idioms).

| Phase | Focus | Notes |
|-------|--------|--------|
| **1 — Heartbeat** | **Liveness** for this API, onboarded `fleet/` members, and (later) attached MCP processes | Timestamps, `/api/v1/health` depth, optional push to UI badges |
| **2 — Comms connectors** | **OpenClaw-class** patterns: **routing** notifications and events over **connectors** (chat, email, webhooks — whatever we standardize) without turning this repo into a full gateway | Start read-only or outbound-only; [SAFETY.md](SAFETY.md) for abuse model |
| **3 — Skill integration** | **FastMCP 3.x** skills/resources where they fit; optional import of **[OpenFang](https://github.com/RightNow-AI/openfang)**-style **`HAND.toml` / `SKILL.md`** bundles as *documented* adapters (same separation idea as RoboFang’s OpenFang adapter — mapping layer, not silent merge) | Version manifests; no skill name collisions with `openmanus_bridge` |
| **4 — Multi-agentic** | **Multiple agents** sharing context: planner + executor + critic, or **parallel** task branches with merge policy | Prefer **local** orchestration; optional bridge to a hub (e.g. RoboFang-style) later |

### Hierarchical local agent fleet (arXiv-informed)

Goal: a **tree or DAG of local agents** (orchestrator → specialists → tools) inspired by **recent** multi-agent / hierarchical RL / routing papers on arXiv — without committing to one architecture in v0.1.

**Design knobs (suggestions welcome):**

- **Router vs fixed tree:** dynamic **specialist spawn** vs static **role graph**.
- **Shared memory:** what lives in **OpenManus** vs **this** API vs **external** MCP memory servers.
- **Budgets:** token, wall-clock, and **tool-call** caps per subtree.
- **Audit:** structured log of **who delegated to whom** (deliberation-style), exportable for debugging.

**Contributing:** open an issue with **arXiv ID + one paragraph** on how it maps to local MCP; we’ll curate a short **reading list** in this section as ideas land.

← [Documentation index](README.md) · [TECH.md](TECH.md)
