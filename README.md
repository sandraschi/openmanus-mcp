# openmanus-mcp

**FastMCP 3.1** MCP server + **SOTA webapp** wrapping **[OpenManus](https://github.com/FoundationAgents/OpenManus)** (FOSS CLI, **100% local LLM** when you configure Ollama / LM Studio in OpenManus). Not Manus.im.

| Item | Value |
|------|--------|
| **Python** | 3.12+ |
| **Framework** | FastMCP 3.1+, FastAPI, Vite + React |
| **Webapp ports** | Backend **10768**, frontend **10769** ([WEBAPP_PORTS](https://github.com/sandraschi/mcp-central-docs/blob/main/operations/WEBAPP_PORTS.md)) |
| **Standards** | [mcp-central-docs / AGENT_PROTOCOLS](https://github.com/sandraschi/mcp-central-docs/blob/main/standards/AGENT_PROTOCOLS.md) |

**GitHub topics:** `manus` `openmanus` `mcp` `ollama` `local-llm` `zeropaid` `fuckzuck` `cli-wrapper` — set under repo **Settings → General → Topics**, or see [.github/TOPICS.md](.github/TOPICS.md) for a `gh repo edit` one-liner.

## Status

**v0.1.0 scaffold** — MCP tool `openmanus_bridge` (`status`, `validate`, `run_prompt` stub), FastAPI health/status, web shell. Subprocess runner + streaming UI next.

## Quick start

```powershell
cd D:\Dev\repos\openmanus-mcp
Copy-Item .env.example .env
# Edit .env: OPENMANUS_ROOT=D:\Dev\repos\OpenManus
uv sync
uv run pytest
uv run python -m openmanus_mcp
```

### Cursor / MCP client

```json
{
  "mcpServers": {
    "openmanus-mcp": {
      "command": "uv",
      "args": ["run", "python", "-m", "openmanus_mcp"],
      "cwd": "D:\\Dev\\repos\\openmanus-mcp"
    }
  }
}
```

Set `OPENMANUS_ROOT` in the environment or `.env` in the repo root (uv loads cwd).

### Webapp

```powershell
cd D:\Dev\repos\openmanus-mcp\web_sota
npm install
cd ..
.\web_sota\start.ps1
```

- UI: <http://127.0.0.1:10769>  
- API: <http://127.0.0.1:10768/api/v1/health>

## MCP tools

| Tool | Purpose |
|------|---------|
| `openmanus_bridge` | `operation=status` \| `validate` \| `run_prompt` (stub) |

## Repo layout

```
src/openmanus_mcp/   # FastMCP server + FastAPI
web_sota/            # Vite React dashboard
tests/
```

## Fleet: “My Computer”–class desktop control

Vendor desktop agents are one bundle; **our** approach is **composable MCP**: run **OpenManus** with **`config/mcp.json`** attaching **[pywinauto-mcp](https://github.com/sandraschi/pywinauto-mcp)** (Win32 click/type/scrape) plus OCR / Windows-ops servers as needed. **High risk** — use VMs, allowlists, and human gates. Architecture write-up: [mcp-central-docs — FLEET_COMPUTER_USE_MCP.md](https://github.com/sandraschi/mcp-central-docs/blob/main/patterns/FLEET_COMPUTER_USE_MCP.md).

## License

MIT
