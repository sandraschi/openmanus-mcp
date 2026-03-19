# openmanus-mcp

![Alpha](https://img.shields.io/badge/status-alpha-orange)
[![CI](https://github.com/sandraschi/openmanus-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/sandraschi/openmanus-mcp/actions/workflows/ci.yml)

**FastMCP 3.1** MCP server + **local dashboard** for **[OpenManus](https://github.com/FoundationAgents/OpenManus)** (FOSS agent, **local LLM**-friendly). **Not** Manus.im.

> **Alpha** — APIs and tools may change. Pin a tag for anything serious; see [RELEASING.md](RELEASING.md).

**Quick install:** [docs/INSTALL.md](docs/INSTALL.md)

## Documentation (staggered / linked)

| | |
|--|--|
| **Index** | [docs/README.md](docs/README.md) — full map |
| **Install** | [docs/INSTALL.md](docs/INSTALL.md) |
| **Technical** | [docs/TECH.md](docs/TECH.md) |
| **Manus naming** | [docs/MANUS.md](docs/MANUS.md) — vendor vs FOSS |
| **OpenManus upstream** | [docs/OPENMANUS.md](docs/OPENMANUS.md) |
| **Architecture** | [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) |
| **Safety** | [docs/SAFETY.md](docs/SAFETY.md) |
| **Fleet** | [docs/FLEET.md](docs/FLEET.md) |
| **Fleet (big picture)** | [docs/FLEET_CONTEXT.md](docs/FLEET_CONTEXT.md) — sandraschi MCP constellation, months of work, MCP + React |
| **Glama** | [docs/GLAMA.md](docs/GLAMA.md) |
| **How we build** | [docs/HOW_WE_BUILD.md](docs/HOW_WE_BUILD.md) — vibecoding, agentic IDEs, zeropaid, FOSS trawl, fleet workflow |

**Meta:** [CONTRIBUTING.md](CONTRIBUTING.md) · [RELEASING.md](RELEASING.md) · [.github/TOPICS.md](.github/TOPICS.md) · [glama.json](glama.json) · [justfile](justfile)

## One-line facts

- **Ports:** API **10768**, UI **10769** ([WEBAPP_PORTS](https://github.com/sandraschi/mcp-central-docs/blob/main/operations/WEBAPP_PORTS.md))
- **MCP tool:** `openmanus_bridge` (`status`, `validate`, `run_prompt` stub)
- **Standards:** [AGENT_PROTOCOLS](https://github.com/sandraschi/mcp-central-docs/blob/main/standards/AGENT_PROTOCOLS.md)

## Planned / TODO

- **My robots** — unified “my fleet” affordances from **toy/edu rovers** (e.g. [Yahboom](https://www.yahboom.net/)-class robocars) through **home robots** (e.g. **Dreame** / **Xiaomi** robot hoovers / vacuums) to **humanoids** (e.g. **Noetix** / **Bumi**-class Android-based bots), with **parallel virtual bots** (sim / digital twins) and **real hardware** under the same task and safety model. Details: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md#roadmap-informal).
- **OpenClaw- / OpenFang-class features (stepwise)** — **heartbeat** / liveness, **comms connectors** (routing-style integrations), **skill** surface (MCP skills + [OpenFang](https://github.com/RightNow-AI/openfang)-style `HAND.toml` / `SKILL.md` patterns where we adopt them), **multi-agentic** flows (delegation, parallel workers). See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md#openclaw-openfang-and-hierarchical-agents-planned).
- **Hierarchical local agent fleet** — **orchestrator + specialized workers** on your machine, informed by **recent arXiv-style** multi-agent / routing / tree-of-agents ideas (we’ll link concrete papers in the arch doc as we implement). **Suggestions and PRs welcome.**
- OpenManus **subprocess runner** + streaming logs, **Cursor snippet** generation from `fleet/`, stronger fleet **health** aggregation — see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md#roadmap-informal).

## The MCP server fleet (why this repo fits a pattern)

**openmanus-mcp** sits in a **wider fleet** of MCP servers on **[sandraschi @ GitHub](https://github.com/sandraschi)** — built over the **last few months**, much of it **very private** and **under the radar** (“ignored by all and sundry” is a feature, not a bug). The recurring shape is **MCP server + React webapp** (plus API): that combo makes niche but **innovative** stacks (**OpenManus**, **robotics**, **Resonite**, **World Labs**-class tooling, etc.) **approachable** for both agents and humans. Longer read: **[docs/FLEET_CONTEXT.md](docs/FLEET_CONTEXT.md)**.

## Who perpetrated this

| Role | Who |
|------|-----|
| **Vibe architect** | [sandraschi](https://github.com/sandraschi) |
| **Implementation detail** | Lotsa LLMs |
| **IDE / agent shell** | [Cursor](https://cursor.com/) |
| **Security** | **Benny** the Schäferhund |
| **Where** | Vienna — **Alsergrund** |
| **Build time (so far)** | ~**2 hours**, lunch included |

## License

MIT
