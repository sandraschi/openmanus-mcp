"""OpenClaw-style skills: SKILL.md discovery, compact system index, optional full-body injection.

Matches the pattern from OpenClaw docs: eligible skills → compact XML-like listing
(name, description, location) in system context; full SKILL.md loaded on demand
(API or filesystem), or inlined when the client passes ``skill_ids`` on chat.
"""

from __future__ import annotations

import html
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

# --- frontmatter (minimal parser; no PyYAML dependency) ----------------------

_FM_BLOCK = re.compile(r"\A---\s*\r?\n(.*?)\r?\n---\s*\r?\n(.*)\Z", re.DOTALL)


def _parse_fm_lines(block: str) -> dict[str, str]:
    meta: dict[str, str] = {}
    for line in block.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, rest = line.partition(":")
        k = key.strip()
        v = rest.strip()
        if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
            v = v[1:-1]
        if k:
            meta[k] = v
    return meta


def parse_skill_md(raw: str) -> tuple[dict[str, str], str]:
    """Split SKILL.md into frontmatter dict and body."""
    m = _FM_BLOCK.match(raw.strip())
    if not m:
        return {}, raw
    return _parse_fm_lines(m.group(1)), m.group(2)


def _slug(s: str) -> str:
    s2 = re.sub(r"[^a-zA-Z0-9]+", "-", s.strip().lower()).strip("-")
    return s2 or "skill"


@dataclass(frozen=True, slots=True)
class SkillMeta:
    """One discovered skill (compact index row)."""

    skill_id: str
    name: str
    description: str
    path: Path
    source: str  # bundled | extra

    def to_public_dict(self) -> dict[str, str]:
        return {
            "id": self.skill_id,
            "name": self.name,
            "description": self.description,
            "location": str(self.path.resolve()),
            "source": self.source,
        }


def bundled_skills_root() -> Path:
    """Shipped skills next to this package (``openmanus_mcp/skills/``)."""
    return Path(__file__).resolve().parent / "skills"


def _roots_from_settings_extra(extra: str) -> list[Path]:
    roots: list[Path] = []
    for part in extra.split(";"):
        p = part.strip()
        if not p:
            continue
        roots.append(Path(p).expanduser().resolve())
    return roots


def discover_skills(*, extra_dirs_semicolon: str) -> list[SkillMeta]:
    """Scan extra dirs first (override precedence), then bundled skills."""
    roots: list[tuple[str, Path]] = []
    for p in _roots_from_settings_extra(extra_dirs_semicolon):
        roots.append(("extra", p))
    b = bundled_skills_root()
    if b.is_dir():
        roots.append(("bundled", b))

    seen_ids: set[str] = set()
    out: list[SkillMeta] = []

    for source, root in roots:
        if not root.is_dir():
            continue
        for path in sorted(root.rglob("SKILL.md")):
            if not path.is_file():
                continue
            try:
                raw = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            fm, _body = parse_skill_md(raw)
            name = (fm.get("name") or path.parent.name).strip()
            desc = (fm.get("description") or "").strip()
            sid = _slug(name)
            if sid in seen_ids:
                base = sid
                n = 2
                while f"{base}-{n}" in seen_ids:
                    n += 1
                sid = f"{base}-{n}"
            seen_ids.add(sid)
            out.append(
                SkillMeta(
                    skill_id=sid,
                    name=name,
                    description=desc,
                    path=path.resolve(),
                    source=source,
                )
            )
    return out


def xml_escape_attr(s: str) -> str:
    return html.escape(s, quote=True)


def format_skills_for_prompt(metas: list[SkillMeta]) -> str:
    """Compact OpenClaw-style index for the system prompt (not full SKILL.md)."""
    if not metas:
        return ""
    lines = [
        "<available_skills>",
        "OpenClaw-style skill index (compact). Each skill's full instructions live in SKILL.md "
        "at the given location. Do not invent playbook steps; read that file if your runtime "
        "exposes filesystem access, or ask the host to pass this skill in skill_ids for full "
        "injection via the chat API.",
    ]
    for m in metas:
        lines.append(
            f'<skill name="{xml_escape_attr(m.name)}" '
            f'description="{xml_escape_attr(m.description)}" '
            f'location="{xml_escape_attr(str(m.path))}" />'
        )
    lines.append("</available_skills>")
    return "\n".join(lines)


def estimate_skills_prompt_chars(metas: list[SkillMeta]) -> int:
    """Rough character count (OpenClaw documents a similar formula)."""
    if not metas:
        return 0
    base = 195
    per = 97
    total = base
    for m in metas:
        total += per + len(xml_escape_attr(m.name))
        total += len(xml_escape_attr(m.description))
        total += len(xml_escape_attr(str(m.path)))
    return total


# --- security + load body ----------------------------------------------------


def _allowed_roots(extra: str) -> list[Path]:
    roots = [p.resolve() for p in _roots_from_settings_extra(extra)]
    b = bundled_skills_root()
    if b.is_dir():
        roots.append(b.resolve())
    return roots


def _is_under_allowed(path: Path, roots: list[Path]) -> bool:
    try:
        rp = path.resolve()
    except OSError:
        return False
    for root in roots:
        try:
            rp.relative_to(root)
            return True
        except ValueError:
            continue
    return False


def find_skill_by_id(skill_id: str, *, extra_dirs_semicolon: str) -> SkillMeta | None:
    for m in discover_skills(extra_dirs_semicolon=extra_dirs_semicolon):
        if m.skill_id == skill_id:
            return m
    return None


def read_skill_body(
    skill_id: str,
    *,
    extra_dirs_semicolon: str,
    max_chars: int,
) -> tuple[str, str] | None:
    """Return (name, full_markdown) or None if missing / unsafe."""
    meta = find_skill_by_id(skill_id, extra_dirs_semicolon=extra_dirs_semicolon)
    if meta is None:
        return None
    roots = _allowed_roots(extra_dirs_semicolon)
    if not _is_under_allowed(meta.path, roots):
        return None
    try:
        raw = meta.path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    if len(raw) > max_chars:
        raw = raw[:max_chars] + "\n\n… [truncated by server max_skill_inject_chars] …\n"
    return meta.name, raw


def format_full_skill_system_message(skill_name: str, body: str) -> str:
    return f"Full skill playbook ({skill_name}) — SKILL.md content:\n\n{body}"


def assemble_chat_system_layers(
    *,
    persona_system: str,
    intent: str,
    skills_mode: Literal["off", "index"],
    skill_ids: list[str],
    page_context: str | None,
    extra_dirs_semicolon: str,
    max_skill_inject_chars: int,
) -> list[dict[str, str]]:
    """System messages in order: persona, optional skills index, optional full skills, page."""
    out: list[dict[str, str]] = [{"role": "system", "content": persona_system}]

    metas = discover_skills(extra_dirs_semicolon=extra_dirs_semicolon)
    if intent == "chat" and skills_mode == "index" and metas:
        idx = format_skills_for_prompt(metas)
        if idx:
            out.append({"role": "system", "content": idx})

    seen: set[str] = set()
    for sid in skill_ids:
        sid = sid.strip()
        if not sid or sid in seen:
            continue
        seen.add(sid)
        loaded = read_skill_body(
            sid,
            extra_dirs_semicolon=extra_dirs_semicolon,
            max_chars=max_skill_inject_chars,
        )
        if loaded is None:
            continue
        name, body = loaded
        out.append(
            {
                "role": "system",
                "content": format_full_skill_system_message(name, body),
            }
        )

    if page_context:
        out.append(
            {
                "role": "system",
                "content": f"Client route / UI context:\n{page_context}",
            }
        )
    return out
