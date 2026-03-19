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
| **Glama** | [docs/GLAMA.md](docs/GLAMA.md) |

**Meta:** [CONTRIBUTING.md](CONTRIBUTING.md) · [RELEASING.md](RELEASING.md) · [.github/TOPICS.md](.github/TOPICS.md) · [glama.json](glama.json) · [justfile](justfile)

## One-line facts

- **Ports:** API **10768**, UI **10769** ([WEBAPP_PORTS](https://github.com/sandraschi/mcp-central-docs/blob/main/operations/WEBAPP_PORTS.md))
- **MCP tool:** `openmanus_bridge` (`status`, `validate`, `run_prompt` stub)
- **Standards:** [AGENT_PROTOCOLS](https://github.com/sandraschi/mcp-central-docs/blob/main/standards/AGENT_PROTOCOLS.md)

## License

MIT
