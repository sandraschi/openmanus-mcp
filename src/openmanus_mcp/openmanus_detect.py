"""Detect a valid OpenManus checkout on disk."""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class OpenManusInstall:
    """Structured result for OpenManus path validation."""

    root: Path
    has_main_py: bool
    has_config_example: bool
    python_min_hint: str

    @property
    def looks_valid(self) -> bool:
        return self.has_main_py and self.root.is_dir()


def describe_openmanus(root: Path | None) -> OpenManusInstall | None:
    """Return install info or None if root is unset."""
    if root is None:
        return None
    r = root.resolve()
    return OpenManusInstall(
        root=r,
        has_main_py=(r / "main.py").is_file(),
        has_config_example=(r / "config" / "config.example.toml").is_file(),
        python_min_hint="3.12 (per upstream README)",
    )
