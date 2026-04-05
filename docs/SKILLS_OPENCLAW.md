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

## Run API (OpenManus subprocess)

`POST /api/v1/run` and `POST /api/v1/run/async` accept optional **`skill_ids`** (same shape as chat, max **8**). The server builds the subprocess prompt by **prepending** the selected full `SKILL.md` bodies (subject to **`OPENMANUS_MAX_SKILL_INJECT_CHARS`**), then appends a clear **Task / user instructions** section with your `prompt`. This matches chat’s full-playbook injection but applies to **runner** flows.

## Web UI

SOTA **Chat**: choose **compact index** on/off and tick skills to attach full playbooks for that send.

SOTA **Run**: load the catalog from `GET /api/v1/skills`, tick skills for **`skill_ids`** on sync/async run, or **append** raw `SKILL.md` bodies into the textarea (client-side) for manual editing before run.
