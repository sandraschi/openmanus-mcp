# Architecture and workflows

## High-level components

```text
┌─────────────────┐     stdio      ┌──────────────────┐
│  MCP client     │◄──────────────►│  openmanus_bridge   │
│  (Cursor, etc.)  │                │  FastMCP server  │
└─────────────────┘                └────────┬─────────┘
                                          │
                     ┌────────────────────┼────────────────────┐
                     │                    │                    │
                     ▼                    ▼                    ▼
            ┌──────────────┐    ┌─────────────────┐   ┌──────────────┐
            │  .env /      │    │  FastAPI        │   │  Runner      │
            │  OPENMANUS_  │    │  :10768         │   │  subprocess  │
            │  ROOT probe  │    │  /api/v1/*      │   │  (OpenManus) │
            └──────────────┘    └────────┬────────┘   └──────┬───────┘
                                         │                    │
                                         ▼                    ▼
                                ┌─────────────────┐   ┌──────────────┐
                                │  Vite React     │   │  JobStore    │
                                │  :10769         │   │  (JSON Disk) │
                                │  Dashboard+Fleet│   └──────────────┘
                                └─────────────────┘
```

## 1. Portmanteau Bridge Pattern
In the SOTA Fleet architecture, **openmanus-mcp** acts as a **Portmanteau Bridge**. Instead of merging the OpenManus reasoning engine directly into the MCP process, it wraps it in a managed lifecycle.

- **Isolation**: Crashes in the agent engine do not take down the MCP server.
- **Environment Parity**: The bridge handles different Python environments (venvs) automatically.
- **State Management**: The bridge provides a unified persistence layer for many ephemeral engine runs.

## 2. Persistent JobStore (Disk-Based)
As of v1.2.0, the **JobStore** has transitioned from in-memory FIFO to a **disk-persistent JSON store**.

- **Location**: `%USERPROFILE%/.openmanus-mcp/jobs.json`
- **Concurrency**: State is shared between the **stdio MCP process** and the **FastAPI background worker**.
- **Atomicity**: Incremental writes and state synchronization ensure that background jobs fired via the Dashboard are visible to the MCP client (and vice versa).

### FastAPI subsystems (beyond fleet + run)

| Module / area | Role |
|---------------|------|
| **`supervisor/`** | Optional background tick (`OPENMANUS_SUPERVISOR_ENABLED`): interval **schedules** → queue **async** OpenManus runs via shared limiter + job store |
| **`connectors/`** | Static **catalog** (`email`, `yahboom`, `calibre`) — metadata + proactive prompt hints; **no** outbound MCP from this process |
| **`skills_catalog.py` + `skills/`** | **AgentSkills-style** `SKILL.md` discovery; **compact XML-like index** injected into chat system prompt; optional **full file** inline via `skill_ids` |
| **Adaptive concurrency** | `concurrency.py` — host RAM/GPU-aware cap shared by sync/async runs and supervisor-fired jobs |

Details: [SUPERVISOR.md](SUPERVISOR.md) · [SKILLS_OPENCLAW.md](SKILLS_OPENCLAW.md)

## 3. Tool Hierarchy & Sampling
The bridge leverages **FastMCP 3.2.0** automated workflows to enable cross-agent coordination.

- **Prompts**: Standardized `mcp.prompt()` templates provide **System Context** to the host LLM about how to best leverage OpenManus.
- **Sampling**: The `sampling_relay` tool allows the bridge to delegate complex reasoning *back* to the host LLM (e.g., Cursor or Antigravity) when necessary.
- **Supervisor**: A background tick service that can schedule periodic tasks without human intervention.

## 4. Request flows
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
- **Streaming logs** from the runner into the webapp logger (partial today — poll / copy stdout from REST result).
- **Cursor snippet generation** from onboarded `fleet/` paths.
- **ORB-class integration** (planned): outbound routing / broker or registry layer — design TBD; see [REPO_HYGIENE.md](REPO_HYGIENE.md#planned-orb-integration) and repo Issues when the thread opens.
- Stronger **health** aggregation across fleet members (optional).

## OpenClaw-style features (shipped & planned)

**Stepwise** adoption — no big-bang rewrite. Names align with ecosystem usage (e.g. **OpenClaw** on [docs.openclaw.ai](https://docs.openclaw.ai/)).

### Shipped in this repo (phase-1)

| Area | What works today |
|------|------------------|
| **Liveness** | `GET /api/v1/health`, `GET /api/v1/status` (includes **supervisor** snapshot fields when configured) |
| **Supervisor** | Background **tick** + **interval schedules** → async OpenManus jobs; **in-memory** schedules; opt-in via env |
| **Connectors** | **Registry** only: `GET /api/v1/connectors` — documents email / yahboom / calibre MCP alignment + proactive prompt text |
| **Skills** | Bundled + extra-dir **`SKILL.md`** scan; **compact index** in chat system prompt; **`skill_ids`** for full-body injection; `GET /api/v1/skills` |
| **UI** | **SOTA Chat**: skills toggles; **Run**: activity categories **comms / robots / media** |

### Still planned (heavier OpenClaw / OpenFang parity)

| Phase | Focus | Notes |
|-------|--------|--------|
| **Heartbeat depth** | Fleet member + attached MCP **liveness** beyond this API process | Push to UI badges, optional probes |
| **Comms gateway** | **Routing** notifications/events over real **channels** (not only catalog metadata) | Read-only or outbound-first; [SAFETY.md](SAFETY.md) |
| **Durable schedules** | Persist schedules (disk/DB), cron expressions, backoff | Today: process-local only |
| **Skill loading** | Token-optimized **lazy** load matching upstream OpenClaw evolution | Today: full inline capped by `OPENMANUS_MAX_SKILL_INJECT_CHARS` |
| **FastMCP resources** | Expose skills via MCP **resources** for stdio clients | Optional; avoid name collisions with `openmanus_bridge` |
| **OpenFang-style bundles** | Optional **`HAND.toml` / `SKILL.md`** adapters ([OpenFang](https://github.com/RightNow-AI/openfang)) | Mapping layer, not silent merge |
| **Multi-agentic** | Planner + executor + critic or parallel branches | Prefer **local** orchestration; optional hub later |

### Hierarchical local agent fleet (arXiv-informed)

Goal: a **tree or DAG of local agents** (orchestrator → specialists → tools) inspired by **recent** multi-agent / hierarchical RL / routing papers on arXiv — without committing to one architecture in v0.1.

**Design knobs (suggestions welcome):**

- **Router vs fixed tree:** dynamic **specialist spawn** vs static **role graph**.
- **Shared memory:** what lives in **OpenManus** vs **this** API vs **external** MCP memory servers.
- **Budgets:** token, wall-clock, and **tool-call** caps per subtree.
- **Audit:** structured log of **who delegated to whom** (deliberation-style), exportable for debugging.

**Contributing:** open an issue with **arXiv ID + one paragraph** on how it maps to local MCP; we’ll curate a short **reading list** in this section as ideas land.

← [Documentation index](README.md) · [TECH.md](TECH.md)
