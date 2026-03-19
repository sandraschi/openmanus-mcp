# How building this works

← [Documentation index](README.md)

A **meta** guide: how **openmanus-mcp** (and sibling **sandraschi** MCP + webapp repos) tend to get built—not a mandate, a pattern.

## 1. The basics

- **Small, shippable repo:** FastMCP **stdio** server + **FastAPI** + **Vite/React** dashboard on **registered ports** (see [TECH.md](TECH.md), [WEBAPP_PORTS](https://github.com/sandraschi/mcp-central-docs/blob/main/operations/WEBAPP_PORTS.md)).
- **`uv` + Ruff + pytest + CI** so first clone isn’t archaeology.
- **`glama.json`** + docs so Glama/registry and humans can find the thing.
- **Fleet hook:** optional onboarding of other repos under `fleet/` ([FLEET.md](FLEET.md)) or a **new repo** in the constellation ([FLEET_CONTEXT.md](FLEET_CONTEXT.md)).

## 2. Vibecoding — or *agentic architecting*

**Natural-language steering** of codebases (“do the thing, here’s the constraint”) only became **reliably useful for real shipping work** in roughly the **last ~four months** (late 2025 → early 2026): longer context, better tool use, and **agentic** loops that don’t lose the plot on the third file.

That’s **vibecoding** in the cheap seats; call it **agentic architecting** if you want a tie. Same idea: you **describe intent and invariants**, the IDE agent **edits, tests, and refactors**, you **gate** merges. It’s not magic—**you** still own architecture, safety, and “zeropaid” choices (below).

## 3. Agentic IDEs

The usual suspects:

- **[Cursor](https://cursor.com/)** — MCP-native, strong multi-file refactors, daily driver for many of these repos.
- **Google Antigravity** (and similar **agent-first** IDEs) — same class: **plan → act → diff** with repo context.

They’re **interfaces** to the same stack: **local git**, **local terminal**, **optional local LLM** for privacy or cost.

## 4. LLM tiers (how brain is paid for)

| Tier | Examples | Role |
|------|-----------|------|
| **Freebie / bundled** | IDE-included models, promos | Fast iteration, boilerplate, docstrings |
| **Local** | **[Ollama](https://ollama.com/)**, **[LM Studio](https://lmstudio.ai/)**, llama.cpp, etc. | **Zero marginal cost**, offline-ish, good for OpenManus + sensitive prompts |
| **Frontier (paid or quota)** | Claude Opus/Sonnet, Gemini, GPT, etc. | Hard refactors, security review, **integration architecture** |

**OpenManus** upstream is explicitly friendly to **local LLM** endpoints in `config.toml`; this MCP repo stays **agnostic**—you wire money or silicon where you want.

## 5. Priority: **zeropaid**

**Zeropaid** = optimize for **$0 recurring** where it doesn’t block quality: local inference, free tiers, self-hosted, FOSS glue. Paid APIs are **opt-in**, not the default assumption for fleet design.

## 6. Staying fresh: daily trawl

**Habit:** most days, skim **AI + infra news** with a filter: **FOSS**, **self-hostable**, **integratable** (API, CLI, MCP-shaped, Windows-friendly).

**Examples of “this week” flavor** (illustrative, not endorsements):

- **NemoClaw**-class stacks (NVIDIA / agentic claw ecosystem—watch for **what’s actually FOSS** and forkable).
- **Maus** (and similar) **Windows desktop** agents—evaluate **telemetry, EULA, and whether an MCP bridge is sane** before any integration.

If it’s **vendor-only** or **phone-home**, it may still inform **UX**, but it rarely becomes a **fleet repo**.

## 7. Integration concept pass (e.g. Opus 4.6)

Before cloning half the internet:

1. **Allocate a sustained reasoning pass** — e.g. **~15 minutes wall-clock** with a **frontier** model (**Claude Opus 4.6** is one option) *or* a very capable local model if you’ve tuned it.
2. **Prompt shape:** “Here’s the GitHub README + license + API surface; propose **MCP tool boundaries**, **webapp pages**, **risks**, **zeropaid path**.”
3. **Output:** a **short integration concept** (1–2 pages): adopt vs fork vs ignore; **ports**; **env vars**; **safety** callouts.

Only after that: **clone / fork** and **deep local analysis** (grep, run tests, threat model).

## 8. If it’s FOSS on GitHub

1. **Clone or fork** into your workspace (or add to **fleet** catalog for scripted clone).
2. **Deep local analysis:** build, tests, licenses, network calls, secrets handling.
3. **Decision:**
   - **New MCP server + webapp repo** (standard shape) → add to **sandraschi** fleet; **glama.json**, **docs**, **CI**; link from **openmanus-mcp** / central docs as needed.
   - **Light integration:** PR upstream, or a **thin wrapper** repo, or **document-only** if scope is wrong.

**Wrong fit** is allowed. **Zeropaid** and **safety** beat **checkbox integrations**.

## 9. Suggestions welcome

Open an issue with: **link**, **license**, **one paragraph “why fleet”**, and whether you want **MCP**, **webapp**, or **both**. Or send a PR to **`fleet_catalog.json`** with a curated entry and install recipe.

## 10. Honest visibility (no growth hacks)

**Lighthouse:** stories like **OpenClaw / OpenFang → huge stars** are **not** reproducible by README edits alone. **1k stars** *is* doable with **shipping + one good loop** of attention.

What actually moves the needle (all **legit**):

1. **30s demo** — screen recording or GIF: MCP tool call + dashboard + Fleet row. Drop under [docs/assets/](assets/README.md) (*Nano Banana stills / **Veo** clip optional but nice.*)
2. **GitHub Topics** — use the **full 20** from [.github/TOPICS.md](../.github/TOPICS.md) so searchers find you.
3. **Snappy “About” description** — paste the one-liner from TOPICS.md (search + social cards).
4. **One** high-signal post (e.g. Show HN, r/LocalLLaMA, X) when the demo is ready — **spamming** hurts.
5. **Glama** + **`glama.json`** — registry discovery for MCP users.
6. **Respond** to first issues fast — that’s how early adopters star.

We’re not chasing **100k** here; we’re building a **credible on-ramp** to OpenManus + MCP + UI.

← [README.md](../README.md) · [FLEET_CONTEXT.md](FLEET_CONTEXT.md) · [CONTRIBUTING.md](../CONTRIBUTING.md)
