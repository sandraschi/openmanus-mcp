# What works where

Quick matrix for **openmanus-mcp** surfaces: stdio MCP, REST, web UI (SOTA), and how **skills** / **supervisor** apply.

| Capability | Stdio MCP (`openmanus_bridge`) | REST API | Web UI |
|------------|-------------------------------|----------|--------|
| OpenManus path check | `validate`, `status` | `GET /api/v1/status` | Run + Settings (status strip) |
| Sync run | `run_prompt` | `POST /api/v1/run` | Run page |
| Async run + poll | `run_prompt_async`, `job_status` | `POST /api/v1/run/async`, `GET /api/v1/run/jobs/{id}` | Run page |
| **Run-time skill playbooks** | *(not in tool yet)* | **`skill_ids` on `/run` and `/run/async`** (server prepends full `SKILL.md` + task) | Run page (checkboxes) |
| Chat + compact skill index | — | `POST /api/v1/chat/completions` (`skills_mode=index`) | Chat |
| Chat + full skills | — | same + `skill_ids` | Chat |
| List / read skills | — | `GET /api/v1/skills`, `GET /api/v1/skills/{id}` | Run (list + append), Chat |
| Supervisor heartbeat / schedules | — | `GET /api/v1/supervisor/*` | Settings (summary from `GET /api/v1/status`) |
| Fleet | — | `/api/v1/fleet/*` | Fleet page |
| Connectors catalog | — | `GET /api/v1/connectors` | *(API only unless linked elsewhere)* |

**Notes**

- **`skill_ids`** on runs uses the same discovery rules as chat (`OPENMANUS_SKILLS_EXTRA_DIRS`, cap `OPENMANUS_MAX_SKILL_INJECT_CHARS`). Max **8** ids per request (API-enforced).
- **Supervisor** must be enabled with **`OPENMANUS_SUPERVISOR_ENABLED=true`**; schedules live under `/api/v1/supervisor/schedules`. See [SUPERVISOR.md](SUPERVISOR.md).

← [Documentation index](README.md) · [SKILLS_OPENCLAW.md](SKILLS_OPENCLAW.md) · [TECH.md](TECH.md)
