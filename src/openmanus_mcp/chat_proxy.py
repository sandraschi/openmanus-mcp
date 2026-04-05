"""HTTP proxy to Ollama and LM Studio for the web dashboard (no API keys in-browser)."""

from __future__ import annotations

from typing import Any, Literal

import httpx

Provider = Literal["ollama", "lmstudio"]


def _norm_base(url: str) -> str:
    return url.rstrip("/")


async def resolve_ollama_model(client: httpx.AsyncClient, base: str, explicit: str | None) -> str:
    if explicit and explicit.strip():
        return explicit.strip()
    r = await client.get(f"{_norm_base(base)}/api/tags", timeout=8.0)
    r.raise_for_status()
    data = r.json()
    models = data.get("models") or []
    if not models:
        raise ValueError("Ollama /api/tags returned no models (pull a model: ollama pull <name>)")
    first = models[0]
    name = first.get("name") or first.get("model")
    if not name:
        raise ValueError("Ollama tags entry missing name")
    return str(name)


async def resolve_lmstudio_model(client: httpx.AsyncClient, base: str, explicit: str | None) -> str:
    if explicit and explicit.strip():
        return explicit.strip()
    r = await client.get(f"{_norm_base(base)}/v1/models", timeout=8.0)
    r.raise_for_status()
    data = r.json()
    items = data.get("data") or []
    if not items:
        raise ValueError("LM Studio /v1/models returned no models (load a model in LM Studio)")
    mid = items[0].get("id")
    if not mid:
        raise ValueError("LM Studio models entry missing id")
    return str(mid)


async def completion_ollama(
    *,
    base: str,
    model: str,
    messages: list[dict[str, str]],
    temperature: float,
) -> dict[str, Any]:
    url = f"{_norm_base(base)}/api/chat"
    payload: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {"temperature": temperature},
    }
    async with httpx.AsyncClient(timeout=120.0) as client:
        r = await client.post(url, json=payload)
        r.raise_for_status()
        data = r.json()
    msg = data.get("message") or {}
    content = msg.get("content")
    if not content:
        return {"success": False, "error": "Ollama response missing message.content", "raw": data}
    return {
        "success": True,
        "content": str(content),
        "raw_model": data.get("model"),
        "provider": "ollama",
    }


async def completion_lmstudio(
    *,
    base: str,
    model: str,
    messages: list[dict[str, str]],
    temperature: float,
) -> dict[str, Any]:
    url = f"{_norm_base(base)}/v1/chat/completions"
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }
    async with httpx.AsyncClient(timeout=120.0) as client:
        r = await client.post(url, json=payload)
        r.raise_for_status()
        data = r.json()
    choices = data.get("choices") or []
    if not choices:
        return {"success": False, "error": "LM Studio response missing choices", "raw": data}
    msg = choices[0].get("message") or {}
    content = msg.get("content")
    if not content:
        return {"success": False, "error": "LM Studio choice missing message.content", "raw": data}
    return {
        "success": True,
        "content": str(content),
        "raw_model": data.get("model"),
        "provider": "lmstudio",
    }
