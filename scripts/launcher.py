"""Select the command name shown to source and installed users."""

from __future__ import annotations

import sys
from pathlib import Path


def installed_mode(root: Path) -> bool:
    """Return whether WorthIR is running from an installed package."""

    return not (root / "paper_results").is_dir()


def launcher_command(root: Path, shell: str = "native") -> str:
    """Return the public command for the requested shell."""

    if installed_mode(root):
        return "worthir"
    if shell == "native":
        shell = "powershell" if sys.platform == "win32" else "posix"
    if shell == "powershell":
        return ".\\worthir.cmd"
    if shell == "posix":
        return "./worthir"
    raise ValueError(f"unknown shell: {shell}")
