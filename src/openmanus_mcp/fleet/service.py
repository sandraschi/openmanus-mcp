"""Clone, install, and optional webapp launch for curated fleet members."""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
import uuid
from datetime import UTC, datetime
from importlib import resources
from pathlib import Path
from typing import Any

from openmanus_mcp.fleet.models import (
    CatalogMember,
    CatalogRow,
    FleetCatalogFile,
    FleetStateFile,
    InstallSpec,
    OnboardedMember,
    OnboardRequest,
    OnboardResponse,
    OnboardResult,
    WebappStartRequest,
    WebappStartResponse,
)
from openmanus_mcp.fleet.paths import default_repo_root

_REPO_ALLOW = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")


def _load_catalog_raw() -> FleetCatalogFile:
    raw = (
        resources.files("openmanus_mcp.data")
        .joinpath("fleet_catalog.json")
        .read_text(encoding="utf-8")
    )
    return FleetCatalogFile.model_validate_json(raw)


def catalog_by_id() -> dict[str, CatalogMember]:
    data = _load_catalog_raw()
    return {m.id: m for m in data.members}


def resolve_fleet_root(configured: Path | None) -> Path:
    """Resolve fleet dir: env override, else ``<repo>/fleet``, else ``./openmanus-fleet``."""
    if configured is not None:
        return Path(configured).expanduser().resolve()
    cand = default_repo_root()
    if (cand / "pyproject.toml").exists():
        return (cand / "fleet").resolve()
    return (Path.cwd() / "openmanus-fleet").resolve()


def _state_path(fleet_root: Path) -> Path:
    return fleet_root / ".fleet_state.json"


def load_state(fleet_root: Path) -> FleetStateFile:
    p = _state_path(fleet_root)
    if not p.is_file():
        return FleetStateFile()
    return FleetStateFile.model_validate_json(p.read_text(encoding="utf-8"))


def save_state(fleet_root: Path, state: FleetStateFile) -> None:
    fleet_root.mkdir(parents=True, exist_ok=True)
    p = _state_path(fleet_root)
    tmp = p.with_suffix(f".tmp.{uuid.uuid4().hex}")
    tmp.write_text(state.model_dump_json(indent=2), encoding="utf-8")
    tmp.replace(p)


def merge_catalog_rows(fleet_root: Path) -> list[CatalogRow]:
    by_id = catalog_by_id()
    st = load_state(fleet_root)
    rows: list[CatalogRow] = []
    for m in by_id.values():
        ob = st.members.get(m.id)
        rows.append(
            CatalogRow(
                **m.model_dump(),
                onboarded=ob is not None,
                clone_path=ob.clone_path if ob else None,
                install_ok=ob.install_ok if ob else None,
            )
        )
    return rows


def _clone_url(github_repo: str) -> str:
    if not _REPO_ALLOW.match(github_repo):
        raise ValueError(f"Invalid github_repo: {github_repo!r}")
    return f"https://github.com/{github_repo}.git"


def _clone_name(member: CatalogMember) -> str:
    return member.github_repo.split("/")[-1]


def _run_capture(
    argv: list[str],
    cwd: Path,
    timeout: float = 600,
) -> subprocess.CompletedProcess[str]:
    # PLW1510: Add check=False
    return subprocess.run(
        argv,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=timeout,
        shell=False,
        check=False,
    )


def _install_uv_pip_editable(clone: Path) -> tuple[bool, str]:
    lines: list[str] = []
    if not shutil.which("uv"):
        return False, "uv not found on PATH; install https://docs.astral.sh/uv/"
    r1 = _run_capture(["uv", "venv"], cwd=clone)
    lines.append(f"uv venv: rc={r1.returncode}\n{r1.stdout}\n{r1.stderr}")
    if r1.returncode != 0:
        return False, "\n".join(lines)
    py = clone / ".venv" / "Scripts" / "python.exe"
    if not py.is_file():
        py = clone / ".venv" / "bin" / "python"
    if not py.is_file():
        return False, "\n".join(lines) + "\nno venv python found"
    r2 = _run_capture(["uv", "pip", "install", "-e", "."], cwd=clone)
    lines.append(f"uv pip install -e .: rc={r2.returncode}\n{r2.stdout}\n{r2.stderr}")
    return r2.returncode == 0, "\n".join(lines)


def _install_uv_sync(clone: Path) -> tuple[bool, str]:
    lines: list[str] = []
    if not shutil.which("uv"):
        return False, "uv not found on PATH"
    r0 = _run_capture(["uv", "lock"], cwd=clone)
    lines.append(f"uv lock: rc={r0.returncode}\n{r0.stdout}\n{r0.stderr}")
    r1 = _run_capture(["uv", "sync", "--extra", "dev"], cwd=clone)
    lines.append(f"uv sync --extra dev: rc={r1.returncode}\n{r1.stdout}\n{r1.stderr}")
    return r1.returncode == 0, "\n".join(lines)


def _install_in_clone(member: CatalogMember, clone: Path) -> tuple[bool, str]:
    # PLR0911: Reduce return statements by decomposing
    spec: InstallSpec = member.install

    if spec.kind == "none":
        return True, "clone only (no package install)"
    if spec.kind == "uv_pip_editable":
        return _install_uv_pip_editable(clone)
    if spec.kind == "uv_sync_extra_dev":
        return _install_uv_sync(clone)

    return False, f"unknown install kind: {spec.kind}"


def onboard_member(fleet_root: Path, member_id: str) -> OnboardResult:
    # PLR0911: Condensed return logic
    by_id = catalog_by_id()
    if member_id not in by_id:
        return OnboardResult(member_id=member_id, success=False, message="Unknown id")

    member = by_id[member_id]
    name = _clone_name(member)
    target = (fleet_root / name).resolve()
    fleet_root.mkdir(parents=True, exist_ok=True)

    try:
        if target.exists():
            if not (target / ".git").is_dir():
                return OnboardResult(member_id=member_id, success=False, message="Not a git repo")
            r = _run_capture(["git", "-C", str(target), "pull", "--ff-only"], cwd=target)
            if r.returncode != 0:
                return OnboardResult(member_id=member_id, success=False, message="pull failed")
        else:
            url = _clone_url(member.github_repo)
            r = _run_capture(["git", "clone", url, str(target)], cwd=fleet_root)
            if r.returncode != 0:
                return OnboardResult(member_id=member_id, success=False, message="clone failed")

        ok, log_txt = _install_in_clone(member, target)
        st = load_state(fleet_root)
        st.members[member_id] = OnboardedMember(
            clone_path=str(target),
            onboarded_at=datetime.now(UTC).isoformat(),
            install_ok=ok,
            install_log=log_txt[-8000:] if len(log_txt) > 8000 else log_txt,
            last_webapp_pid=None,
        )
        save_state(fleet_root, st)
        return OnboardResult(
            member_id=member_id,
            success=ok,
            message="Onboarded",
            clone_path=str(target),
        )

    except Exception as e:
        return OnboardResult(member_id=member_id, success=False, message=str(e))


def onboard_many(fleet_root: Path, body: OnboardRequest) -> OnboardResponse:
    results: list[OnboardResult] = []
    for mid in body.member_ids:
        results.append(onboard_member(fleet_root, mid))
    ok = all(r.success for r in results)
    return OnboardResponse(success=ok, results=results)


def start_webapp(fleet_root: Path, body: WebappStartRequest) -> WebappStartResponse:
    # PLR0911: Consolidate validations
    by_id = catalog_by_id()
    if body.member_id not in by_id:
        return WebappStartResponse(
            success=False,
            message="Unknown member_id",
            pid=None,
            command=None,
        )
    member = by_id[body.member_id]
    if member.webapp is None:
        return WebappStartResponse(success=False, message="No webapp", pid=None, command=None)
    st = load_state(fleet_root)
    ob = st.members.get(body.member_id)
    if ob is None or not ob.install_ok:
        return WebappStartResponse(success=False, message="Not onboarded", pid=None, command=None)

    clone = Path(ob.clone_path)
    script = (clone / member.webapp.script_relative).resolve()
    if not str(script).startswith(str(clone.resolve())) or not script.is_file():
        return WebappStartResponse(success=False, message="Invalid script", pid=None, command=None)

    if sys.platform != "win32":
        return WebappStartResponse(
            success=False,
            message="Windows (PS1) only",
            pid=None,
            command=None,
        )

    cmd = ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script)]
    creationflags = getattr(subprocess, "CREATE_NEW_CONSOLE", 0)
    proc = subprocess.Popen(cmd, cwd=str(clone), creationflags=creationflags)
    ob.last_webapp_pid = proc.pid
    save_state(fleet_root, st)
    return WebappStartResponse(success=True, message="Started", pid=proc.pid, command=cmd)


def members_detail(fleet_root: Path) -> dict[str, Any]:
    st = load_state(fleet_root)
    return {k: v.model_dump() for k, v in st.members.items()}
