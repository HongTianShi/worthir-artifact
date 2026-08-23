#!/usr/bin/env python3
"""Export frozen manuscript graphics to the PDF names in PAPER_SPEC.json."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from PIL import Image


def image_to_pdf(source: Path, target: Path) -> None:
    with Image.open(source) as image:
        rgb = image.convert("RGB")
        rgb.save(target, "PDF", resolution=300.0)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assets", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    assets = args.assets.resolve()
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    conversions = {
        "figure1.png": "figure1.pdf",
        "appendix_figure_e1.png": "appendix_figure_e1.pdf",
        "appendix_figure_e2.png": "appendix_figure_e2.pdf",
        "appendix_figure_f1.png": "appendix_figure_f1.pdf",
    }
    for source_name, target_name in conversions.items():
        image_to_pdf(assets / source_name, output / target_name)
    shutil.copy2(assets / "appendix_figure_f2.pdf", output / "appendix_figure_f2.pdf")


if __name__ == "__main__":
    main()
