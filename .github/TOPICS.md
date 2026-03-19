# GitHub repository settings (topics + description)

## Snappy description (paste into **Settings → General → Description**)

**Short (fits most UIs):**

```text
FastMCP 3.1 MCP + React dashboard for OpenManus (FOSS). Local LLM. Fleet onboarding. Not Manus.im.
```

**Alt (more keywords, still one line):**

```text
Model Context Protocol server + Vite UI for FoundationAgents/OpenManus — Ollama, LM Studio, fleet MCP clones, beta.
```

**Homepage URL (optional):** `https://github.com/sandraschi/openmanus-mcp` or your docs site if you add one later.

---

## Topics (search discovery)

GitHub allows **20 topics** — use them all. Below is an **expanded** set (drop any that GitHub rejects).

**Suggested 20 (copy-paste chips):**

`mcp` · `model-context-protocol` · `fastmcp` · `openmanus` · `open-manus` · `ai-agents` · `local-llm` · `ollama` · `lm-studio` · `self-hosted` · `anthropic` · `cursor` · `fastapi` · `vite` · `react` · `python` · `mcp-server` · `automation` · `manus` · `zeropaid`

**Optional / swap in** if you drop something above: `foss` · `cli-wrapper` · `fuckzuck` · `glama` · `foundationagents`

---

## GitHub CLI (when `gh` is on PATH)

```powershell
gh repo edit sandraschi/openmanus-mcp `
  --description "FastMCP 3.1 MCP + React dashboard for OpenManus (FOSS). Local LLM. Fleet onboarding. Not Manus.im." `
  --add-topic mcp `
  --add-topic model-context-protocol `
  --add-topic fastmcp `
  --add-topic openmanus `
  --add-topic open-manus `
  --add-topic ai-agents `
  --add-topic local-llm `
  --add-topic ollama `
  --add-topic lm-studio `
  --add-topic self-hosted `
  --add-topic anthropic `
  --add-topic cursor `
  --add-topic fastapi `
  --add-topic vite `
  --add-topic react `
  --add-topic python `
  --add-topic mcp-server `
  --add-topic automation `
  --add-topic manus `
  --add-topic zeropaid
```

Verify: `gh api repos/sandraschi/openmanus-mcp --jq '{topics,description}'`

If **`gh` is not on PATH** in Cursor, install [GitHub CLI](https://cli.github.com/) and fix PATH. See [GITHUB_CLI_CURSOR_PATH](https://github.com/sandraschi/mcp-central-docs/blob/main/operations/GITHUB_CLI_CURSOR_PATH.md).

---

**Previously applied (2026-03-19):** older minimal topic set; **replace** with the block above for better search.
