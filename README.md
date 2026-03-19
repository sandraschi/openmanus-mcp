<div align="center">

<img src="docs/assets/banner.svg" alt="openmanus-mcp — FastMCP + OpenManus FOSS + fleet UI" width="92%" />

<br/>

[![Beta](https://img.shields.io/badge/status-beta-yellowgreen?style=flat-square)](./RELEASING.md)
[![CI](https://img.shields.io/github/actions/workflow/status/sandraschi/openmanus-mcp/ci.yml?branch=main&style=flat-square&label=CI)](https://github.com/sandraschi/openmanus-mcp/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue?style=flat-square)](docs/INSTALL.md)
[![FastMCP](https://img.shields.io/badge/FastMCP-3.1%2B-8b5cf6?style=flat-square)](https://github.com/jlowin/fastmcp)
[![License](https://img.shields.io/badge/license-MIT-22c55e?style=flat-square)](LICENSE)
[![Glama](https://img.shields.io/badge/Glama-MCP-0ea5e9?style=flat-square)](https://glama.ai/mcp/servers?query=openmanus)

**MCP server + local dashboard for [OpenManus](https://github.com/FoundationAgents/OpenManus) (FOSS).**  
Local LLM via upstream config (**Ollama**, **LM Studio**, …). **Not** Manus.im.

[Install](docs/INSTALL.md) · [Tech](docs/TECH.md) · [Glama](docs/GLAMA.md) · [How we build](docs/HOW_WE_BUILD.md)

</div>

---

> **Beta** — behavior may still shift; pin a **tag** for anything serious → [RELEASING.md](RELEASING.md).

## Why this exists

| | |
|--:|--|
| **Agents** | `openmanus_bridge` over **stdio** (Cursor, Claude, Glama, …) |
| **Humans** | **Vite** dashboard **:10769** + **FastAPI** **:10768** |
| **Fleet** | Onboard curated MCP repos from the UI → [docs/FLEET.md](docs/FLEET.md) |
| **OpenClaw-class** | **Supervisor** (interval schedules → async runs), **connector** catalog, **skills** (compact index + optional full `SKILL.md` in chat) → [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) |
| **Money** | **Zeropaid**-biased; local inference first → [docs/HOW_WE_BUILD.md](docs/HOW_WE_BUILD.md) |

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
| **Fleet (big picture)** | [docs/FLEET_CONTEXT.md](docs/FLEET_CONTEXT.md) |
| **Visual assets** | [docs/assets/README.md](docs/assets/README.md) — *Nano Banana / Veo-style hero + demo when you add files* |

**Meta:** [CONTRIBUTING.md](CONTRIBUTING.md) · [RELEASING.md](RELEASING.md) · [.github/TOPICS.md](.github/TOPICS.md) (topics + **snappy GitHub description**) · [glama.json](glama.json) · [justfile](justfile)

## Honest visibility (no growth hacks)

**Lighthouse:** stories like **OpenClaw / OpenFang → huge stars** are **not** reproducible by README edits alone. **1k stars** *is* doable with **shipping + one good loop** of attention.

What actually moves the needle (all **legit**):

1. **30s demo** — screen recording or GIF: MCP tool call + dashboard + Fleet row. Drop under [docs/assets/](docs/assets/README.md) (*Nano Banana stills / **Veo** clip optional but nice.*)
2. **GitHub Topics** — use the **full 20** from [.github/TOPICS.md](.github/TOPICS.md) so searchers find you.
3. **Snappy “About” description** — paste the one-liner from TOPICS.md (search + social cards).
4. **One** high-signal post (e.g. Show HN, r/LocalLLaMA, X) when the demo is ready — **spamming** hurts.
5. **Glama** + **`glama.json`** — registry discovery for MCP users.
6. **Respond** to first issues fast — that’s how early adopters star.

We’re not chasing **100k** here; we’re building a **credible on-ramp** to OpenManus + MCP + UI.

## Authenticity (not “agentslop”)

**MCP ≠ low-effort dump.** Maintainer-owned, **CI-backed**, stubs labeled honestly — see **[docs/REPO_HYGIENE.md](docs/REPO_HYGIENE.md)** (quality bar, spam stance, ecosystem **lament**, **ORB** on roadmap). PRs use **[.github/pull_request_template.md](.github/pull_request_template.md)**.

## Planned / TODO

- **My robots** — toy rovers → robot hoovers → humanoids; virtual ∥ real → [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md#roadmap-informal)
- **OpenClaw-class (partially shipped)** — supervisor tick + schedules, connector registry, skills index + chat injection → [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md#openclaw-style-features-shipped--planned)
- **OpenClaw-class (still planned)** — full comms gateway, durable schedule store, lazy skill loading parity, multi-agent orchestration → same section
- **Hierarchical local agents** (arXiv-informed) — PRs welcome
- **ORB** integration — planned; scope TBD → [docs/REPO_HYGIENE.md](docs/REPO_HYGIENE.md#planned-orb-integration) + Issues
- OpenManus **runner** + **Cursor snippets** + fleet **health** — [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md#roadmap-informal)

## The MCP fleet pattern

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
