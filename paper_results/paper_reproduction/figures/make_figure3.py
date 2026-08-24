#!/usr/bin/env python3
"""Redraw the manuscript's FEVER route-mix decomposition figure."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


MIX_INDIGO = "#6676A8"
MATCH_CYAN = "#2B8EAD"
GRAPHITE = "#1F2933"
GRID = "#DCE2E8"


def configure_style() -> None:
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "DejaVu Sans"],
            "font.size": 8.2,
            "axes.titlesize": 9.0,
            "axes.labelsize": 8.5,
            "xtick.labelsize": 7.6,
            "ytick.labelsize": 7.6,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def signed(value: float) -> str:
    return f"{value:+.2f}".replace("-", "−")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    frame = pd.read_csv(args.input)
    required = {"menu", "policy", "mix", "matching", "net_delta_u"}
    if not required.issubset(frame.columns):
        raise RuntimeError(f"missing columns: {sorted(required - set(frame.columns))}")
    if not np.allclose(
        frame["mix"] + frame["matching"], frame["net_delta_u"], atol=1e-12
    ):
        raise RuntimeError("route-mix and matching terms do not close to net delta U")

    configure_style()
    styles = {
        "ExtraTrees": (MATCH_CYAN, "o", "-"),
        "QPP": (MIX_INDIGO, "s", (0, (4, 2))),
        "ARR": ("#59636F", "^", (0, (1.5, 1.8))),
    }
    fig, axes = plt.subplots(1, 2, sharey=True, figsize=(7.20, 3.23))
    fig.subplots_adjust(left=0.12, right=0.97, bottom=0.20, top=0.88, wspace=0.10)
    x = np.array([0.0, 1.0, 2.0])
    labels = ["Fixed\nreference", "Route-mix\nterm", "Net after\nmatching"]
    for ax, menu, title in zip(
        axes, (3, 5), ("A. Three-route setting", "B. Five-route setting")
    ):
        subset = frame.loc[frame["menu"].eq(menu)]
        ax.axhspan(-9.0, 0.0, color="#F5F5FA", zorder=0)
        ax.axhspan(0.0, 2.0, color="#F2F8FA", zorder=0)
        ax.axhline(0.0, color=GRAPHITE, linewidth=1.0, zorder=1)
        for name, (color, marker, linestyle) in styles.items():
            row = subset.loc[subset["policy"].str.startswith(name)].iloc[0]
            trajectory = 100.0 * np.array([0.0, row["mix"], row["net_delta_u"]])
            ax.plot(x, trajectory, color=color, linestyle=linestyle, linewidth=1.8)
            ax.scatter(
                x[1:], trajectory[1:], marker=marker, s=45, color=color,
                edgecolor="white", linewidth=0.75, zorder=4
            )
            ax.text(
                2.07, trajectory[-1], f"{name}  {signed(trajectory[-1])}",
                va="center", fontsize=7.0, color=color, fontweight="bold"
            )
        ax.scatter(
            [0.0], [0.0], marker="D", s=38, facecolor="white",
            edgecolor=GRAPHITE, linewidth=0.9, zorder=5
        )
        ax.set_title(title, loc="left", fontweight="bold", pad=7)
        ax.set_xticks(x, labels)
        ax.set_xlim(-0.12, 2.62)
        ax.set_ylim(-9.0, 2.0)
        ax.grid(axis="y", color=GRID, linewidth=0.65, zorder=0)
        ax.spines[["top", "right"]].set_visible(False)
    axes[0].set_ylabel("Cumulative utility difference (points)")
    axes[1].spines["left"].set_visible(False)
    axes[1].tick_params(axis="y", left=False, labelleft=False)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output, bbox_inches="tight", pad_inches=0.03)
    plt.close(fig)


if __name__ == "__main__":
    main()
