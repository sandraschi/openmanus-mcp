# Safety

## Scope

**openmanus-mcp** exposes **local** MCP tools and a **local** web UI. It can **onboard** other repos (fleet) and **launch** PowerShell scripts for their webapps. That increases **blast radius** if you point agents at **production** machines without boundaries.

## Fleet and desktop control

Composable stacks (OpenManus + **pywinauto-mcp** + OCR, etc.) can drive **real keyboards and mice** on **Windows**. That is **high risk**:

- Data exfiltration, destructive clicks, privilege abuse, and **social engineering at machine speed** are all in scope for a capable agent.
- **Do not** treat “local LLM” as “safe LLM” — the model can still choose harmful tool use.

**Mitigations (minimum):**

- Prefer **VMs** or **dedicated sacrificial hosts** for experimentation.
- Use **allowlists** (which apps, which directories) and **human confirmation** for irreversible actions.
- Keep **secrets** out of prompts and logs; assume **screenshots** and **clipboard** are readable by tools.

## Central pattern doc

Architecture and philosophy: **[FLEET_COMPUTER_USE_MCP](https://github.com/sandraschi/mcp-central-docs/blob/main/patterns/FLEET_COMPUTER_USE_MCP.md)** (mcp-central-docs).

## This repo’s surface

| Feature | Risk note |
|---------|-----------|
| **`openmanus_bridge`** | Information disclosure about paths; future `run_prompt` executes upstream code |
| **Fleet onboard** | Runs **`git`** and **`uv`** against user-chosen disk locations |
| **Webapp start** | Spawns **PowerShell** in a new console with **member-defined** scripts |
| **Dashboard** | Localhost-only by default; do not expose **10768/10769** to untrusted networks |

## Reporting

Security issues: use **[GitHub Security](https://github.com/sandraschi/openmanus-mcp/security)** / maintainer contact per **[SECURITY.md](../SECURITY.md)** if present.

← [Documentation index](README.md) · [MANUS.md](MANUS.md)
