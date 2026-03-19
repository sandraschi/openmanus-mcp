# LM Studio integration

This guide explains how to run `openmanus-mcp` + OpenManus against a local LM Studio server.

## Why LM Studio here

- OpenAI-compatible local API (`/v1/models`, `/v1/chat/completions`)
- Fast local iteration without cloud keys
- Works with both:
  - dashboard chat proxy (`/api/v1/chat/completions`)
  - upstream OpenManus model runtime (via `config/config.toml`)

## 1) Start LM Studio server

1. Install LM Studio.
2. Download at least one chat model.
3. Start local server mode.
4. Confirm endpoint:
   - `http://127.0.0.1:1234/v1/models`

## 2) Wire openmanus-mcp

In `openmanus-mcp/.env`:

```env
OPENMANUS_LMSTUDIO_BASE_URL=http://127.0.0.1:1234
```

Notes:
- Alias also supported: `LMSTUDIO_BASE_URL`
- Dashboard probe endpoint: `GET /api/v1/glom/lmstudio`

## 3) Wire upstream OpenManus

In `OpenManus/config/config.toml`, use OpenAI-compatible settings pointed at LM Studio:

```toml
[llm]
api_type = "openai"
model = "your-lmstudio-model-id"
base_url = "http://127.0.0.1:1234/v1"
api_key = "lmstudio"
temperature = 0.0
```

Use the model ID as shown by LM Studio `/v1/models`.

## 4) Verify end-to-end

1. `GET /api/v1/glom/lmstudio` shows `reachable: true`
2. Settings page displays LM Studio probe body with models
3. Chat panel:
   - provider: `lmstudio`
   - returns assistant message
4. `POST /api/v1/run` returns successful OpenManus run

## Troubleshooting

- `404 model not found`:
  - wrong model ID in OpenManus config or chat payload
- `connection refused`:
  - LM Studio server not running
- very slow first response:
  - model cold-start/loading latency

## vLLM vs LM Studio (quick)

- LM Studio:
  - easiest local desktop setup
  - best for single-user interactive use
- vLLM:
  - best for high concurrency / throughput serving
  - stronger when multiple agents/users hit the same backend

For this repo, LM Studio is the easiest default; vLLM is worth it when load grows.
