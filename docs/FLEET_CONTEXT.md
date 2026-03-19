# The sandraschi MCP server fleet (context)

← [Documentation index](README.md)

## What it is

Over the **last few months**, **[sandraschi](https://github.com/sandraschi)** on GitHub has accumulated a **fleet of MCP servers** — mostly **small, focused repos** that wrap a domain (Resolve, email, OCR, robotics, social VR, world models, OpenManus, …) behind **Model Context Protocol** tools. Much of that work lived **very private** for a long stretch: **low star count, little chatter**, easy for “all and sundry” to **ignore** even when the underlying ideas were sharp.

This document is **not** a full inventory (that changes weekly). It explains **why the pattern matters**.

## MCP server + React webapp

The combo that keeps repeating is:

1. **MCP server** (usually **FastMCP 3.x**, stdio) — agents in Cursor, Claude, Glama, etc. get **structured tools** and conversational returns.
2. **React + Vite “SOTA” webapp** + **FastAPI** (or similar) on **registered high ports** — humans get **health, status, onboarding, logs, and fleet-ish UX** without spelunking Python or JSON-RPC.

That **dual surface** turns repos that would otherwise feel like **obscure CLI utilities** into something **browsable and demoable**. Same codebase feeds **IDE agents** and **a tab in the browser**.

## Why some repos suddenly look interesting

Many upstreams are already **innovative** but **hard to approach** (build matrix, hardware, niche communities). A thin MCP layer plus a **glassmorphism** dashboard lowers the “first success” bar:

| Area | Example directions (illustrative) |
|------|-------------------------------------|
| **Agents / local LLM** | [OpenManus](https://github.com/FoundationAgents/OpenManus) — FOSS “Manus-class” workflows; **openmanus-mcp** is the bridge + UI here. |
| **Robotics** | Yahboom-class rovers, sim vs real — MCP as the **policy boundary** between LLM and hardware. |
| **Social VR** | **Resonite** — rich scene / ProtoFlux surface; MCP as **remote hands** for creators who live in-ID. |
| **World / scene models** | **World Labs**-style stacks — MCP as **inspect + control** for heavy pipelines. |

None of that **requires** hype; it requires **repeatable install, ports, and one obvious URL**.

## Relation to “fleet” inside openmanus-mcp

This repo’s **[FLEET.md](FLEET.md)** onboarding (clone curated members under `fleet/`) is a **microcosm** of the same idea: **compose** many MCP-capable repos on disk, wire them in the client, optionally start their webapps. The **bigger fleet** is the whole **sandraschi** constellation on GitHub — public, private, and in-between — built as a **personal toolchain** that happens to be **publishable**.

## Tone

Self-deprecating truth: **ignored ≠ worthless**. The fleet was built for **real use** (Vienna keyboard, Benny-approved perimeter), not for leaderboard farming. If a repo ships **MCP + React**, it’s probably meant to be **used**, not just starred.

← [README.md](../README.md) · [FLEET.md](FLEET.md) · [ARCHITECTURE.md](ARCHITECTURE.md)
