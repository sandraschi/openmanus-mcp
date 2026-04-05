# Safety

## Scope

**openmanus-mcp** exposes **local** MCP tools and a **local** web UI. It can **onboard** other repos (fleet) and **launch** PowerShell scripts for their webapps. That increases **blast radius** if you point agents at **production** machines without boundaries.

## Fleet and desktop control

Composable stacks (OpenManus + **pywinauto-mcp** + OCR, etc.) can drive **real keyboards and mice** on **Windows**. That is **high risk**:

- Data exfiltration, destructive clicks, privilege abuse, and **social engineering at machine speed** are all in scope for a capable agent.
- **Do not** treat “local LLM” as “safe LLM” — the model can still choose harmful tool use.

## Sampling Security (v1.20)

As of FastMCP 3.2.0, this bridge supports **Sampling** (the bridge asking the host LLM to reason). This creates a "subagent handover" with specific risks:

- **Token Exhaustion**: Recursive sampling can lead to rapid token consumption or context length limits.
- **Prompt Injection**: A compromised subagent prompt could theoretically manipulate the host LLM via sampling responses.
- **Confirmation Bypass**: The host LLM must still ask for permission for destructive subagent actions if the subagent itself doesn't have a human-in-the-loop gate.

**Mitigations (minimum):**

- Keep **secrets** out of prompts and logs; assume **screenshots** and **clipboard** are readable by tools.
- Periodically audit the `jobs.json` file to monitor subagent tool use history.
- Use **allowlists** (which apps, which directories) and **human confirmation** for irreversible actions.
- Prefer **VMs** or **dedicated sacrificial hosts** for experimentation.

## Unified Startup Risks

Using the `.\web_sota\start.ps1 -Engine` switch launches a new, unmanaged PowerShell console running the native OpenManus CLI.

- **Visibility**: This window is visible and persistent (using `-NoExit`). Ensure you monitor it for error loops or runaway tool use.
- **PowerShell Execution**: Ensure your PowerShell ExecutionPolicy allows scripts to run securely before using the automated launcher.

## Reporting

Security issues: use **[GitHub Security](https://github.com/sandraschi/openmanus-mcp/security)** / maintainer contact per **[SECURITY.md](../SECURITY.md)** if present.

← [Documentation index](README.md) · [MANUS.md](MANUS.md)
