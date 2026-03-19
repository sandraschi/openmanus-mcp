# Fleet setup (OpenManus + openmanus-mcp + pywinauto-mcp)

← [Documentation index](README.md)


**openmanus-mcp alone** gives you the bridge MCP server and **this repo’s** webapp (`web_sota`, ports **10768/10769**). It does **not** install Windows UI automation.

For **desktop control** as described in [FLEET_COMPUTER_USE_MCP](https://github.com/sandraschi/mcp-central-docs/blob/main/patterns/FLEET_COMPUTER_USE_MCP.md), you also need **[pywinauto-mcp](https://github.com/sandraschi/pywinauto-mcp)** (separate clone, Windows-only). Register **both** MCP servers in your client (e.g. Cursor).

## What you need

| Piece | Role | Web UI |
|--------|------|--------|
| **openmanus-mcp** (this repo) | MCP wrapper / status / future OpenManus runner | **Yes** — `web_sota` |
| **pywinauto-mcp** | Win32 “finger”: click, type, desktop state | **Not in upstream today** — MCP stdio only; if a webapp is added later, run its `start.ps1` / README |
| **OpenManus** (upstream) | Agent + LLM | Upstream’s own UX / CLI |

## Webapp onboarding (RoboFang-style)

With the API and UI running (`.\web_sota\start.ps1`), open **Fleet** in the sidebar. You get a **curated catalog** (`src/openmanus_mcp/data/fleet_catalog.json`): each row has **Onboard** (git clone into `fleet/` + install recipe) and **Start webapp** when the catalog entry defines a PowerShell script (none of the default rows ship a web UI yet; extend the JSON to add `webapp` for repos that have `web_sota/start.ps1`).

State file: `fleet/.fleet_state.json` (gitignored with the rest of `fleet/*` except `.gitkeep`).

REST (same as the UI uses):

- `GET /api/v1/fleet/catalog`
- `GET /api/v1/fleet/members`
- `POST /api/v1/fleet/onboard` body `{ "member_ids": ["pywinauto-mcp"] }`
- `POST /api/v1/fleet/webapp/start` body `{ "member_id": "..." }` (Windows, new console)

Override clone root: env **`OPENMANUS_FLEET_ROOT`** (see `.env.example`).

## Automate (Windows)

From the **root of this repo**:

```powershell
.\scripts\Bootstrap-Fleet.ps1
```

Optional:

- `-SiblingRoot <path>` — folder where `pywinauto-mcp` should live as a **sibling** of this repo (default: parent of this repo).
- `-SkipNpm` — do not run `npm install` in `web_sota`.
- `-SkipPyWinAuto` — only refresh **openmanus-mcp** (`uv sync`) and npm; assume pywinauto-mcp already cloned.
- `-Face` — install pywinauto-mcp with optional face-recognition extra (heavier; may need build tools).

The script will:

1. `git clone` **pywinauto-mcp** next to this repo if missing.
2. Create **pywinauto-mcp** `.venv` and `uv pip install -e .` (or `-e ".[face]"` with `-Face`).
3. `uv sync --extra dev` here; `npm install` in `web_sota` unless `-SkipNpm`.
4. Write **`examples/cursor-fleet.generated.json`** (gitignored) with **absolute** `cwd` paths for Cursor — merge into your MCP config.

## Manual (same outcome)

1. Clone [pywinauto-mcp](https://github.com/sandraschi/pywinauto-mcp) (any path).
2. Follow its README: venv + `pip install -e .` (or `uv venv` + `uv pip install -e .`).
3. In Cursor, add **two** servers: one for this repo (`uv run python -m openmanus_mcp`), one for pywinauto (`python -m pywinauto_mcp` with `cwd` = pywinauto-mcp root, ideally using that repo’s `.venv\Scripts\python.exe`).
4. Start **this** dashboard: `.\web_sota\start.ps1`.

Template with placeholders (no machine paths): **`examples/cursor-fleet.template.json`**.

## OpenManus `config/mcp.example.json`

Upstream OpenManus ships [mcp.example.json](https://github.com/FoundationAgents/OpenManus/blob/main/config/mcp.example.json) (SSE-style sample). How subprocess MCPs attach to the **Manus** runtime can change between releases — treat that file + OpenManus docs as source of truth for **in-OpenManus** wiring. **Cursor** wiring is independent: use the generated or template JSON above.

## Safety

High risk — VMs, allowlists, human confirmation. See **[SAFETY.md](SAFETY.md)** and the central [FLEET_COMPUTER_USE_MCP](https://github.com/sandraschi/mcp-central-docs/blob/main/patterns/FLEET_COMPUTER_USE_MCP.md) pattern.

← [Documentation index](README.md)
