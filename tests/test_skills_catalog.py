"""Skills discovery, prompt formatting, chat system assembly."""

from openmanus_mcp.chat_personas import persona_system_prompt
from openmanus_mcp.skills_catalog import (
    assemble_chat_system_layers,
    discover_skills,
    estimate_skills_prompt_chars,
    format_skills_for_prompt,
    parse_skill_md,
)


def test_parse_skill_md_frontmatter() -> None:
    raw = """---
name: test-skill
description: A test
---
Body line.
"""
    fm, body = parse_skill_md(raw)
    assert fm.get("name") == "test-skill"
    assert "Body line" in body


def test_discover_bundled_mcp_builder() -> None:
    metas = discover_skills(extra_dirs_semicolon="")
    ids = {m.skill_id for m in metas}
    assert "mcp-builder" in ids
    mcp = next(m for m in metas if m.skill_id == "mcp-builder")
    assert "FastMCP" in mcp.description or "MCP" in mcp.description


def test_format_skills_for_prompt_xml() -> None:
    metas = discover_skills(extra_dirs_semicolon="")
    text = format_skills_for_prompt(metas)
    assert "<available_skills>" in text
    assert '<skill name=' in text
    assert "location=" in text


def test_estimate_chars_positive_with_skills() -> None:
    metas = discover_skills(extra_dirs_semicolon="")
    n = estimate_skills_prompt_chars(metas)
    assert n > 200


def test_assemble_chat_includes_index_by_default() -> None:
    sys_p = persona_system_prompt("reductionist", intent="chat")
    layers = assemble_chat_system_layers(
        persona_system=sys_p,
        intent="chat",
        skills_mode="index",
        skill_ids=[],
        page_context=None,
        extra_dirs_semicolon="",
        max_skill_inject_chars=24_000,
    )
    assert layers[0]["role"] == "system"
    c0 = layers[0]["content"].lower()
    assert "reductionist" in c0 or "technical" in c0
    assert any("<available_skills>" in x["content"] for x in layers)


def test_assemble_refine_skips_skill_index() -> None:
    sys_p = persona_system_prompt("reductionist", intent="refine")
    layers = assemble_chat_system_layers(
        persona_system=sys_p,
        intent="refine",
        skills_mode="index",
        skill_ids=[],
        page_context=None,
        extra_dirs_semicolon="",
        max_skill_inject_chars=24_000,
    )
    assert not any("<available_skills>" in x["content"] for x in layers)


def test_assemble_off_no_index() -> None:
    sys_p = persona_system_prompt("reductionist", intent="chat")
    layers = assemble_chat_system_layers(
        persona_system=sys_p,
        intent="chat",
        skills_mode="off",
        skill_ids=[],
        page_context=None,
        extra_dirs_semicolon="",
        max_skill_inject_chars=24_000,
    )
    assert len(layers) == 1
    assert "<available_skills>" not in layers[0]["content"]


def test_assemble_skill_ids_inject_full_body() -> None:
    sys_p = persona_system_prompt("reductionist", intent="chat")
    layers = assemble_chat_system_layers(
        persona_system=sys_p,
        intent="chat",
        skills_mode="off",
        skill_ids=["mcp-builder"],
        page_context=None,
        extra_dirs_semicolon="",
        max_skill_inject_chars=24_000,
    )
    assert len(layers) >= 2
    joined = "\n".join(x["content"] for x in layers)
    assert "Full skill playbook" in joined
    assert "FastMCP" in joined
