#!/usr/bin/env python3
"""Install the CPU-only environment for the FiQA-Compression260 replay."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
TORCH_VERSION = "2.12.1"
CPU_INDEX = "https://download.pytorch.org/whl/cpu"


def run(*arguments: str) -> None:
    command = [sys.executable, "-m", "pip", *arguments]
    print("+ " + " ".join(command), flush=True)
    subprocess.run(command, check=True)


def main() -> None:
    torch_arguments = ["install", "--disable-pip-version-check", f"torch=={TORCH_VERSION}"]
    if sys.platform != "darwin":
        torch_arguments.extend(["--index-url", CPU_INDEX])
    run(*torch_arguments)
    run("install", "--disable-pip-version-check", "-r", str(HERE / "requirements.txt"))
    print("FiQA-Compression260 CPU environment is ready.")


if __name__ == "__main__":
    main()
