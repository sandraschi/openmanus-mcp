# Glama (`glama.json`)

← [Documentation index](README.md)


This repo ships **`glama.json`** at the root for [Glama](https://glama.ai/mcp/servers) discovery and for clients that read the **`mcpServers`** block.

## Layout

| Section | Purpose |
|--------|---------|
| **`$schema`** | `https://glama.ai/schemas/mcp.json` — IDE validation where supported |
| **`packages`** | Registry-style entry (GitHub + stdio via `uv run …`) |
| **`mcpServers`** | Rich client config: capabilities, timeouts, webapp URLs (**10769** UI, **10768** API) |

## Requirements

- **`uv`** on `PATH`, repo checkout with dependencies: `uv sync` (dev: `uv sync --extra dev`).
- **`cwd`** for MCP clients should be the **repository root** (same as `uv` project root) so `.env` and `fleet/` resolve correctly.

## Validate locally

```powershell
just check-glama
```

Or: `uv run python -c "import json; json.load(open('glama.json', encoding='utf-8'))"`.

## Version

Keep **`version`** in `glama.json` aligned with **`pyproject.toml`** and release tags when you cut releases.

## References

- [mcp-central-docs — MCPB / Glama notes](https://github.com/sandraschi/mcp-central-docs/blob/main/standards/MCPB_PACKAGING_STANDARDS.md) (Glama vs MCPB, discovery)
