"""根据运行方式选择向用户显示的命令。"""

from __future__ import annotations

import sys
from pathlib import Path


def installed_mode(root: Path) -> bool:
    """判断 WorthIR 是否从安装包运行。"""

    return not (root / "paper_results").is_dir()


def launcher_command(root: Path, shell: str = "native") -> str:
    """返回指定终端应使用的公开命令。"""

    if installed_mode(root):
        return "worthir"
    if shell == "native":
        shell = "powershell" if sys.platform == "win32" else "posix"
    if shell == "powershell":
        return ".\\worthir.cmd"
    if shell == "posix":
        return "./worthir"
    raise ValueError(f"未知终端：{shell}")
