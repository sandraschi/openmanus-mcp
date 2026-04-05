# openmanus-mcp: Process Interface Relay

A high-performance **Model Context Protocol (MCP)** server and **React/SOTA** dashboard for [OpenManus](https://github.com/FoundationAgents/OpenManus).

> [!TIP]
> **System Context**: This is a **Portmanteau Bridge** that manages the subprocess lifecycle, persistent state, and task history for the OpenManus engine.

##  Features
- **FastMCP 3.2.0**: Built on SOTA v1.20 for reliable asynchronous task management.
- **Persistent Jobs**: Agent tasks survive server restarts (`~/.openmanus-mcp/jobs.json`).
- **Ecosystem Ready**: Integrated positioning with Manus, OpenClaw, and Robofang.
- **System Dashboard**: Native monitoring UI for real-time subprocess management.
- **Agentic Prompts**: Native templates for rapid task generation.
- **Sampling Support**: Reasoning via host LLM sampling (SEP-1577).

##  Ecosystem Positioning
OpenManus MCP is part of a broader autonomous agent fleet. Understanding the boundaries between Manus, OpenClaw, and Robofang is critical for production deployment.

- See [**docs/ECOSYSTEM.md**](file:///D:/Dev/repos/openmanus-mcp/docs/ECOSYSTEM.md) for the full architectural map.

##  Quick Start
See the full [**ONBOARDING.md**](file:///D:/Dev/repos/openmanus-mcp/docs/ONBOARDING.md) for detailed setup.

1.  **Configure**: Set `OPENMANUS_ROOT` to your clone of OpenManus.
2.  **Start**:
    ```powershell
    uv sync
    uv run openmanus-mcp
    ```
3.  **Explore**: Open [http://localhost:10769](http://localhost:10769) to see your fleet.

##  The Portmanteau Rationale
In modern AI architecture, tools should be **composable** yet **specialized**. `openmanus-mcp` follows the Portmanteau pattern by providing a single, authoritative `openmanus_bridge` tool that handles:
1.  **Orchestration**: Starting and stopping agent runs.
2.  **Telemetry**: Real-time log and state ingestion.
3.  **Persistence**: Saving and restoring task history.

##  Requirements
-   **Python 3.12+**
-   **uv**
-   **OpenManus Clone** (The core engine)

##  Testing & CI/CD
-   **Local**: `uv run pytest`
-   **Integration**: `uv run pytest --integration` (Runs real agent tasks)
-   **CI**: GitHub Actions with Ruff linting and build verification.

##  Standards & Compliance
-   **SOTA v1.20**
-   **FastMCP 3.2.0**
-   **SEP-1577** (Agentic Workflow Protocol)

---
 2026 Sandra Schi  Alsergrund, Vienna.
[Materialist Reductionism]  [Socialist Infrastructuralism]
