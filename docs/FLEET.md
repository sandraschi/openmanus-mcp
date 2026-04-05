# Fleet Coordination

## SOTA Fleet v1.20 Standard
The **OpenManus Fleet** is a collection of interoperable MCP servers designed for local agent automation. This bridge (**openmanus-mcp**) provides the **Portmanteau Coordination Layer**.

## Onboarding Membership
Onboarding a fleet member (e.g. `pywinauto-mcp`) adds it to the bridge via:
- **Registry**: Tracks member clones in `fleet/`.
- **Environment**: Manages member-specific **uv** environments.
- **WebApp Link**: Provides "Start Dashboard" access for each member via the bridge UI.

## Integration Archetype

| Feature | Bridge Integration |
|---------|-------------------|
| **Tools** | Member tools are called by the reasoning engine, not merged into the bridge process. |
| **Liveness** | The bridge polls member **FastAPI /health** endpoints (SOTA port 107xx). |
| **Builds** | Members use the `.mcpb` standard for deployment in the fleet registry. |

## Member Port Registry (2026 SOTA)

| Repo | Port (API) | Port (UI) | Status |
|------|------------|-----------|--------|
| **openmanus-mcp** | **10768** | **10769** | PROD |
| **pywinauto-mcp** | 10770 | 10771 | ALPHA |
| **obs-mcp** | 10772 | 10773 | ALPHA |
| **games-mcp** | 10774 | 10775 | BETA |

## Coordination Workflows

### 1. Cross-Agent Handoff
When OpenManus handles a task involving **pywinauto-mcp**, the bridge:
1. Verifies the member webapp is running.
2. Injects the member tool schema into the OpenManus system prompt.
3. Facilitates tool usage via the **MCP Host (Cursor/Antigravity)**.

### 2. Unified State
Async jobs in the bridge are stored in the **Persistent JobStore**. Fleet members can theoretically subscribe to the `jobs.json` store to react to bridge completions (planned).

## Fleet Onboarding Command
```powershell
# Manual onboarding (if not using the UI)
Invoke-RestMethod -Method POST -Uri "http://127.0.0.1:10768/api/v1/fleet/onboard" -Body (@{
    repo_url = "https://github.com/sandraschi/pywinauto-mcp.git"
    target_path = "D:\Dev\repos\fleet\pywinauto-mcp"
} | ConvertTo-Json)
```

← [Documentation index](README.md) · [TECH.md](TECH.md)
