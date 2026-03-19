# OpenManus (upstream)

**openmanus-mcp** is built to work **alongside** a local checkout of **[FoundationAgents/OpenManus](https://github.com/FoundationAgents/OpenManus)**.

## What OpenManus is

- **FOSS** agent / “Manus-class” **CLI** style workflow (see upstream README and `main.py`).
- You configure **LLM endpoints** in upstream **`config.toml`** (examples under `config/config.example-*.toml`).
- **Local inference:** e.g. **Ollama**, **LM Studio** — no cloud requirement if you set `api_type` / `base_url` accordingly.
- **Serving alternative:** **vLLM** can be used behind OpenAI-compatible endpoints when you need higher multi-request throughput.

This project does **not** fork OpenManus; it expects you to clone upstream separately.

## How openmanus-mcp uses it

1. Set **`OPENMANUS_ROOT`** in **`.env`** (or environment) to the **root directory** of your OpenManus clone (the folder that contains upstream `main.py`).
2. Use **`openmanus_bridge`** operation **`validate`** in MCP to check path layout (`main.py`, config examples).
3. **`run_prompt`** runs a **subprocess** of upstream **`main.py`** or **`run_flow.py`**: single-line prompts use **`main.py --prompt`**; multiline prompts use **stdin**. Use **`run_prompt_async`** + **`job_status`** for polling. REST: **`POST /api/v1/run`**, **`POST /api/v1/run/async`**, **`GET /api/v1/run/jobs/{id}`** (same runner). Configure **`OPENMANUS_RUNNER_TIMEOUT_S`** and **`OPENMANUS_JOB_STORE_MAX_COMPLETED`** as needed.

## MCP config in OpenManus

Upstream ships **`config/mcp.example.json`** (evolves with releases). Wiring **external** MCP servers **inside** the OpenManus process is **upstream-defined** — treat their docs and examples as source of truth for *in-agent* MCP.

**Cursor / Glama** wiring of **openmanus-mcp** is **independent** (stdio + `cwd` to this repo). See [INSTALL.md](INSTALL.md).

## Further reading

- Upstream: [OpenManus](https://github.com/FoundationAgents/OpenManus)
- Local LM Studio guide in this repo: [LMSTUDIO.md](LMSTUDIO.md)
- Manus.im vs FOSS: [MANUS.md](MANUS.md)
- Fleet + desktop automation: [FLEET.md](FLEET.md) · [SAFETY.md](SAFETY.md)

← [Documentation index](README.md)
