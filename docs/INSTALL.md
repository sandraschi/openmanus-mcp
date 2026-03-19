# Install

## Requirements

- **Python 3.12+**
- **[uv](https://docs.astral.sh/uv/)** on `PATH`
- **Node.js + npm** for the dashboard (optional if you only run MCP stdio)
- **Git** (for fleet onboarding / clones)

## 1. Clone and Python env

```powershell
git clone https://github.com/sandraschi/openmanus-mcp.git
cd openmanus-mcp
Copy-Item .env.example .env
```

Edit **`.env`**: set **`OPENMANUS_ROOT`** to your [OpenManus](https://github.com/FoundationAgents/OpenManus) clone (see [OPENMANUS.md](OPENMANUS.md)). Optional: **`OPENMANUS_FLEET_ROOT`** for fleet clones (see [FLEET.md](FLEET.md)).

```powershell
uv sync --extra dev
uv run pytest
```

## 2. MCP client (Cursor, etc.)

Use an **absolute** `cwd` to this repo (Cursor on Windows often mishandles `~`):

```json
{
  "mcpServers": {
    "openmanus-mcp": {
      "command": "uv",
      "args": ["run", "python", "-m", "openmanus_mcp"],
      "cwd": "C:/absolute/path/to/openmanus-mcp"
    }
  }
}
```

`uv` loads **`.env`** from the project directory. You can also set **`OPENMANUS_ROOT`** in the client environment.

**Glama:** see [GLAMA.md](GLAMA.md) and root **`glama.json`**.

## 3. Webapp + API (dashboard)

From **repository root**:

```powershell
Set-Location .\web_sota
npm install
Set-Location ..
.\web_sota\start.ps1
```

Or **`just start-web`** if you use [just](../justfile).

- **UI:** <http://127.0.0.1:10769> (sidebar **Fleet** for curated onboarding)
- **API:** <http://127.0.0.1:10768/api/v1/health>

Ports are fixed to **10768** / **10769** per [WEBAPP_PORTS](https://github.com/sandraschi/mcp-central-docs/blob/main/operations/WEBAPP_PORTS.md).

## 4. Optional: fleet bootstrap (Windows)

Scripted sibling clone + Cursor snippet: **`scripts/Bootstrap-Fleet.ps1`** — [FLEET.md](FLEET.md).

## Verify

- MCP: client shows server and tool **`openmanus_bridge`**
- API: `GET /api/v1/health` returns `ok: true`
- Next: [TECH.md](TECH.md) · [ARCHITECTURE.md](ARCHITECTURE.md)

← [Documentation index](README.md)
