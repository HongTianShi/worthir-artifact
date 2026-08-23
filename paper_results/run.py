#!/usr/bin/env python3
"""配置并验证 WorthIR 论文结果。"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import venv
from pathlib import Path


ROOT = Path(__file__).resolve().parent
VENV = ROOT / ".venv"
REQUIREMENTS = ROOT / "requirements.txt"

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    os.environ["PYTHONIOENCODING"] = "utf-8"
    os.environ["PYTHONUTF8"] = "1"


def environment_python() -> Path:
    if sys.platform == "win32":
        return VENV / "Scripts" / "python.exe"
    return VENV / "bin" / "python"


def run(command: list[str]) -> None:
    print("+ " + " ".join(command), flush=True)
    subprocess.run(command, cwd=ROOT, check=True)


def prepare_environment() -> Path:
    python = environment_python()
    if not python.is_file():
        print("正在创建 paper_results/.venv……", flush=True)
        venv.EnvBuilder(with_pip=True).create(VENV)
    expected = REQUIREMENTS.read_text(encoding="utf-8")
    stamp = VENV / ".worthir-requirements"
    current = stamp.read_text(encoding="utf-8") if stamp.is_file() else ""
    if current != expected:
        run(
            [
                str(python),
                "-m",
                "pip",
                "install",
                "--disable-pip-version-check",
                "-r",
                str(REQUIREMENTS),
            ]
        )
        stamp.write_text(expected, encoding="utf-8")
    return python


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--use-current-python", action="store_true")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "reproduced",
    )
    args = parser.parse_args()
    if sys.version_info < (3, 10):
        raise SystemExit("WorthIR 需要 Python 3.10 或更高版本。")

    python = Path(sys.executable) if args.use_current_python else prepare_environment()
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    report = output / "validation.json"
    run(
        [
            str(python),
            str(ROOT / "scripts" / "validate_results.py"),
            "--root",
            str(ROOT),
            "--output",
            str(report),
            "--work-dir",
            str(output),
        ]
    )
    result = json.loads(report.read_text(encoding="utf-8"))
    if result.get("status") != "PASS":
        raise SystemExit(f"验证失败；详见 {report}")
    print("通过：WorthIR 论文结果已复现")
    print(f"论文图表：{output / 'paper'}")
    print(f"RQ2--RQ5 摘要：{output / 'rqs'}")
    print(f"校验报告：{report}")


if __name__ == "__main__":
    main()
