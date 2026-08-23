#!/usr/bin/env python3
"""运行可复用 WorthIR 框架的示例和完整性检查。"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    os.environ["PYTHONIOENCODING"] = "utf-8"
    os.environ["PYTHONUTF8"] = "1"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "reproduced" / "framework",
    )
    args = parser.parse_args()
    if sys.version_info < (3, 10):
        raise SystemExit("WorthIR 需要 Python 3.10 或更高版本。")

    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    report = output / "validation.json"
    command = [
        sys.executable,
        str(ROOT / "scripts" / "validate_framework.py"),
        "--root",
        str(ROOT),
        "--output",
        str(report),
    ]
    print("+ " + " ".join(command), flush=True)
    subprocess.run(command, cwd=ROOT, check=True)
    result = json.loads(report.read_text(encoding="utf-8"))
    if result.get("status") != "PASS":
        raise SystemExit(f"验证失败；详见 {report}")
    print("通过：WorthIR 框架已就绪")
    print(f"报告：{report}")


if __name__ == "__main__":
    main()
