# openmanus-mcp — Agent Guide

## Overview
FastMCP 3.2.0 MCP + React dashboard for OpenManus (FOSS). Local LLM. Fleet onboarding.

## Entry Points
- `uv run openmanus-mcp` → `openmanus_mcp.__main__:main`

## Standards
- FastMCP 3.2+ portmanteau tool pattern — tools use `operation` enum param
- Responses: structured dicts with `success`, `message`, domain-specific fields
- Dual transport: stdio (Claude Desktop) + HTTP (`MCP_TRANSPORT=http`)
- See [mcp-central-docs](https://github.com/sandraschi/mcp-central-docs) for fleet-wide coding standards

## Key Files
- `README.md` — full documentation
- `pyproject.toml` — build config and entry points
- `CLAUDE.md` — Claude Code context (if present)
