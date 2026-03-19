# Repository hygiene & authenticity

This project is **MCP + agent-adjacent**, so it gets extra scrutiny from people tired of **low-effort “AI slop”** repos. This page is our **honest signal**: what we optimize for, and what we reject.

## Why this exists — GitHub is noisier than it used to be

**Lament, briefly:** maintainers everywhere are drowning in **streams of useless AI PRs and issues** — generic refactors, hallucinated fixes, dependency churn, and copy-paste “contributions” that exist only to farm green squares or train engagement metrics. That noise **erodes trust** in real agent-assisted work.

Worse patterns are showing up too: **repo sabotage and poisoning** (social pressure, bad-faith reports, malicious or misleading patches dressed as helpful automation), and **centaur** setups: a **human face** up front (account, byline, “I’m responsible”) with **agentic automation** behind. The back half is **not** a harmless pony — it’s an **agent** that can **hide more agents** (MCP tools, sub-agents, scripts, fleets), **recursively**, so **blast radius and review load** grow **ad nauseam** while the human part still looks like “one contributor.” When that goes wrong, **accountability vanishes** (“the agent did it”: unreviewed merges, toxic drive-by comments, scope creep).

**Asymmetric damage:** one **troll with an agent fleet** (parallel accounts, scripted issues, spam PRs, coordinated pile-ons) can burn **hours of maintainer time** across **many** repos before platforms react. GitHub’s tools weren’t built for that volume; **small projects get hit hardest**.

None of that is a reason to ban tools — it *is* a reason to be **explicit** about standards (this page), **close** garbage fast, and **protect** `main` with CI and human merge authority.

### Arms race (2026): hardening stacks and who else is in the fight

**Offense and defense are both accelerating.** What ships this month is stale next quarter — assume **continuous** learning, not a one-time checklist.

**Defensive tooling worth studying** (names overlap; verify before you buy):

- **Dark Twin Universe (DTU)** — **twin / shadow** hardening: **parallel or sandboxed** “dark” copies of your agent’s world (inputs, tools, policies) so you can **probe** behavior **before** production paths see the same traffic. **This org’s DTU work** is **[dark-app-factory](https://github.com/sandraschi/dark-app-factory)** on GitHub (**public**) — **source of truth** for patterns and runbooks. *(It stayed private briefly while the factory was honed.)*
- **Agent gateways** against **prompt injection** and **indirect instruction** — malicious text smuggled via **tool arguments**, **retrieved documents**, **READMEs**, **CI logs**, **MCP tool results**, etc. A concrete vendor in this space is **[Bastio](https://www.bastio.com/)** (AI security gateway, deterministic inspection). Other **“Bastion”**-named stacks exist (e.g. local gateways, separate research blogs); **bastion.ai** is **not** a product homepage — **verify URLs** before relying on them.

**Offense is not hypothetical.** The same **fleet**, **MCP**, and **automation** primitives defenders use are available to **virus / malware authors**, **organized crime** (**yakuza**-class syndicates are one example), and **extremist** movements (**ISIS**-class networks and analogues). They will **iterate** as fast as the tooling ecosystem — **2026 will be ugly** in places. This repo’s scope stays **hygiene + transparency + CI**; **layer** twinning, gateways, and org **IR** where your **stakes** require it.

**Stay vigilant:** re-read **threat models** when you add **new tools**, **new MCP servers**, or **new fleet members** — **nested agents** compound risk faster than policy docs grow.

### Plain English: security / abuse jargon

We sometimes borrow terms from **security research**. Spelling: **Sybil** (the standard term in papers — not “Sibyl” the oracle).

| Term | What it means without the jargon |
|------|----------------------------------|
| **Sybil attack** | One real actor runs **many fake identities** (sockpuppets) so a platform thinks it’s dealing with lots of separate people — used to **spam**, **dodge per-account limits**, or **inflate consensus**. |
| **Sybil resistance** | Anything that makes **mass sockpuppets costly or detectable** (verification, rate limits, reputation, org SSO, etc.). **Not inherently crypto** — same goal as “you can’t open 10k GitHub accounts for free and look like 10k humans.” |
| **Poisoning** (in this doc) | **Sabotage by bad inputs**: malicious or misleading **patches**, **dependencies**, **reports**, or **data** meant to break trust, automation, or safety — not “machine learning poisoning” unless we say so explicitly. |
| **Centaur** (here) | **Human front + agent “horse”** (we keep the **centaur** metaphor): **not** a cute pony — the rear is **real automation** that can **nest** (agents behind agents, MCP chains, fleets), so **risk and opacity** scale fast. **Healthy** = a human **actually steers** and can explain what ran. **Anti-pattern** = **smokescreen**: nobody **owns** merges, tone, or scope (“the agent did it”). |

## What we optimize for

| Signal | What it means here |
|--------|-------------------|
| **Runnable product** | Install path, `uv`, CI (Ruff + pytest + web build), ports documented — not a README-only wrapper. |
| **Clear scope** | One FastMCP server, one FastAPI surface, one Vite app, fleet onboarding — see [ARCHITECTURE.md](ARCHITECTURE.md). |
| **Explicit stubs** | e.g. `run_prompt` — we say **stub** in [OPENMANUS.md](OPENMANUS.md), not fake “done”. |
| **Human maintainer** | [sandraschi](https://github.com/sandraschi) owns merges; issues should get **real triage**, not bot-only replies. |
| **Attribution** | Upstream **OpenManus**, **FastMCP**, ecosystem patterns — linked and named, not laundered. |

## AI-assisted development (transparent)

- **Using** Copilot, Cursor, Claude, local LLMs, etc. is **normal** here — same bar as hand-written work: **tests pass**, **Ruff clean**, **diff reviewable**.
- **Please** mention in the PR if a large change was mostly model-generated — helps reviewers prioritize (not a moral test, a **review bandwidth** hint).
- **Do not** open PRs that are **generic boilerplate** (whole-file README swaps, copy-paste policy essays, dependency dumps without justification). Those will be closed.

## What we are not

- Not a **star-farming** or **SEO wrapper** repo.
- Not **undisclosed** autonomous bots merging to `main`.
- Not claiming parity with **Manus.im** or other vendors — see [MANUS.md](MANUS.md).

## If something looks off

- **Security** → [SECURITY.md](../SECURITY.md) (private advisory preferred).
- **Spam, bad-faith mass issues, or coordinated pile-ons** → one **issue** or **Discussion** with facts; maintainers will triage. **Brigading** doesn’t improve the code.

## Planned ORB integration

**ORB** integration is **planned** (exact API and packaging **TBD**). When scope is fixed it will be documented in [ARCHITECTURE.md](ARCHITECTURE.md), [TECH.md](TECH.md), and the root [CHANGELOG.md](../CHANGELOG.md). Watch **Issues** for the design thread.

← [Documentation index](README.md) · [CONTRIBUTING.md](../CONTRIBUTING.md)
