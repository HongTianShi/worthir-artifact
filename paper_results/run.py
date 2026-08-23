#!/usr/bin/env python3
"""Set up and validate the WorthIR paper results."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import venv
from pathlib import Path


ROOT = Path(__file__).resolve().parent
VENV = ROOT / ".venv"
REQUIREMENTS_LOCK = ROOT / "requirements-lock.txt"


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
        print("Creating paper_results/.venv ...", flush=True)
        venv.EnvBuilder(with_pip=True).create(VENV)
    expected = REQUIREMENTS_LOCK.read_text(encoding="utf-8")
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
                "--require-hashes",
                "-r",
                str(REQUIREMENTS_LOCK),
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
        raise SystemExit("WorthIR requires Python 3.10 or newer.")

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
        raise SystemExit(f"Validation failed; see {report}")
    print("PASS: paper results recomputed from released ledgers and frozen readouts")
    print(f"Result index: {output / 'INDEX.md'}")
    print(f"Paper figures and tables: {output / 'paper'}")
    print(f"RQ2--RQ5 summaries: {output / 'rqs'}")
    print(f"Validation report: {report}")


if __name__ == "__main__":
    main()
