# OpenManus (upstream)

**openmanus-mcp** is built to work **alongside** a local checkout of **[FoundationAgents/OpenManus](https://github.com/FoundationAgents/OpenManus)**.

## What OpenManus is

- **FOSS** agent / “Manus-class” **CLI** style workflow (see upstream README and `main.py`).
- You configure **LLM endpoints** in upstream **`config.toml`** (examples under `config/config.example-*.toml`).
- **Local inference:** e.g. **Ollama**, **LM Studio** — no cloud requirement if you set `api_type` / `base_url` accordingly.

This project does **not** fork OpenManus; it expects you to clone upstream separately.

## How openmanus-mcp uses it

1. Set **`OPENMANUS_ROOT`** in **`.env`** (or environment) to the **root directory** of your OpenManus clone (the folder that contains upstream `main.py`).
2. Use **`openmanus_bridge`** operation **`validate`** in MCP to check path layout (`main.py`, config examples).
3. **`run_prompt`** is still a **stub** in alpha; run the agent via upstream’s CLI until the runner lands here.

## MCP config in OpenManus

Upstream ships **`config/mcp.example.json`** (evolves with releases). Wiring **external** MCP servers **inside** the OpenManus process is **upstream-defined** — treat their docs and examples as source of truth for *in-agent* MCP.

**Cursor / Glama** wiring of **openmanus-mcp** is **independent** (stdio + `cwd` to this repo). See [INSTALL.md](INSTALL.md).

## Further reading

- Upstream: [OpenManus](https://github.com/FoundationAgents/OpenManus)
- Manus.im vs FOSS: [MANUS.md](MANUS.md)
- Fleet + desktop automation: [FLEET.md](FLEET.md) · [SAFETY.md](SAFETY.md)

← [Documentation index](README.md)
