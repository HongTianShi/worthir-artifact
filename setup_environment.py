#!/usr/bin/env python3
"""Create WorthIR's local Python environment and verify it in one command."""

from __future__ import annotations

import subprocess
import sys
import venv
from pathlib import Path


ROOT = Path(__file__).resolve().parent
VENV = ROOT / ".venv"


def _venv_python() -> Path:
    return VENV / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")


def main() -> None:
    if sys.version_info < (3, 10):
        raise SystemExit("WorthIR requires Python 3.10 or newer.")
    if not _venv_python().is_file():
        print(f"Creating {VENV}", flush=True)
        venv.EnvBuilder(with_pip=False).create(VENV)
    python = _venv_python()
    command = [
        str(python),
        "-c",
        "import site; print(site.getsitepackages()[0])",
    ]
    site_packages = Path(
        subprocess.check_output(command, text=True, cwd=ROOT).strip()
    )
    (site_packages / "worthir-local.pth").write_text(
        str(ROOT / "src") + "\n", encoding="utf-8"
    )
    subprocess.run([str(python), str(ROOT / "worthir.py"), "doctor"], cwd=ROOT, check=True)
    launcher = ".\\worthir.cmd" if sys.platform == "win32" else "./worthir"
    print("READY")
    print(f"Next: {launcher} demo-custom")


if __name__ == "__main__":
    main()
