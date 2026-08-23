"""Draw WorthIR's timing contract from one frozen TREC-DL topic.

The visual argument is deliberately geometric:

    query + cheap signals -> locked route -> hidden complete ledger

The figure uses five numbered parts in a three-column layout.  Only the
commitment boundary receives strong visual emphasis; the former aggregate
footer is folded into the lower-right block.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.path import Path as MplPath
from matplotlib.patches import (
    Circle,
    Ellipse,
    FancyArrowPatch,
    PathPatch,
    Polygon,
    Rectangle,
)
import numpy as np


INK = "#171A1D"
MID = "#666B70"
LIGHT = "#D7D9DB"
PALE = "#F3F3F2"
BLUE = "#236A93"
ORANGE = "#A96300"
PURPLE = "#68578E"
GREEN = "#25785E"
RED = "#A8423C"


def setup_style() -> None:
    mpl.rcParams.update(
        {
            "font.family": "Times New Roman",
            "font.size": 7.5,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
        }
    )


def put(ax, x, y, value, **kwargs):
    defaults = dict(ha="left", va="center", color=INK, fontsize=7.5)
    defaults.update(kwargs)
    return ax.text(x, y, value, **defaults)


def rule(ax, xs, ys, width=0.75, dash=(0, (4, 3)), color=INK, zorder=2):
    ax.plot(xs, ys, lw=width, ls=dash, color=color, zorder=zorder)


def arrow(ax, start, end, color=INK, width=1.05):
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle="-|>",
            mutation_scale=8.5,
            linewidth=width,
            color=color,
            connectionstyle="arc3,rad=0",
            zorder=12,
        )
    )


def heading(ax, x, y, roman, title):
    put(
        ax,
        x,
        y,
        roman,
        fontsize=9.2,
        fontweight="bold",
        color="#8A8D90",
    )
    put(
        ax,
        x + 3.0,
        y,
        title,
        fontsize=9.2,
        fontweight="bold",
        color=INK,
    )


def draw_open_eye(ax, x, y, scale=1.0):
    # The y extent deliberately compensates for the wide figure canvas so the
    # eye remains anatomical rather than collapsing into a flat symbol.
    vertices = [
        (x - 3.0 * scale, y),
        (x - 1.55 * scale, y + 4.1 * scale),
        (x + 1.55 * scale, y + 4.1 * scale),
        (x + 3.0 * scale, y),
        (x + 1.55 * scale, y - 3.4 * scale),
        (x - 1.55 * scale, y - 3.4 * scale),
        (x - 3.0 * scale, y),
    ]
    codes = [
        MplPath.MOVETO,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.CURVE4,
    ]
    ax.add_patch(
        PathPatch(
            MplPath(vertices, codes),
            facecolor="white",
            edgecolor=BLUE,
            lw=1.15,
        )
    )
    ax.add_patch(
        Ellipse(
            (x, y),
            1.85 * scale,
            3.9 * scale,
            facecolor="#DCECF4",
            edgecolor=BLUE,
            lw=0.8,
        )
    )
    ax.add_patch(
        Ellipse(
            (x, y),
            0.78 * scale,
            1.65 * scale,
            facecolor=BLUE,
            edgecolor="none",
        )
    )
    ax.scatter(
        [x - 0.17 * scale],
        [y + 0.45 * scale],
        s=3.2,
        color="white",
        zorder=9,
    )


def draw_closed_eye(ax, x, y, scale=1.0):
    vertices = [
        (x - 3.0 * scale, y + 0.9 * scale),
        (x - 1.45 * scale, y - 2.8 * scale),
        (x + 1.45 * scale, y - 2.8 * scale),
        (x + 3.0 * scale, y + 0.9 * scale),
    ]
    codes = [
        MplPath.MOVETO,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.CURVE4,
    ]
    ax.add_patch(
        PathPatch(
            MplPath(vertices, codes),
            facecolor="none",
            edgecolor=PURPLE,
            lw=1.15,
        )
    )
    # Attach each lash to the cubic eyelid itself.  The center of this curve
    # is lower than the sides, so a shared starting y would leave it floating.
    lash_segments = (
        ((x - 2.2 * scale, y - 0.6 * scale), (x - 2.45 * scale, y - 2.25 * scale)),
        ((x, y - 1.88 * scale), (x, y - 3.50 * scale)),
        ((x + 2.2 * scale, y - 0.6 * scale), (x + 2.45 * scale, y - 2.25 * scale)),
    )
    for start, end in lash_segments:
        ax.plot(
            [start[0], end[0]],
            [start[1], end[1]],
            color=PURPLE,
            lw=0.85,
        )


def draw_lock(ax, x, y, scale=1.0):
    shackle_vertices = [
        (x - 1.15 * scale, y + 1.7 * scale),
        (x - 1.15 * scale, y + 6.2 * scale),
        (x + 1.15 * scale, y + 6.2 * scale),
        (x + 1.15 * scale, y + 1.7 * scale),
    ]
    shackle_codes = [
        MplPath.MOVETO,
        MplPath.CURVE4,
        MplPath.CURVE4,
        MplPath.CURVE4,
    ]
    ax.add_patch(
        PathPatch(
            MplPath(shackle_vertices, shackle_codes),
            facecolor="none",
            edgecolor=ORANGE,
            lw=1.05,
        )
    )
    ax.add_patch(
        Rectangle(
            (x - 1.75 * scale, y - 2.1 * scale),
            3.5 * scale,
            4.2 * scale,
            facecolor="white",
            edgecolor=ORANGE,
            lw=1.0,
        )
    )
    # A conventional keyhole: round head plus a short tapered stem.  Its
    # vertical dimensions compensate for the wide canvas, so it remains
    # recognizable after the full-width figure is reduced in the paper.
    ax.add_patch(
        Ellipse(
            (x, y + 0.15 * scale),
            0.52 * scale,
            1.00 * scale,
            facecolor=ORANGE,
            edgecolor="none",
        )
    )
    ax.add_patch(
        Polygon(
            [
                (x - 0.13 * scale, y - 0.10 * scale),
                (x + 0.13 * scale, y - 0.10 * scale),
                (x + 0.27 * scale, y - 1.12 * scale),
                (x - 0.27 * scale, y - 1.12 * scale),
            ],
            closed=True,
            facecolor=ORANGE,
            edgecolor="none",
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output-stem", required=True, type=Path)
    args = parser.parse_args()

    payload = json.loads(args.input.read_text(encoding="utf-8"))
    ex = payload["example"]
    route_by_id = {route["route_id"]: route for route in ex["routes"]}
    route_order = [
        "stop_bm25",
        "dense_fusion",
        "cross_encoder",
        "late_interaction",
    ]
    if set(route_by_id) != set(route_order):
        raise RuntimeError(f"Unexpected route menu: {sorted(route_by_id)}")

    setup_style()
    fig, ax = plt.subplots(figsize=(7.18, 3.72))
    fig.patch.set_facecolor("white")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")

    # Unequal semantic grid: two stacked left blocks, a full-height commitment
    # block, and two stacked evaluator blocks.  No colored panel backgrounds.
    x0, x1, x2, x3 = 1.0, 29.5, 53.5, 99.0
    # Pull the lower frame up to the content baseline; the former y=2 edge
    # left a conspicuous empty strip beneath the aggregate readout.
    y0, y3 = 7.0, 98.0
    y_left = 69.0
    y_right = 34.5
    rule(ax, [x0, x3, x3, x0, x0], [y0, y0, y3, y3, y0], width=0.85)
    rule(ax, [x1, x1], [y0, y3], width=0.72)
    # The commitment boundary is the only strong divider.
    rule(ax, [x2, x2], [y0, y3], width=1.2, dash=(0, (3, 2)))
    rule(ax, [x0, x1], [y_left, y_left], width=0.72)
    rule(ax, [x2, x3], [y_right, y_right], width=0.72)

    # I. Query: a compact real input anchor, not a prose block.
    heading(ax, 2.5, 94.0, "I", "QUERY")
    put(
        ax,
        2.5,
        88.6,
        "TREC-DL'19 / topic 527433",
        fontsize=6.8,
        color=MID,
    )
    put(
        ax,
        2.5,
        79.2,
        "types of dysarthria\nfrom cerebral palsy",
        fontsize=9.9,
        fontweight="bold",
        linespacing=1.13,
    )

    # II. Decision-time state: three compact glyphs encode signal shape,
    # visible information, and information withheld until after commitment.
    heading(ax, 2.5, 64.9, "II", "CHEAP SIGNALS")
    centers = (6.4, 14.9, 23.8)
    glyph_y = 54.8
    top = ex["bm25_top_score"]
    mean = ex["bm25_score_mean"]
    std = ex["bm25_score_std"]
    margin = ex["bm25_top1_top2_margin"]
    glyph = np.array(
        [top, top - margin, mean + 0.9 * std, mean + 0.25 * std, mean]
    )
    glyph = (glyph - glyph.min()) / (glyph.max() - glyph.min())
    for i, value in enumerate(glyph):
        ax.add_patch(
            Rectangle(
                (4.0 + i * 1.05, glyph_y - 2.6),
                0.58,
                1.5 + 5.0 * value,
                facecolor=BLUE,
                edgecolor="none",
            )
        )
    put(ax, centers[0], 46.8, "BM25 shape", ha="center", fontsize=6.5, fontweight="bold")
    put(ax, centers[0], 42.7, f"top {top:.2f}", ha="center", fontsize=5.9, color=MID)
    put(ax, centers[0], 38.9, f"mean {mean:.2f}", ha="center", fontsize=5.9, color=MID)
    put(ax, centers[0], 35.1, f"sd {std:.2f}", ha="center", fontsize=5.9, color=MID)
    put(ax, centers[0], 31.3, f"margin {margin:.3f}", ha="center", fontsize=5.9, color=MID)

    draw_open_eye(ax, centers[1], glyph_y + 0.6, scale=1.0)
    put(ax, centers[1], 46.8, "VISIBLE", ha="center", fontsize=6.5, fontweight="bold", color=BLUE)
    put(ax, centers[1], 41.8, "query", ha="center", fontsize=5.7)
    put(ax, centers[1], 37.8, "score stats", ha="center", fontsize=5.7)
    put(ax, centers[1], 33.8, "route meta.", ha="center", fontsize=5.7)
    put(ax, centers[1], 29.8, "6 tokens", ha="center", fontsize=5.7, color=MID)

    draw_closed_eye(ax, centers[2], glyph_y + 0.7, scale=1.0)
    put(ax, centers[2], 46.8, "WITHHELD", ha="center", fontsize=6.5, fontweight="bold", color=PURPLE)
    put(ax, centers[2], 41.8, "qrels", ha="center", fontsize=5.7)
    put(ax, centers[2], 37.8, "route outcomes", ha="center", fontsize=5.7)
    put(ax, centers[2], 33.8, "utility / oracle", ha="center", fontsize=5.7)
    put(
        ax,
        2.8,
        21.0,
        "Legal at commitment:",
        fontsize=6.3,
        color=MID,
        fontweight="bold",
    )
    put(
        ax,
        2.8,
        17.2,
        "query + cheap summaries.",
        fontsize=6.3,
        color=MID,
        style="italic",
    )
    put(
        ax,
        2.8,
        13.2,
        "Withheld until scoring:",
        fontsize=6.3,
        color=MID,
        fontweight="bold",
    )
    put(
        ax,
        2.8,
        9.4,
        "qrels + paid outcomes + oracle.",
        fontsize=6.3,
        color=MID,
        style="italic",
    )

    # Flow of the legal state into the one-shot route selection.
    arrow(ax, (28.2, 51.5), (31.1, 51.5), color=INK, width=1.0)

    # III. Commit: a compact menu, not four decorative path lines.
    heading(ax, 31.1, 94.0, "III", "COMMIT")
    put(
        ax,
        31.1,
        88.6,
        "Choose one cumulative route",
        fontsize=6.8,
        color=MID,
    )
    put(
        ax,
        31.1,
        84.2,
        "before paid outputs exist",
        fontsize=6.8,
        color=MID,
    )
    labels = {
        "stop_bm25": "BM25",
        "dense_fusion": "Dense fusion",
        "cross_encoder": "Cross-encoder",
        "late_interaction": "Late interaction",
    }
    selected = "cross_encoder"
    y_route = [73.5, 63.0, 52.5, 42.0]
    for route_id, y in zip(route_order, y_route):
        route = route_by_id[route_id]
        active = route_id == selected
        edge = ORANGE if active else MID
        ax.add_patch(
            Circle(
                (32.8, y),
                1.05,
                facecolor=edge if active else "white",
                edgecolor=edge,
                lw=1.0,
            )
        )
        if active:
            ax.add_patch(
                Rectangle(
                    (31.1, y - 3.9),
                    20.8,
                    7.8,
                    facecolor=PALE,
                    edgecolor=ORANGE,
                    lw=0.9,
                )
            )
            ax.add_patch(Circle((32.8, y), 1.05, facecolor=ORANGE, edgecolor=ORANGE))
        put(
            ax,
            35.0,
            y + 0.6,
            labels[route_id],
            fontsize=7.2,
            fontweight="bold" if active else "normal",
            color=ORANGE if active else INK,
        )
        put(
            ax,
            51.1,
            y + 0.6,
            f"{route['C_op']:.3f}",
            fontsize=6.8,
            ha="right",
            color=MID,
        )
    put(ax, 31.1, 79.4, "route", fontsize=6.2, color=MID)
    put(ax, 51.1, 79.4, "cum. cost", fontsize=6.2, color=MID, ha="right")
    draw_lock(ax, 41.8, 27.7, scale=1.18)
    put(
        ax,
        41.8,
        19.0,
        "CE action locked",
        fontsize=6.8,
        color=ORANGE,
        fontweight="bold",
        ha="center",
    )
    put(ax, 41.8, 14.4, "before outcome join", fontsize=6.2, color=MID, ha="center")

    # The actual selected route crosses the one strong information boundary.
    arrow(ax, (51.7, 52.5), (55.5, 52.5), color=ORANGE, width=1.35)

    # IV. Hidden ledger: the widest and most information-dense block.
    heading(ax, 55.2, 94.0, "IV", "HIDDEN LEDGER")
    put(
        ax,
        55.2,
        88.6,
        "Evaluator joins every registered outcome after lock",
        fontsize=6.8,
        color=PURPLE,
    )
    x_route, x_q, x_c, x_u, x_role = 55.7, 73.5, 80.7, 87.0, 97.1
    put(ax, x_route, 82.2, "route", fontsize=6.5, fontweight="bold")
    put(ax, x_q, 82.2, "NDCG@10", fontsize=6.5, ha="center", fontweight="bold")
    put(ax, x_c, 82.2, "cost", fontsize=6.5, ha="center", fontweight="bold")
    put(ax, x_u, 82.2, "utility", fontsize=6.5, ha="center", fontweight="bold")
    put(ax, x_role, 82.2, "role", fontsize=6.5, ha="right", fontweight="bold")
    ax.plot([55.3, 98.2], [79.3, 79.3], color=INK, lw=0.8)
    roles = {
        "dense_fusion": ("utility-best", GREEN),
        "cross_encoder": ("selected", ORANGE),
        "late_interaction": ("quality-best", PURPLE),
    }
    y_rows = [73.6, 65.8, 58.0, 50.2]
    for route_id, y in zip(route_order, y_rows):
        row = route_by_id[route_id]
        if route_id == selected:
            ax.add_patch(
                Rectangle(
                    (55.3, y - 3.2),
                    42.9,
                    6.4,
                    facecolor=PALE,
                    edgecolor="none",
                )
            )
            ax.plot([55.3, 55.3], [y - 3.2, y + 3.2], color=ORANGE, lw=2.0)
        put(
            ax,
            x_route,
            y,
            labels[route_id],
            fontsize=6.8,
            fontweight="bold" if route_id == selected else "normal",
        )
        put(ax, x_q, y, f"{row['raw_ndcg_at_10']:.3f}", fontsize=6.8, ha="center")
        put(ax, x_c, y, f"{row['C_op']:.3f}", fontsize=6.8, ha="center")
        put(
            ax,
            x_u,
            y,
            f"{row['utility']:.3f}",
            fontsize=6.8,
            ha="center",
            fontweight="bold" if route_id == ex["utility_oracle_action"] else "normal",
            color=GREEN if route_id == ex["utility_oracle_action"] else INK,
        )
        if route_id in roles:
            role, color = roles[route_id]
            put(
                ax,
                x_role,
                y,
                role,
                fontsize=6.25,
                ha="right",
                fontweight="bold",
                color=color,
            )
    ax.plot([55.3, 98.2], [46.2, 46.2], color=LIGHT, lw=0.75)
    put(ax, 55.7, 41.5, "Chosen CE regret", fontsize=6.7, color=MID)
    put(ax, 72.0, 41.5, ".0509", fontsize=8.0, color=RED, fontweight="bold")
    put(
        ax,
        78.4,
        41.5,
        "exact in the registered menu",
        fontsize=6.2,
        color=MID,
    )
    put(
        ax,
        55.7,
        37.4,
        "Selected, quality-best, and utility-best routes differ.",
        fontsize=6.25,
        color=MID,
        style="italic",
    )

    # V. The former footer becomes a proper evaluator-level result block.
    heading(ax, 55.2, 30.4, "V", "ACROSS 43 TEST TOPICS")
    put(ax, 55.7, 24.2, "DEPLOYABLE", fontsize=6.4, color=BLUE, fontweight="bold")
    put(
        ax,
        55.7,
        19.2,
        "Quality-selected fixed route: CE",
        fontsize=6.25,
        fontweight="bold",
    )
    put(
        ax,
        55.7,
        14.3,
        "Utility-selected fixed route: CE",
        fontsize=6.25,
        fontweight="bold",
    )

    put(ax, 78.1, 24.2, "EVALUATOR-ONLY", fontsize=6.4, color=PURPLE, fontweight="bold")
    put(ax, 78.1, 19.6, "Quality-best vs. utility-best", fontsize=6.2, color=MID)
    put(ax, 78.1, 14.5, "13/43 disagree", fontsize=7.4, color=PURPLE, fontweight="bold")
    put(ax, 78.1, 9.8, "Quality-oracle regret", fontsize=6.2, color=MID)
    put(ax, 97.5, 9.8, ".014147", fontsize=7.4, color=RED, fontweight="bold", ha="right")
    args.output_stem.parent.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "svg", "png"):
        extra = {"dpi": 360} if ext == "png" else {}
        fig.savefig(
            args.output_stem.with_suffix(f".{ext}"),
            bbox_inches="tight",
            pad_inches=0.02,
            facecolor="white",
            **extra,
        )
    plt.close(fig)

    manifest = {
        "figure": "worthir_contract",
        "layout_version": "v2-five-part-unequal-grid",
        "source_json": args.input.name,
        "query_uid": ex["query_uid"],
        "displayed_route_rows": ex["routes"],
        "aggregate_2019": {
            "global_fixed_quality": "cross_encoder",
            "global_fixed_utility": "cross_encoder",
            "oracle_disagreement": "13/43 (30.23%; ties favor least cost)",
            "quality_oracle_utility_regret": 0.014147,
        },
        "design_contract": {
            "reading_order": [
                "I Query",
                "II Cheap signals",
                "III Commit",
                "IV Hidden ledger",
                "V Across 43 test topics",
            ],
            "colored_panel_backgrounds": False,
            "rounded_containers": False,
            "strong_boundary": "post-commit outcome join only",
            "footer_band": False,
        },
        "glyph_note": (
            "The five-bar BM25 glyph is a deterministic visual summary derived "
            "from archived top, mean, standard deviation, and top-1/2 margin; "
            "it is not labeled as five raw document scores."
        ),
    }
    args.output_stem.with_name(args.output_stem.name + "_manifest").with_suffix(
        ".json"
    ).write_text(json.dumps(manifest, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
