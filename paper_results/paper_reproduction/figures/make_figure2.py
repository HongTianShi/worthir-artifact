from __future__ import annotations

import json
import argparse
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
REPLAYS = ROOT / "replays"
OUT = Path(__file__).resolve().parent / "outputs"

LAMBDA = 0.08
EFFECTIVENESS_POINT_SCALE = 100.0

BLUE = "#2F6FA3"
BLUE_DARK = "#174A73"
ORANGE = "#D97706"
ORANGE_LIGHT = "#FFF3E3"
GRAY = "#707070"
GRID = "#D9E0E6"
BLACK = "#222222"

mpl.rcParams.update(
    {
        "font.family": "serif",
        "font.serif": ["Times New Roman", "DejaVu Serif"],
        "mathtext.fontset": "stix",
        "font.size": 9.0,
        "axes.titlesize": 11.0,
        "axes.labelsize": 9.5,
        "xtick.labelsize": 8.3,
        "ytick.labelsize": 8.3,
        "legend.fontsize": 8.0,
        "axes.linewidth": 0.8,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "none",
    }
)


def pareto_frontier(frame: pd.DataFrame) -> pd.DataFrame:
    """Return cost-ascending points not dominated in cost--effectiveness space."""
    ordered = frame.sort_values(["cost", "quality"], ascending=[True, False])
    keep = []
    best_quality = -np.inf
    for idx, row in ordered.iterrows():
        if row["quality"] > best_quality + 1e-12:
            keep.append(idx)
            best_quality = row["quality"]
    return ordered.loc[keep].sort_values("cost")


def add_utility_reference(
    ax,
    ref_cost: float,
    ref_quality: float,
    xlim,
    ylim,
    effectiveness_scale: float = 1.0,
):
    """Draw the iso-utility line through a reference point."""
    utility = ref_quality - LAMBDA * ref_cost
    xs = np.linspace(xlim[0], xlim[1], 300)
    ys = (utility + LAMBDA * xs) * effectiveness_scale
    ax.fill_between(
        xs,
        ys,
        ylim[1],
        where=ys <= ylim[1],
        color=ORANGE_LIGHT,
        alpha=0.62,
        zorder=0,
    )
    ax.plot(xs, ys, color=ORANGE, lw=1.15, ls=(0, (4, 3)), zorder=1)


def style_axis(ax, xlim, ylim, title, effectiveness_scale: float = 1.0):
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    if title:
        ax.set_title(title, loc="left", fontweight="bold", pad=7)
    ax.set_xlabel("Cost (task-specific units)")
    ylabel = (
        "Mean effectiveness (points)"
        if effectiveness_scale == EFFECTIVENESS_POINT_SCALE
        else "Mean effectiveness"
    )
    ax.set_ylabel(ylabel)
    grid_lw = 0.55 if effectiveness_scale == EFFECTIVENESS_POINT_SCALE else 0.65
    grid_alpha = 0.82 if effectiveness_scale == EFFECTIVENESS_POINT_SCALE else 1.0
    ax.grid(True, color=GRID, lw=grid_lw, alpha=grid_alpha, zorder=0)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def draw_route_points(
    ax,
    frame,
    label_offsets,
    frontier=True,
    effectiveness_scale: float = 1.0,
):
    if frontier:
        pf = pareto_frontier(frame)
        ax.plot(
            pf["cost"],
            pf["quality"] * effectiveness_scale,
            color=BLUE_DARK,
            lw=(1.35 if effectiveness_scale == EFFECTIVENESS_POINT_SCALE else 1.55),
            zorder=2,
        )
    ax.scatter(
        frame["cost"],
        frame["quality"] * effectiveness_scale,
        s=46,
        facecolor=BLUE,
        edgecolor="white",
        linewidth=0.7,
        zorder=4,
    )
    for _, row in frame.iterrows():
        offset = label_offsets[row["route"]]
        if offset is None:
            continue
        if len(offset) == 4:
            dx, dy, ha, leader = offset
        else:
            dx, dy, ha = offset
            leader = False
        ax.annotate(
            row["label"],
            (row["cost"], row["quality"] * effectiveness_scale),
            xytext=(dx, dy),
            textcoords="offset points",
            ha=ha,
            va="center",
            fontsize=8.1,
            color=BLACK,
            arrowprops=(
                dict(arrowstyle="-", color=GRAY, lw=0.65, shrinkA=2, shrinkB=4)
                if leader
                else None
            ),
            zorder=7,
        )


def fixed_choice_panel(
    ax,
    frame,
    title,
    xlim,
    ylim,
    quality_best,
    utility_best,
    label_offsets,
    effectiveness_scale=EFFECTIVENESS_POINT_SCALE,
):
    style_axis(ax, xlim, ylim, title, effectiveness_scale)
    qrow = frame.loc[frame.route == quality_best].iloc[0]
    urow = frame.loc[frame.route == utility_best].iloc[0]
    add_utility_reference(
        ax,
        qrow.cost,
        qrow.quality,
        xlim,
        ylim,
        effectiveness_scale,
    )
    draw_route_points(
        ax,
        frame,
        label_offsets,
        effectiveness_scale=effectiveness_scale,
    )

    ax.scatter(
        [qrow.cost],
        [qrow.quality * effectiveness_scale],
        s=105,
        facecolor="none",
        edgecolor=BLACK,
        linewidth=1.35,
        zorder=5,
    )
    ax.scatter(
        [urow.cost],
        [urow.quality * effectiveness_scale],
        s=110,
        marker="D",
        facecolor="none",
        edgecolor=ORANGE,
        linewidth=1.65,
        zorder=6,
    )


def adaptive_panel(
    ax,
    frame,
    title,
    xlim,
    ylim,
    fixed_point,
    adaptive_point,
    delta_ci,
    fixed_label,
    label_offsets,
    annotation_xy,
    arrow_rad=0.0,
    fixed_label_offset=(6, -13, "left"),
    adaptive_label_offset=(7, 9, "left"),
    effectiveness_scale=EFFECTIVENESS_POINT_SCALE,
):
    style_axis(ax, xlim, ylim, title, effectiveness_scale)
    add_utility_reference(
        ax,
        fixed_point[0],
        fixed_point[1],
        xlim,
        ylim,
        effectiveness_scale,
    )
    draw_route_points(
        ax,
        frame,
        label_offsets,
        effectiveness_scale=effectiveness_scale,
    )

    fixed_xy = (fixed_point[0], fixed_point[1] * effectiveness_scale)
    adaptive_xy = (adaptive_point[0], adaptive_point[1] * effectiveness_scale)

    ax.scatter(
        [fixed_xy[0]],
        [fixed_xy[1]],
        s=88,
        marker="s",
        facecolor="white",
        edgecolor=BLACK,
        linewidth=1.45,
        zorder=7,
    )
    ax.scatter(
        [adaptive_xy[0]],
        [adaptive_xy[1]],
        s=165,
        marker="*",
        facecolor=ORANGE,
        edgecolor=BLACK,
        linewidth=0.75,
        zorder=8,
    )
    ax.annotate(
        "",
        xy=adaptive_xy,
        xytext=fixed_xy,
        arrowprops=dict(
            arrowstyle="->",
            color=ORANGE,
            lw=2.0,
            shrinkA=5,
            shrinkB=6,
            connectionstyle=f"arc3,rad={arrow_rad}",
        ),
        zorder=6,
    )

    delta = (adaptive_point[1] - LAMBDA * adaptive_point[0]) - (
        fixed_point[1] - LAMBDA * fixed_point[0]
    )
    delta_points = delta * effectiveness_scale
    ci_points = tuple(v * effectiveness_scale for v in delta_ci)
    text = (
        rf"Utility gain  $\Delta U={delta_points:+.2f}$"
        + "\n"
        + rf"95% interval ({ci_points[0]:.2f} $\rightarrow$ {ci_points[1]:.2f})"
    )
    ax.text(
        annotation_xy[0],
        annotation_xy[1],
        text,
        transform=ax.transAxes,
        color=ORANGE,
        fontsize=7.7,
        linespacing=1.2,
        va="bottom",
        bbox=dict(boxstyle="round,pad=.30", fc=ORANGE_LIGHT, ec="none"),
        zorder=10,
    )
    ax.annotate(
        fixed_label,
        fixed_xy,
        xytext=fixed_label_offset[:2],
        textcoords="offset points",
        fontsize=7.2,
        color=BLACK,
        ha=fixed_label_offset[2],
        va="top",
        zorder=9,
    )
    ax.annotate(
        "Adaptive",
        adaptive_xy,
        xytext=adaptive_label_offset[:2],
        textcoords="offset points",
        fontsize=7.5,
        color=ORANGE,
        fontweight="bold",
        ha=adaptive_label_offset[2],
        va="bottom",
        zorder=9,
    )


def load_trec() -> pd.DataFrame:
    p = REPLAYS / "canonical_trec/organizer_private/data/test/2019/route_outcomes.parquet"
    raw = pd.read_parquet(p)
    means = raw.groupby("route_id", as_index=False).agg(
        quality=("raw_ndcg_at_10", "mean"), cost=("C_op", "mean")
    )
    labels = {
        "stop_bm25": "BM25",
        "dense_fusion": "Dense fusion",
        "cross_encoder": "Cross-encoder",
        "late_interaction": "ColBERTv2",
    }
    means["route"] = means["route_id"]
    means["label"] = means.route.map(labels)
    return means[["route", "label", "cost", "quality"]]


def load_fiqa() -> pd.DataFrame:
    p = REPLAYS / "dense_and_legacy_recoverability/analysis_results.json"
    data = json.loads(p.read_text(encoding="utf-8"))["compression_diagnostic"]
    frame = pd.DataFrame(data).rename(columns={"view": "route", "raw_ndcg": "quality"})
    labels = {
        "summary": "Summary",
        "binary sign": "Binary",
        "IVF-PQ": "IVF-PQ",
        "trunc-96 fp32": "Trunc-96",
        "int8 dense": "Int8 dense",
        "trunc-192 fp32": "Trunc-192",
        "full dense": "Full dense",
        "cross-encoder rerank": "Cross-encoder",
    }
    frame["label"] = frame.route.map(labels)
    return frame[["route", "label", "cost", "quality"]]


def load_fever():
    actions = pd.read_csv(REPLAYS / "fever/frozen_results/registered_actions_lambda08.csv")
    outcomes = pd.read_parquet(REPLAYS / "fever/organizer_private/test_outcomes.parquet")[
        ["query_uid", "route", "raw_ndcg_10"]
    ]
    costs = pd.read_parquet(REPLAYS / "fever/organizer_private/route_costs.parquet")[
        ["query_uid", "route", "cost_work"]
    ]
    ledger = outcomes.merge(costs, on=["query_uid", "route"], validate="one_to_one")
    frame = ledger.groupby("route", as_index=False).agg(
        quality=("raw_ndcg_10", "mean"), cost=("cost_work", "mean")
    )
    labels = {
        "bm25": "BM25",
        "bi200": "Bi-encoder",
        "ce20": "CE-20",
        "ce100": "CE-100",
        "hybrid": "Hybrid",
    }
    frame["label"] = frame.route.map(labels)
    selected = (
        actions.merge(
            ledger,
            left_on=["query_uid", "selected_route"],
            right_on=["query_uid", "route"],
            validate="one_to_one",
        )
    )
    adaptive = (selected.cost_work.mean(), selected.raw_ndcg_10.mean())
    fixed_row = frame.loc[frame.route == "ce100"].iloc[0]
    fixed = (fixed_row.cost, fixed_row.quality)
    return frame[["route", "label", "cost", "quality"]], fixed, adaptive


def load_structured():
    outcomes = pd.read_parquet(REPLAYS / "structured_v2/organizer_private/data/outcomes.parquet")
    actions = pd.read_parquet(
        REPLAYS / "structured_v2/organizer_private/audit_sources/frozen_oof_query_actions.parquet"
    )
    frame = outcomes.groupby("view", as_index=False).agg(
        quality=("raw_quality", "mean"), cost=("declared_cost", "mean")
    ).rename(columns={"view": "route"})
    labels = {
        "summary": "Summary",
        "one_hop": "One-hop",
        "two_hop": "Two-hop",
        "full_context": "Full context",
        "ce": "Cross-encoder",
    }
    frame["label"] = frame.route.map(labels)

    ref_rows = actions[["query_uid", "f_dev_view"]].merge(
        outcomes,
        left_on=["query_uid", "f_dev_view"],
        right_on=["query_uid", "view"],
        validate="one_to_one",
    )
    fixed = (ref_rows.declared_cost.mean(), ref_rows.raw_quality.mean())
    adaptive = (actions.selected_cost.mean(), actions.selected_raw_quality.mean())
    return frame[["route", "label", "cost", "quality"]], fixed, adaptive


def save_figure(fig, stem):
    fig.savefig(OUT / f"{stem}.pdf", bbox_inches="tight", pad_inches=0.03)
    fig.savefig(OUT / f"{stem}.svg", bbox_inches="tight", pad_inches=0.03)
    fig.savefig(OUT / f"{stem}.png", dpi=600, bbox_inches="tight", pad_inches=0.03)


def save_panel_figure(fig, stem):
    """Export a panel on a fixed canvas so LaTeX subfigures align exactly."""
    fig.savefig(OUT / f"{stem}.pdf", facecolor="white")
    fig.savefig(OUT / f"{stem}.svg", facecolor="white")
    fig.savefig(OUT / f"{stem}.png", dpi=600, facecolor="white")


def add_fixed_choice_legend(ax):
    handles = [
        Line2D(
            [0],
            [0],
            marker="o",
            color=BLUE_DARK,
            markerfacecolor=BLUE,
            markeredgecolor="white",
            lw=1.35,
            label="Available routes / Pareto curve",
        ),
        Line2D(
            [0],
            [0],
            marker="o",
            color="none",
            markerfacecolor="none",
            markeredgecolor=BLACK,
            markersize=7,
            label="Effectiveness-best",
        ),
        Line2D(
            [0],
            [0],
            marker="D",
            color="none",
            markerfacecolor="none",
            markeredgecolor=ORANGE,
            markersize=6.5,
            label="Utility-best",
        ),
        Line2D(
            [0],
            [0],
            color=ORANGE,
            ls=(0, (4, 3)),
            lw=1.15,
            label=r"Equal utility ($\lambda=0.08$); higher is better",
        ),
    ]
    ax.legend(
        handles=handles,
        loc="lower right",
        bbox_to_anchor=(0.99, 0.02),
        frameon=False,
        fontsize=6.9,
        handlelength=2.3,
        borderpad=0.45,
        labelspacing=0.42,
    )


def add_available_routes_legend(ax):
    handles = [
        Line2D(
            [0],
            [0],
            marker="o",
            color=BLUE_DARK,
            markerfacecolor=BLUE,
            markeredgecolor="white",
            lw=1.35,
            label="Available routes / Pareto curve",
        ),
        Line2D(
            [0],
            [0],
            color=ORANGE,
            ls=(0, (4, 3)),
            lw=1.15,
            label=r"Equal utility ($\lambda=0.08$); higher is better",
        ),
    ]
    ax.legend(
        handles=handles,
        loc="lower right",
        bbox_to_anchor=(0.985, 0.315),
        ncol=1,
        frameon=False,
        fontsize=7.1,
        handlelength=2.2,
        labelspacing=0.35,
        borderpad=0.2,
    )


def draw_trec_profile(ax, trec, title=""):
    fixed_choice_panel(
        ax,
        trec,
        title,
        (-0.035, 1.07),
        (40.0, 73.5),
        "cross_encoder",
        "cross_encoder",
        {
            "stop_bm25": (5, 9, "left"),
            "dense_fusion": (5, -10, "left"),
            "cross_encoder": (9, 19, "left"),
            "late_interaction": (-5, -12, "right"),
        },
    )


def draw_fiqa_profile(ax, fiqa, title=""):
    fixed_choice_panel(
        ax,
        fiqa,
        title,
        (-0.045, 1.105),
        (0.0, 41.5),
        "cross-encoder rerank",
        "int8 dense",
        {
            "summary": (5, 9, "left"),
            "binary sign": (0, 31, "center", True),
            "IVF-PQ": (0, -21, "center", True),
            "trunc-96 fp32": (10, -5, "left", True),
            "int8 dense": (0, 16, "center"),
            "trunc-192 fp32": (13, -16, "left", True),
            "full dense": (0, 18, "center", True),
            "cross-encoder rerank": (-8, -18, "right"),
        },
    )


def draw_fever_profile(ax, fever, title=""):
    fever_frame, fever_fixed, fever_adaptive = fever
    adaptive_panel(
        ax,
        fever_frame,
        title,
        (-0.03, 0.61),
        (58.5, 84.5),
        fever_fixed,
        fever_adaptive,
        (0.0097, 0.0125),
        "Fixed CE-100",
        {
            "bm25": (5, 9, "left"),
            "bi200": (-5, -12, "right"),
            "ce20": (5, -12, "left"),
            "ce100": None,
            "hybrid": (-5, 10, "right"),
        },
        (0.035, 0.045),
    )


def draw_structured_profile(ax, structured, title=""):
    struct_frame, struct_fixed, struct_adaptive = structured
    adaptive_panel(
        ax,
        struct_frame,
        title,
        (-0.045, 1.02),
        (69.0, 97.5),
        struct_fixed,
        struct_adaptive,
        (0.0217, 0.0315),
        "OOF fixed reference",
        {
            "summary": (5, -10, "left"),
            "one_hop": (-8, -15, "right"),
            "two_hop": (12, 12, "left", True),
            "full_context": (5, -10, "left"),
            "ce": (-5, 10, "right"),
        },
        (0.035, 0.045),
        arrow_rad=0.25,
        adaptive_label_offset=(-2, 13, "center"),
    )


def build_fixed_route_figure(trec, fiqa):
    fig, axes = plt.subplots(1, 2, figsize=(7.25, 3.40))
    draw_trec_profile(axes[0], trec, "A. TREC-DL 2019")
    draw_fiqa_profile(axes[1], fiqa, "B. FiQA-Compression260")
    add_fixed_choice_legend(axes[0])
    fig.subplots_adjust(left=0.085, right=0.99, top=0.90, bottom=0.16, wspace=0.22)
    save_figure(fig, "fig_cost_quality_fixed_routes")
    plt.close(fig)


def build_adaptive_figure(fever, structured):
    fig, axes = plt.subplots(1, 2, figsize=(7.25, 3.25))
    draw_fever_profile(axes[0], fever, "C. FEVER")
    draw_structured_profile(axes[1], structured, "D. 2Wiki-Structured")
    add_available_routes_legend(axes[1])
    fig.subplots_adjust(left=0.08, right=0.99, top=0.90, bottom=0.16, wspace=0.20)
    save_figure(fig, "fig_cost_quality_adaptive_policies")
    plt.close(fig)


def build_profile_subfigures(trec, fiqa, fever, structured):
    panel_specs = [
        ("fig_profile_trec", lambda ax: draw_trec_profile(ax, trec), add_fixed_choice_legend),
        ("fig_profile_fiqa", lambda ax: draw_fiqa_profile(ax, fiqa), None),
        ("fig_profile_fever", lambda ax: draw_fever_profile(ax, fever), None),
        (
            "fig_profile_2wiki",
            lambda ax: draw_structured_profile(ax, structured),
            add_available_routes_legend,
        ),
    ]
    for stem, draw_panel, add_legend in panel_specs:
        fig, ax = plt.subplots(figsize=(3.55, 2.75))
        draw_panel(ax)
        if add_legend is not None:
            add_legend(ax)
        fig.subplots_adjust(left=0.18, right=0.985, top=0.975, bottom=0.19)
        save_panel_figure(fig, stem)
        plt.close(fig)


def build_combined_profile_preview(trec, fiqa, fever, structured):
    fig, axes = plt.subplots(2, 2, figsize=(7.25, 5.75))
    draw_trec_profile(axes[0, 0], trec, "A. TREC-DL 2019")
    draw_fiqa_profile(axes[0, 1], fiqa, "B. FiQA-Compression260")
    draw_fever_profile(axes[1, 0], fever, "C. FEVER")
    draw_structured_profile(axes[1, 1], structured, "D. 2Wiki-Structured")
    add_fixed_choice_legend(axes[0, 0])
    add_available_routes_legend(axes[1, 1])
    fig.subplots_adjust(
        left=0.09,
        right=0.99,
        top=0.95,
        bottom=0.10,
        wspace=0.22,
        hspace=0.34,
    )
    save_figure(fig, "fig_effectiveness_cost_profiles_2x2_preview")
    plt.close(fig)


def write_summary(frames):
    records = []
    for task, frame in frames.items():
        for _, row in frame.iterrows():
            records.append(
                {
                    "task": task,
                    "item_type": "fixed_route",
                    "item": row.route,
                    "cost": row.cost,
                    "quality": row.quality,
                    "utility_lambda_0_08": row.quality - LAMBDA * row.cost,
                }
            )
    pd.DataFrame(records).to_csv(OUT / "plotted_fixed_route_values.csv", index=False)


def main():
    global OUT
    parser = argparse.ArgumentParser(
        description="Redraw the manuscript's four-panel Figure 2."
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    OUT = args.output.resolve().parent
    OUT.mkdir(parents=True, exist_ok=True)
    trec = load_trec()
    fiqa = load_fiqa()
    fever = load_fever()
    structured = load_structured()
    write_summary(
        {
            "TREC-DL 2019": trec,
            "FiQA-Compression260": fiqa,
            "FEVER": fever[0],
            "2Wiki-Structured": structured[0],
        }
    )
    build_fixed_route_figure(trec, fiqa)
    build_adaptive_figure(fever, structured)
    build_profile_subfigures(trec, fiqa, fever, structured)
    build_combined_profile_preview(trec, fiqa, fever, structured)
    generated = OUT / "fig_effectiveness_cost_profiles_2x2_preview.pdf"
    if generated != args.output.resolve():
        generated.replace(args.output.resolve())
    print(f"Wrote {args.output.resolve()}")


if __name__ == "__main__":
    main()
