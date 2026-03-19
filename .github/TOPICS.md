# GitHub repository topics

**Applied on 2026-03-19** via `gh repo edit` (topics: `cli-wrapper`, `fuckzuck`, `local-llm`, `manus`, `mcp`, `ollama`, `openmanus`, `zeropaid`). Verify: `gh api repos/sandraschi/openmanus-mcp --jq .topics`

If **`gh` is not on PATH** in your editor or terminal, install [GitHub CLI](https://cli.github.com/) and fix PATH (Windows: add the install folder Git picked, often under `Program Files`). See [mcp-central-docs: GITHUB_CLI_CURSOR_PATH.md](https://github.com/sandraschi/mcp-central-docs/blob/main/operations/GITHUB_CLI_CURSOR_PATH.md).

---

Set under **Settings → General → Topics** on the repo, or with **GitHub CLI** (when `gh` is on your `PATH`):

```powershell
gh repo edit sandraschi/openmanus-mcp `
  --add-topic manus `
  --add-topic openmanus `
  --add-topic mcp `
  --add-topic ollama `
  --add-topic local-llm `
  --add-topic zeropaid `
  --add-topic fuckzuck `
  --add-topic cli-wrapper
```

**Paste into Topics field (one per chip):**

`manus` · `openmanus` · `mcp` · `ollama` · `local-llm` · `zeropaid` · `fuckzuck` · `cli-wrapper`

> GitHub may reject topics that violate their policies; if a chip fails to save, drop it and retry.
