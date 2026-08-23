#!/usr/bin/env python3
"""Redraw WorthIR Figures 4--7 from the released analysis tables."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Rectangle
from matplotlib.ticker import FuncFormatter, MultipleLocator
import numpy as np
import pandas as pd


BLUE = "#2F78A1"
NAVY = "#1F5A85"
TEAL = "#1B8E75"
ORANGE = "#D97706"
AMBER = "#B58B2A"
INDIGO = "#6676A8"
RED = "#B5524B"
BLACK = "#202A31"
GRAY = "#6C7880"
LIGHT = "#DCE2E8"
WHITE = "#FFFFFF"


def configure_style() -> None:
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "DejaVu Sans"],
            "mathtext.fontset": "stixsans",
            "font.size": 8.2,
            "axes.titlesize": 9.0,
            "axes.labelsize": 8.5,
            "xtick.labelsize": 7.5,
            "ytick.labelsize": 7.5,
            "legend.fontsize": 7.1,
            "axes.linewidth": 0.8,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
            "savefig.facecolor": "white",
        }
    )


def clean_axis(ax: plt.Axes, grid_axis: str | None = None) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    if grid_axis:
        ax.grid(axis=grid_axis, color=LIGHT, linewidth=0.65, zorder=0)
        ax.set_axisbelow(True)


def export(fig: plt.Figure, output: Path, stem: str, height_mm: float) -> None:
    output.mkdir(parents=True, exist_ok=True)
    fig.set_size_inches(183.0 / 25.4, height_mm / 25.4)
    for suffix, options in (
        ("pdf", {}),
        ("png", {"dpi": 600}),
    ):
        fig.savefig(
            output / f"{stem}.{suffix}",
            bbox_inches="tight",
            pad_inches=0.03,
            **options,
        )
    plt.close(fig)


def signed_points(value: float) -> str:
    if abs(value) < 0.005:
        return "0"
    return f"{value:+.2f}".replace("-", "−")


def figure4(data_root: Path, output: Path) -> None:
    source = data_root / "analyses/rq3_utility_sources/data/query_strata.csv"
    frame = pd.read_csv(source)
    names = {
        "no_effectiveness_gain": r"$\mathcal{S}_0$",
        "effectiveness_gain_not_worth_cost": r"$\mathcal{S}_1$",
        "cost_effective_acquisition": r"$\mathcal{S}_2$",
    }
    tasks = ["TREC-DL pooled", "FEVER", "MuSiQue", "2Wiki-Structured"]
    styles = [("#337C94", None), (AMBER, "...."), (INDIGO, "////")]
    fig, axes = plt.subplots(1, 4, sharey=True)
    fig.subplots_adjust(left=0.075, right=0.995, bottom=0.18, top=0.78, wspace=0.16)
    for panel, (ax, task) in enumerate(zip(axes, tasks)):
        rows = frame.loc[frame["task"] == task].set_index("query_stratum")
        values = np.array(
            [
                rows.loc[stratum, "utility_gain_contribution_per_query"] * 100
                for stratum in names
            ]
        )
        total = np.abs(values).sum()
        shares = values / total * 100 if total else np.zeros(3)
        for x, share, value, (color, hatch) in zip(
            range(3), shares, values, styles
        ):
            if abs(share) >= 0.05:
                ax.bar(
                    x,
                    share,
                    width=0.58,
                    color=color,
                    edgecolor=BLACK,
                    linewidth=0.55,
                    hatch=hatch,
                    zorder=3,
                )
            else:
                ax.scatter(x, 0, s=22, facecolor=WHITE, edgecolor=color, zorder=4)
            inside = abs(share) >= 18
            y = share - np.sign(share) * 6 if inside else (8 if share >= 0 else share - 8)
            ax.text(
                x,
                y,
                signed_points(value),
                ha="center",
                va="top" if inside and share > 0 else "bottom",
                color=WHITE if inside else BLACK,
                fontsize=7.3,
                fontweight="bold" if abs(value) >= 0.01 else "normal",
                zorder=5,
            )
        overall = float(rows["headline_utility_gain"].iloc[0]) * 100
        ax.axhline(0, color=BLACK, linewidth=0.9)
        ax.axhline(50, color=LIGHT, linewidth=0.6, zorder=0)
        ax.axhline(-50, color=LIGHT, linewidth=0.6, zorder=0)
        ax.set_xlim(-0.62, 2.62)
        ax.set_ylim(-55, 112)
        ax.set_xticks(range(3), list(names.values()))
        ax.tick_params(axis="x", length=0)
        ax.set_title(
            rf"{chr(65 + panel)}. {task}" + "\n" + rf"Overall $\Delta U$: {signed_points(overall)}",
            fontweight="bold",
            pad=7,
        )
        for spine in ax.spines.values():
            spine.set_visible(False)
    axes[0].set_yticks([-50, 0, 50, 100], ["−50%", "0", "50%", "100%"])
    axes[0].set_ylabel("Share of absolute contribution")
    for ax in axes[1:]:
        ax.tick_params(labelleft=False)
    fig.legend(
        handles=[
            Patch(facecolor=styles[0][0], edgecolor=BLACK, label=r"$\mathcal{S}_0$  No effectiveness gain"),
            Patch(facecolor=styles[1][0], edgecolor=BLACK, hatch="....", label=r"$\mathcal{S}_1$  Gain rejected by cost"),
            Patch(facecolor=styles[2][0], edgecolor=BLACK, hatch="////", label=r"$\mathcal{S}_2$  Paid route worthwhile"),
        ],
        loc="upper center",
        ncol=3,
        frameon=False,
        bbox_to_anchor=(0.54, 0.99),
    )
    export(fig, output, "figure4", 72)


def figure5(data_root: Path, output: Path) -> None:
    source = data_root / "analyses/rq4_robustness/data/cost_preference_curves.csv"
    frame = pd.read_csv(source)
    panels = [
        ("FEVER", "query-relative operator work", "A. FEVER", "Same predictor; actions recomputed every 0.005"),
        ("2Wiki-Structured", "declared within-task schedule", "B. 2Wiki-Structured", "Full refit and route reselection every 0.01"),
        ("MuSiQue", "query-relative token/scoring work", "C. MuSiQue: query-relative work", "Fixed actions; fixed route reselected every 0.01"),
        ("MuSiQue", "development-normalized additive work", "D. MuSiQue: development-normalized work", "Fixed actions; fixed route reselected every 0.01"),
    ]
    fig, axes = plt.subplots(2, 2)
    fig.subplots_adjust(left=0.095, right=0.992, top=0.89, bottom=0.13, hspace=0.38, wspace=0.22)
    for ax, (task, profile, title, note) in zip(axes.flat, panels):
        part = frame.loc[
            frame["task"].eq(task) & frame["cost_profile"].eq(profile)
        ].sort_values("lambda")
        x = part["lambda"].to_numpy()
        y = part["delta"].to_numpy() * 100
        ax.plot(x, y, color=NAVY, linewidth=1.55, zorder=2)
        marked = part.loc[part["low"].notna() & part["high"].notna()]
        my = marked["delta"].to_numpy() * 100
        ax.errorbar(
            marked["lambda"],
            my,
            yerr=np.vstack(
                [my - marked["low"].to_numpy() * 100, marked["high"].to_numpy() * 100 - my]
            ),
            fmt="o",
            ms=4.2,
            color=BLUE,
            mfc=BLUE,
            mec=WHITE,
            mew=0.6,
            capsize=2.2,
            linewidth=0.8,
            zorder=4,
        )
        primary = part.loc[np.isclose(part["lambda"], 0.08)].iloc[0]
        primary_y = float(primary["delta"]) * 100
        ax.axvspan(0.077, 0.083, color="#F7EDCF", alpha=0.75, zorder=0)
        ax.axvline(0.08, color=ORANGE, linewidth=0.8, zorder=1)
        ax.scatter(0.08, primary_y, marker="*", s=95, color=ORANGE, edgecolor=BLACK, linewidth=0.6, zorder=6)
        ax.annotate(
            rf"Primary $\lambda=0.08$: {primary_y:+.2f}",
            xy=(0.08, primary_y),
            xytext=(36, -18),
            textcoords="offset points",
            color=ORANGE,
            fontsize=7.0,
            fontweight="bold",
            arrowprops={"arrowstyle": "-", "color": ORANGE, "lw": 0.65},
        )
        ax.axhline(0, color=GRAY, linewidth=0.7, linestyle=(0, (4, 3)))
        ax.set_xlim(-0.012, 0.332)
        ax.set_xticks([0, 0.08, 0.16, 0.24, 0.32], ["0", "0.08", "0.16", "0.24", "0.32"])
        ax.set_title(title, loc="left", fontweight="bold", pad=8)
        ax.text(0.015, 0.97, note, transform=ax.transAxes, ha="left", va="top", color=GRAY, fontsize=6.6)
        clean_axis(ax, "y")
    fig.supxlabel(r"Cost preference $\lambda$", y=0.035)
    fig.supylabel(r"Mean gain over $F_{\mathrm{dev}}$ (utility points)", x=0.018)
    export(fig, output, "figure5", 116)


def figure6(data_root: Path, output: Path) -> None:
    source = data_root / "analyses/rq5_route_value/data/rq5_fever_gold_rank_band_routes.csv"
    frame = pd.read_csv(source)
    specs = [
        ("ce20_minus_bm25", "rank11_20", "BM25 ranks 11–20\nCE-20 vs BM25"),
        ("ce100_minus_ce20", "rank21_100", "BM25 ranks 21–100\nCE-100 vs CE-20"),
        ("hybrid_minus_ce100", "rank101_200", "BM25 ranks 101–200\nHybrid vs CE-100"),
    ]
    rows = []
    for contrast, band, label in specs:
        row = frame.loc[frame["contrast"].eq(contrast) & frame["gold_rank_band"].eq(band)].iloc[0]
        rows.append((row, f"{label}  ·  n={int(row['n']):,}"))
    absent = frame.loc[frame["gold_rank_band"].eq("absent_top200")]
    y = np.arange(4)[::-1]
    fig = plt.figure()
    grid = fig.add_gridspec(1, 2, width_ratios=(1.72, 1.0), wspace=0.13)
    gain = fig.add_subplot(grid[0, 0])
    share = fig.add_subplot(grid[0, 1], sharey=gain)
    fig.subplots_adjust(left=0.285, right=0.985, bottom=0.18, top=0.89)
    labels = []
    for index, (row, label) in enumerate(rows):
        yi = y[index]
        delta_e = float(row["mean_delta_quality"]) * 100
        delta_u = float(row["mean_delta_utility"]) * 100
        gain.plot([delta_u, delta_e], [yi - 0.11, yi + 0.11], color=LIGHT, lw=1.3)
        gain.scatter(delta_e, yi + 0.11, s=42, color=NAVY, edgecolor=WHITE, linewidth=0.65, zorder=3)
        gain.scatter(delta_u, yi - 0.11, s=40, marker="s", color=ORANGE, edgecolor=WHITE, linewidth=0.65, zorder=3)
        gain.text(delta_e + 1.2, yi + 0.11, f"{delta_e:.1f}", va="center", color=NAVY, fontsize=7.0)
        gain.text(delta_u - 1.2, yi - 0.11, f"{delta_u:.1f}", va="center", ha="right", color=ORANGE, fontsize=7.0)
        labels.append(label)
        positive = float(row["positive_delta_utility_share"]) * 100
        share.hlines(yi, 0, positive, color=TEAL, linewidth=2.3, alpha=0.8)
        share.scatter(positive, yi, s=44, color=TEAL, edgecolor=WHITE, linewidth=0.65)
        share.text(min(positive + 1.8, 102), yi, f"{positive:.1f}%", va="center", ha="left" if positive < 98 else "right", color=TEAL, fontsize=7.2, fontweight="bold")
    yi = y[3]
    low = float(absent["mean_delta_utility"].min()) * 100
    high = float(absent["mean_delta_utility"].max()) * 100
    gain.scatter(0, yi + 0.11, s=42, color=NAVY, edgecolor=WHITE, linewidth=0.65)
    gain.plot([low, high], [yi - 0.11, yi - 0.11], color=ORANGE, linewidth=3)
    gain.scatter([low, high], [yi - 0.11, yi - 0.11], marker="|", s=74, color=ORANGE)
    gain.text(1.2, yi + 0.11, "0.0", va="center", color=NAVY, fontsize=7.0)
    gain.text(high + 1.4, yi - 0.11, rf"$\Delta U$ ({low:.2f} → {high:.2f})".replace("-", "−"), va="center", color=ORANGE, fontsize=6.9)
    labels.append(f"Not in BM25 top 200\nAll paid routes vs BM25  ·  n={int(absent['n'].iloc[0]):,}")
    share.scatter(0, yi, s=44, color=TEAL, edgecolor=WHITE, linewidth=0.65)
    share.text(1.8, yi, "0.0%", va="center", color=TEAL, fontsize=7.2, fontweight="bold")
    gain.set_yticks(y, labels, linespacing=1.15)
    share.tick_params(axis="y", left=False, labelleft=False)
    gain.axvline(0, color=BLACK, linewidth=0.85)
    gain.set_xlim(-7, 78)
    gain.xaxis.set_major_locator(MultipleLocator(20))
    gain.set_xlabel("Mean gain over the reference route (points)")
    gain.set_title("A. Effectiveness and utility gain", loc="left", fontweight="bold", pad=8)
    gain.legend(
        handles=[
            Line2D([0], [0], marker="o", color="none", markerfacecolor=NAVY, label=r"Effectiveness gain $\Delta E$"),
            Line2D([0], [0], marker="s", color="none", markerfacecolor=ORANGE, label=r"Utility gain $\Delta U$"),
        ],
        loc="upper left",
        ncol=2,
        frameon=False,
    )
    share.set_xlim(0, 108)
    share.xaxis.set_major_locator(MultipleLocator(25))
    share.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x:.0f}%"))
    share.set_xlabel(r"Queries with $\Delta U>0$")
    share.set_title("B. Positive-utility frequency", loc="left", fontweight="bold", pad=8)
    for ax in (gain, share):
        ax.set_ylim(-0.52, 3.68)
        clean_axis(ax, "x")
    export(fig, output, "figure6", 91)


def figure7(data_root: Path, output: Path) -> None:
    latency = pd.read_csv(data_root / "analyses/rq2_policy_comparison/results/fever_online_latency.csv")
    utility = pd.read_csv(data_root / "analyses/rq2_policy_comparison/results/fever_same_menu_policy_comparison.csv")
    delta = dict(zip(utility["policy"], utility["delta_fixed"]))
    delta["fixed_ce100"] = 0.0
    latency["delta_u"] = latency["policy"].map(delta)
    latency["menu"] = latency["policy"].str.extract(r"(3|5)$", expand=False).fillna("–")
    fig = plt.figure()
    grid = fig.add_gridspec(1, 2, width_ratios=(1.08, 1.0), wspace=0.28)
    trade = fig.add_subplot(grid[0, 0])
    comp = fig.add_subplot(grid[0, 1])
    fig.subplots_adjust(left=0.09, right=0.985, bottom=0.18, top=0.88)
    baseline = float(latency.loc[latency["policy"].eq("fixed_ce100"), "online_mean_ms"].iloc[0])
    trade.add_patch(Rectangle((100, 0), baseline - 100, 2.3, facecolor=TEAL, alpha=0.055, edgecolor="none"))
    trade.axhline(0, color=BLACK, linewidth=0.9)
    trade.axvline(baseline, color=GRAY, linestyle="--", linewidth=0.9)
    family_color = {"qpp": TEAL, "extratrees": NAVY, "arr": RED, "fixed_ce100": BLACK}
    labels = {"fixed_ce100": "Fixed CE-100", "qpp3": "QPP-3", "extratrees3": "ExtraTrees-3", "arr3": "ARR-3", "qpp5": "QPP-5", "extratrees5": "ExtraTrees-5", "arr5": "ARR-5"}
    for row in latency.itertuples(index=False):
        family = row.policy.rstrip("35") if row.policy != "fixed_ce100" else row.policy
        color = family_color[family]
        marker = {"3": "o", "5": "s", "–": "*"}[row.menu]
        trade.scatter(
            row.online_mean_ms,
            row.delta_u * 100,
            marker=marker,
            s=55 if row.menu != "–" else 100,
            facecolor="none" if row.menu == "5" else color,
            edgecolor=color if row.menu == "5" else WHITE,
            linewidth=1.4 if row.menu == "5" else 0.7,
            zorder=4,
        )
    trade.annotate(
        "Fixed CE-100",
        xy=(baseline, 0),
        xytext=(292, -0.72),
        ha="right",
        va="top",
        fontsize=7.0,
        arrowprops={"arrowstyle": "-", "color": GRAY, "lw": 0.6},
    )
    trade.text(253, 0.90, "QPP-3/5  +0.56", color=TEAL, fontsize=7.0, fontweight="bold")
    trade.text(184, 1.43, "ExtraTrees-3/5  +1.17/+1.11", color=NAVY, fontsize=7.0, fontweight="bold")
    trade.text(125, -3.78, "ARR-3  −4.01", color=RED, fontsize=7.0, fontweight="bold")
    trade.text(220, -5.55, "ARR-5  −5.82", color=RED, fontsize=7.0, fontweight="bold")
    trade.text(106, 1.5, "faster and higher utility", color=TEAL, fontsize=6.8, va="top")
    trade.set_xlim(100, 315)
    trade.set_ylim(-6.6, 2.3)
    trade.xaxis.set_major_locator(MultipleLocator(50))
    trade.yaxis.set_major_locator(MultipleLocator(2))
    trade.set_xlabel("Estimated mean warm-online latency (ms)")
    trade.set_ylabel("Mean utility gain over fixed CE-100 (points)")
    trade.set_title("A. Latency–utility trade-off", loc="left", fontweight="bold", pad=8)
    clean_axis(trade, "both")
    order = list(labels)
    bars = latency.set_index("policy").loc[order].reset_index()
    y = np.arange(len(bars))[::-1]
    comp.barh(y, bars["route_component_mean_ms"], height=0.56, color=BLUE, label="Selected-route execution")
    comp.barh(y, bars["router_mean_ms"], left=bars["route_component_mean_ms"], height=0.56, color=ORANGE, label="Router overhead")
    for yi, total in zip(y, bars["online_mean_ms"]):
        comp.text(total + 4, yi, f"{total:.1f}", va="center", fontsize=6.9)
    comp.axvline(baseline, color=GRAY, linestyle="--", linewidth=0.9)
    comp.axhline(2.5, color=LIGHT, linewidth=0.9)
    comp.set_yticks(y, [labels[key] for key in order])
    comp.set_xlim(0, 335)
    comp.xaxis.set_major_locator(MultipleLocator(100))
    comp.set_xlabel("Mean latency (ms)")
    comp.set_title("B. Latency decomposition", loc="left", fontweight="bold", pad=8)
    comp.legend(loc="upper left", ncol=2, frameon=False)
    clean_axis(comp, "x")
    export(fig, output, "figure7", 96)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    configure_style()
    figure4(args.data_root.resolve(), args.output_dir.resolve())
    figure5(args.data_root.resolve(), args.output_dir.resolve())
    figure6(args.data_root.resolve(), args.output_dir.resolve())
    figure7(args.data_root.resolve(), args.output_dir.resolve())
    print(json.dumps({"figures": [4, 5, 6, 7], "output": str(args.output_dir.resolve())}))


if __name__ == "__main__":
    main()
