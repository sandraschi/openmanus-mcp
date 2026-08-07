"""Detect a valid OpenManus checkout on disk."""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class OpenManusInfo:
    """Structured result for OpenManus path validation."""

    root: Path
    has_main_py: bool
    has_config_example: bool
    python_min_hint: str

    @property
    def looks_valid(self) -> bool:
        return self.has_main_py and self.root.is_dir()


def describe_openmanus(root: Path | None) -> OpenManusInfo | None:
    """Return install info or None if root is unset."""
    if root is None:
        return None
    r = root.resolve()
    return OpenManusInfo(
        root=r,
        has_main_py=(r / "main.py").is_file(),
        has_config_example=(r / "config" / "config.example.toml").is_file(),
        python_min_hint="3.12 (per upstream README)",
    )


def main() -> None:
    import sys

    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    info = describe_openmanus(target)
    if info:
        print(f"Root: {info.root}")
        print(f"Valid: {info.looks_valid}")
        print(f"Main.py: {info.has_main_py}")
        print(f"Config: {info.has_config_example}")
    else:
        print("No path provided or path invalid.")


if __name__ == "__main__":
    main()
