"""Render the cross-task, within-menu recoverability bridge.

The plot performs no fitting or statistical estimation.  It visualizes the
two recovered-headroom columns in Table 3.  Every row is normalized within
its own registered task: its fixed reference is 0 and its evaluator-only
per-query oracle is 100.  Absolute utility is never compared across rows.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image


HERE = Path(__file__).resolve().parent
DATA = HERE / "recoverability_bridge_data.csv"
OUT = HERE / "recoverability_bridge"

INK = "#24313A"
MID = "#6F7B83"
TRACK = "#D9E0E4"
BLUE = "#0072B2"          # Okabe--Ito blue
BLUE_LIGHT = "#8EC5E3"


def configure_style() -> None:
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Liberation Sans", "DejaVu Sans"],
            "font.size": 8.0,
            "axes.labelsize": 8.0,
            "xtick.labelsize": 7.2,
            "ytick.labelsize": 8.0,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
        }
    )


def load_and_validate() -> pd.DataFrame:
    frame = pd.read_csv(DATA)
    required = {"task", "kappa_dev", "kappa_tih"}
    if set(frame.columns) != required:
        raise ValueError(f"Expected columns {sorted(required)}, got {frame.columns.tolist()}.")
    if len(frame) != 5 or frame["task"].nunique() != 5:
        raise ValueError("Expected exactly five distinct registered task rows.")
    values = frame[["kappa_dev", "kappa_tih"]].to_numpy(dtype=float)
    if not np.isfinite(values).all() or (values < 0).any() or (values > 100).any():
        raise ValueError("Recovered-headroom values must be finite percentages in [0, 100].")
    return frame


def render(frame: pd.DataFrame) -> plt.Figure:
    # Single-column composition for the main paper. The data and normalization
    # remain identical to Table 3.
    frame = frame.copy()
    frame["task"] = [
        "Structured 2k",
        "Hyperlink 10k",
        "FEVER",
        "MuSiQue",
        "Dense replay",
    ]
    fig, ax = plt.subplots(figsize=(3.34, 2.08))
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    y = np.arange(len(frame), dtype=float)
    dev = frame["kappa_dev"].to_numpy(dtype=float)
    tih = frame["kappa_tih"].to_numpy(dtype=float)

    for row_y, dev_value, tih_value in zip(y, dev, tih):
        # The full gray bridge is the registered within-task headroom.
        ax.hlines(row_y, 0, 100, color=TRACK, linewidth=1.15, zorder=0)
        # The colored segment is the share recovered by the valid policy.
        ax.hlines(row_y - 0.07, 0, dev_value, color=BLUE_LIGHT, linewidth=1.8, zorder=1)
        # A short connector exposes the reference sensitivity without turning
        # heterogeneous diagnostic ranges into a common confidence interval.
        ax.plot(
            [tih_value, dev_value],
            [row_y + 0.07, row_y - 0.07],
            color=MID,
            linewidth=0.7,
            zorder=2,
        )
        ax.scatter(
            [dev_value],
            [row_y - 0.07],
            s=31,
            marker="o",
            facecolor=BLUE,
            edgecolor=INK,
            linewidth=0.65,
            zorder=4,
        )
        ax.scatter(
            [tih_value],
            [row_y + 0.07],
            s=24,
            marker="o",
            facecolor="white",
            edgecolor=INK,
            linewidth=0.85,
            zorder=3,
        )
        label = (
            f"{dev_value:.2f}%"
            if np.isclose(dev_value, tih_value)
            else f"{dev_value:.2f}% / {tih_value:.2f}%"
        )
        ax.text(
            max(dev_value, tih_value) + 2.6,
            row_y,
            label,
            ha="left",
            va="center",
            fontsize=6.3,
            color=INK,
            fontweight="bold",
        )

    ax.set_xlim(-1, 105)
    ax.set_ylim(len(frame) - 0.48, -1.03)
    ax.set_yticks(y, labels=frame["task"].tolist())
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xlabel("Recovered fixed-to-oracle headroom (%)", fontsize=7.0)
    ax.tick_params(axis="y", length=0, pad=4, colors=INK, labelsize=7.0)
    ax.tick_params(axis="x", length=2.5, width=0.6, colors=INK, pad=2)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color("#AEB8BE")
    ax.spines["bottom"].set_linewidth(0.6)

    # Compact dual-encoding legend; the 0 and 100 endpoint semantics are
    # carried by the axis and caption, avoiding a crowded single-column header.
    legend_y = -0.75
    ax.scatter([34.0], [legend_y], s=26, marker="o", facecolor=BLUE,
               edgecolor=INK, linewidth=0.65, clip_on=False, zorder=5)
    ax.text(37.0, legend_y, r"vs. $F_{\rm dev}$", va="center",
            ha="left", fontsize=6.4, color=INK)
    ax.scatter([62.0], [legend_y], s=21, marker="o", facecolor="white",
               edgecolor=INK, linewidth=0.85, clip_on=False, zorder=5)
    ax.text(65.0, legend_y, r"vs. $F_{\rm TIH}$", va="center",
            ha="left", fontsize=6.4, color=INK)

    fig.subplots_adjust(left=0.31, right=0.985, top=0.87, bottom=0.22)
    return fig


def main() -> None:
    configure_style()
    frame = load_and_validate()
    fig = render(frame)
    outputs = {
        "pdf": OUT.with_suffix(".pdf"),
        "svg": OUT.with_suffix(".svg"),
        "png": OUT.with_suffix(".png"),
    }
    fig.savefig(outputs["pdf"], bbox_inches=None)
    fig.savefig(outputs["svg"], bbox_inches=None)
    fig.savefig(outputs["png"], dpi=320, bbox_inches=None)
    plt.close(fig)

    gray_path = OUT.parent / f"{OUT.name}_grayscale.png"
    deut_path = OUT.parent / f"{OUT.name}_deuteranopia.png"
    with Image.open(outputs["png"]) as image:
        image.convert("L").save(gray_path)
        try:
            from colorspacious import cspace_convert

            rgb = np.asarray(image.convert("RGB"), dtype=float) / 255.0
            simulated = cspace_convert(
                rgb,
                {
                    "name": "sRGB1+CVD",
                    "cvd_type": "deuteranomaly",
                    "severity": 100,
                },
                "sRGB1",
            )
            simulated = np.clip(simulated * 255.0, 0, 255).astype(np.uint8)
            Image.fromarray(simulated).save(deut_path)
        except Exception:
            image.convert("RGB").save(deut_path)

    manifest = {
        "figure": "recoverability_bridge",
        "source_data": DATA.name,
        "script": Path(__file__).name,
        "semantics": {
            "row_normalization": "within registered task",
            "left_endpoint": "registered fixed reference = 0",
            "right_endpoint": "evaluator-only per-query oracle = 100",
            "filled_marker": "kappa_dev",
            "open_marker": "kappa_TIH",
            "absolute_utility_cross_task_comparison": False,
            "uncertainty_intervals_drawn": False,
        },
        "outputs": {key: {"path": path.name} for key, path in outputs.items()},
        "proofs": {
            "grayscale": {"path": gray_path.name},
            "deuteranopia": {"path": deut_path.name},
        },
    }
    manifest_path = OUT.parent / f"{OUT.name}_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
