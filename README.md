<div align="center">

<img src="docs/assets/banner.svg" alt="openmanus-mcp — FastMCP + OpenManus FOSS + MCP server fleet UI" width="92%" />

<br/>

[![Beta](https://img.shields.io/badge/status-beta-yellowgreen?style=flat-square)](./RELEASING.md)
[![CI](https://img.shields.io/github/actions/workflow/status/sandraschi/openmanus-mcp/ci.yml?branch=main&style=flat-square&label=CI)](https://github.com/sandraschi/openmanus-mcp/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue?style=flat-square)](docs/INSTALL.md)
[![FastMCP](https://img.shields.io/badge/FastMCP-3.1%2B-8b5cf6?style=flat-square)](https://github.com/jlowin/fastmcp)
[![License](https://img.shields.io/badge/license-MIT-22c55e?style=flat-square)](LICENSE)
[![Glama](https://img.shields.io/badge/Glama-MCP-0ea5e9?style=flat-square)](https://glama.ai/mcp/servers?query=openmanus)

**Bridge and browser UI for [OpenManus](https://github.com/FoundationAgents/OpenManus)** — the **FOSS** agent, not Manus.im.  
Use your own **Ollama**, **LM Studio**, or other local endpoints; this repo stays out of your wallet by default.

[Install](docs/INSTALL.md) · [Tech](docs/TECH.md) · [Glama](docs/GLAMA.md) · [How we build](docs/HOW_WE_BUILD.md)

</div>

---

> **Beta** — behavior may still shift; pin a **tag** for anything serious → [RELEASING.md](RELEASING.md).

## What you get

### For Humans

**Webapp** to **start and control** tasks: run OpenManus (sync or queued), pick presets and activities, chat with a **local** model, onboard other **MCP servers** into your **fleet**, and skim API help. Getting it running step by step: [INSTALL.md](docs/INSTALL.md).

### For Agents

**MCP** from **Cursor**, **Claude Desktop**, **Glama**, and similar hosts. Implemented with **[FastMCP 3.1+](https://github.com/jlowin/fastmcp)**; tool **`openmanus_bridge`** checks your OpenManus install, runs prompts, and polls async jobs without leaving the editor. Client setup: [INSTALL.md](docs/INSTALL.md) · transport and API shape: [TECH.md](docs/TECH.md).

### MCP server fleet

A **fleet of MCP server repos** (curated siblings): clone and track them from the dashboard — each stays its own project, **not** one giant merged tool namespace. Details: [docs/FLEET.md](docs/FLEET.md).

### Automation (OpenClaw-style)

Optional **supervisor** (interval schedules → background runs), a **connector** catalog (email / robot / media hints), and **skills** (compact skill index + optional full playbooks in chat). Overview: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

### Cost bias

**Zeropaid-first**: local inference and FOSS glue before paid APIs — [docs/HOW_WE_BUILD.md](docs/HOW_WE_BUILD.md).

## Documentation

| | |
|--|--|
| **Index** | [docs/README.md](docs/README.md) |
| **Install** | [docs/INSTALL.md](docs/INSTALL.md) |
| **Architecture & roadmap** | [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) |
| **Supervisor & connectors** | [docs/SUPERVISOR.md](docs/SUPERVISOR.md) |
| **Skills (AgentSkills-style)** | [docs/SKILLS_OPENCLAW.md](docs/SKILLS_OPENCLAW.md) |
| **Manus vs OpenManus** | [docs/MANUS.md](docs/MANUS.md) |
| **Safety** | [docs/SAFETY.md](docs/SAFETY.md) |
| **MCP server fleet (big picture)** | [docs/FLEET_CONTEXT.md](docs/FLEET_CONTEXT.md) |
| **Visual assets** | [docs/assets/README.md](docs/assets/README.md) — *Nano Banana / Veo-style hero + demo when you add files* |

**Meta:** [CONTRIBUTING.md](CONTRIBUTING.md) · [RELEASING.md](RELEASING.md) · [.github/TOPICS.md](.github/TOPICS.md) (topics + **snappy GitHub description**) · [glama.json](glama.json) · [justfile](justfile)

**Visibility / stars (straight talk):** [docs/HOW_WE_BUILD.md#10-honest-visibility-no-growth-hacks](docs/HOW_WE_BUILD.md#10-honest-visibility-no-growth-hacks)

## Authenticity (not “agentslop”)

**MCP ≠ low-effort dump.** Maintainer-owned, **CI-backed**, stubs labeled honestly — see **[docs/REPO_HYGIENE.md](docs/REPO_HYGIENE.md)** (quality bar, spam stance, ecosystem **lament**, **ORB** on roadmap). PRs use **[.github/pull_request_template.md](.github/pull_request_template.md)**.

## Planned / TODO

- **My robots (planned)** — **medium-term** direction:
  - Connect the same agents and **MCP servers** to **hardware you already have** (toy/education rovers, robot vacuums, and down the road more human-like robots)—not just files and APIs.
  - Keep **you in the loop** for anything that could hurt someone or break something; no “surprise, the arm moved.”
  - Support **try-it-in-software-first** (simulation / replay) as a peer to **live** runs, so you rehearse before the real world. Details: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md#roadmap-informal).
- **OpenClaw-class (partially shipped)** — supervisor tick + schedules, connector registry, skills index + chat injection → [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md#openclaw-style-features-shipped--planned)
- **OpenClaw-class (still planned)** — full comms gateway, durable schedule store, lazy skill loading parity, multi-agent orchestration → same section
- **Hierarchical local agents** (arXiv-informed) — PRs welcome
- **ORB** integration — planned; scope TBD → [docs/REPO_HYGIENE.md](docs/REPO_HYGIENE.md#planned-orb-integration) + Issues
- OpenManus **runner** + **Cursor snippets** + **MCP server fleet health** — [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md#roadmap-informal)

## The MCP server fleet pattern

This repo is one of many **MCP + React** projects under **[sandraschi](https://github.com/sandraschi)** — [docs/FLEET_CONTEXT.md](docs/FLEET_CONTEXT.md).

## Who perpetrated this

| Role | Who |
|------|-----|
| **Vibe architect** | [sandraschi](https://github.com/sandraschi) |
| **Implementation detail** | Lotsa LLMs |
| **IDE / agent shell** | [Cursor](https://cursor.com/) |
| **Security** | **Benny** the Schäferhund |
| **Where** | Vienna — **Alsergrund** |
| **Build time (so far)** | Built in **15 mins** (joke!) |

## License

MIT
