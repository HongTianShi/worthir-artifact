#!/usr/bin/env python3
"""离线创建 WorthIR 源码环境，并检查框架是否可以运行。"""

from __future__ import annotations

import os
import subprocess
import sys
import venv
from pathlib import Path


ROOT = Path(__file__).resolve().parent
VENV = ROOT / ".venv"

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    os.environ["PYTHONIOENCODING"] = "utf-8"
    os.environ["PYTHONUTF8"] = "1"


def _venv_python() -> Path:
    return VENV / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")


def main() -> None:
    if sys.version_info < (3, 10):
        raise SystemExit("WorthIR 需要 Python 3.10 或更高版本。")
    if not _venv_python().is_file():
        print(f"正在创建 {VENV}", flush=True)
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
    print("环境已就绪")
    print(f"下一步：{launcher} demo-custom")


if __name__ == "__main__":
    main()
