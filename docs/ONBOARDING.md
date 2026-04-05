# Onboarding Guide: openmanus-mcp

Welcome to the **openmanus-mcp** bridge. This project allows you to control the **OpenManus** AI agent via the Model Context Protocol (MCP) and a modern SOTA dashboard.

> [!IMPORTANT]
> **This is a Bridge**: You MUST have the original [OpenManus](https://github.com/FoundationAgents/OpenManus) repository installed on your machine. This MCP server acts as an interface to that engine.

## 1. Prerequisites
- **Python 3.12+**
- **uv** (recommended for dependency management)
- **OpenManus Repository**: Cloned and configured.

## 2. Standard Setup
1.  **Clone OpenManus**:
    ```powershell
    git clone https://github.com/FoundationAgents/OpenManus.git D:\Dev\repos\OpenManus
    cd D:\Dev\repos\OpenManus
    # Configure your config.toml inside OpenManus (LLM API keys, etc.)
    ```
2.  **Configure openmanus-mcp**:
    -   Create a `.env` file in the `openmanus-mcp` root.
    -   Add `OPENMANUS_ROOT=D:\Dev\repos\OpenManus` (the path to your clone).
3.  **Start the Bridge**:
    ```powershell
    # Option A: Just the Bridge UI (Standard)
    .\web_sota\start.ps1

    # Option B: Bridge UI + OpenManus CLI (Unified Startup)
    .\web_sota\start.ps1 -Engine
    ```

## 3. Unified Startup (Automated Setup)
The `start.ps1 -Engine` switch provides a SOTA experience by:
- Launching the **FastAPI Backend** (10768)
- Launching the **Vite Frontend** (10769)
- Opening a **separate PowerShell window** running the original OpenManus CLI in your `OPENMANUS_ROOT`.
- Automatically detecting your `OPENMANUS_ROOT` from the environment or your `.env` file.


## 3. Frequently Asked Questions
### Q: Do I need to start the OpenManus CLI before starting the MCP server?
**A**: No, it's optional. The bridge manages child processes automatically. However, many users prefer to see the native CLI logs alongside the dashboard. Use `.\web_sota\start.ps1 -Engine` to launch both simultaneously.


### Q: Where are my jobs stored?
**A**: By default, they are persisted in `~/.openmanus-mcp/jobs.json`. You can change this via `OPENMANUS_JOB_STORE_PATH`.

### Q: How do I see logs?
**A**:
-   **Terminal**: Real-time server and bridge logs.
-   **Dashboard**: The "Jobs" and "Output" tabs in the web UI show agent-specific logs.
-   **OpenManus Logs**: Check the `logs/` directory inside your `OPENMANUS_ROOT`.

## 4. Troubleshooting
- **ModuleNotFoundError**: Ensure you ran `uv sync`.
- **Invalid Root**: Verify `OPENMANUS_ROOT` points to a directory containing `main.py`.
- **Port Conflicts**: Use the `-Port` argument in `start.ps1` if 10769 is taken.
