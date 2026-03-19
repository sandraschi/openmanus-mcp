# Skills (OpenClaw-style)

Architecture context: [ARCHITECTURE.md](ARCHITECTURE.md#openclaw-style-features-shipped--planned).

This API mirrors the **OpenClaw / AgentSkills** pattern:

1. **Compact index** — For `intent=chat` and `skills_mode=index`, the server adds a system message with an XML-like list of skills: `name`, `description`, and filesystem `location` (path to `SKILL.md`).
2. **Full playbook on demand** — The model is instructed not to invent steps; it should read `SKILL.md` at `location` if the runtime has file access, or the client can pass **`skill_ids`** so the server inlines full markdown into extra system messages.

## Bundled skills

Shipped under `src/openmanus_mcp/skills/*/SKILL.md` (e.g. `mcp-builder`).

## Extra directories

Set **`OPENMANUS_SKILLS_EXTRA_DIRS`** to semicolon-separated roots (Windows-friendly). Scanned **before** bundled paths so extra skills **override** on same `name` / id precedence (first discovery wins).

## REST

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/v1/skills` | List skills + `estimated_index_chars` |
| GET | `/api/v1/skills/{id}` | Full `SKILL.md` body (path-validated) |

## Chat API

`POST /api/v1/chat/completions` accepts:

- **`skills_mode`**: `index` | `off` (index is skipped when `intent=refine`).
- **`skill_ids`**: e.g. `["mcp-builder"]` to inject full skill text (capped by **`OPENMANUS_MAX_SKILL_INJECT_CHARS`**, default 24000).

## Web UI

SOTA Chat panel: choose **compact index** on/off and tick skills to attach full playbooks for that send.
