# Manus vs OpenManus vs openmanus-mcp

Three different things share similar names. This page disambiguates them.

## Manus.im (vendor)

**Manus.im** is a **commercial** product and brand: hosted “agent” / computer-use style experiences, vendor-controlled infrastructure, and **not** what this repository implements or endorses.

- Do **not** assume this MCP server talks to Manus.im APIs.
- This repo’s GitHub topics include critique/humor tags; they refer to **ecosystem positioning**, not an integration with that vendor.

## OpenManus (FOSS)

**[OpenManus](https://github.com/FoundationAgents/OpenManus)** is an **open-source** project (FoundationAgents) — a CLI/agent codebase you run yourself, including with **local LLMs** (Ollama, LM Studio, etc.) via upstream `config.toml`.

- **Not** the same codebase as Manus.im.
- **openmanus-mcp** is a **separate** wrapper: MCP + web UI around *your* OpenManus checkout.

## openmanus-mcp (this repo)

**openmanus-mcp** adds:

- A **FastMCP 3.1** server (`openmanus_bridge`, stdio)
- A **FastAPI** + **Vite** dashboard (ports **10768/10769**)
- **Fleet onboarding** (curated clones under `fleet/`)

It does **not** replace OpenManus; it complements it. See [OPENMANUS.md](OPENMANUS.md) and [INSTALL.md](INSTALL.md).

## Naming in docs and issues

| Term | Meaning |
|------|---------|
| **Manus** (generic) | Ambiguous — prefer **Manus.im** or **OpenManus** |
| **OpenManus** | Upstream FOSS repo |
| **openmanus-mcp** | This MCP + webapp project |

← [Documentation index](README.md)
