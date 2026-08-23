"""Render the FiQA cost--quality inversion as a full-width aligned dot table.

The eight aggregates are frozen values from:
  reports/compression_evidence_ladder_beir_fiqa_test__
  sentence_transformers_all_MiniLM_L6_v2.json

This script performs no retrieval, fitting, or statistical estimation.  It
validates U = raw_NDCG@10 - 0.08 * C_op and directly aligns declared cost,
raw retrieval quality, and cost-adjusted utility for every evidence view.
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
DATA = HERE / "cost_quality_inversion_data.csv"
OUT = HERE / "cost_quality_final"

LAMBDA = 0.08
BLUE = "#0072B2"       # Okabe--Ito blue
ORANGE = "#E69F00"     # Okabe--Ito orange
ORANGE_TEXT = "#8F5E00"
INK = "#263238"
MID_GRAY = "#5F686D"
LIGHT_GRAY = "#CBD3D7"
TRACK_GRAY = "#E2E7EA"
PALE_BLUE = "#EAF4FA"
PALE_ORANGE = "#FFF3DD"


def configure_style() -> None:
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Liberation Sans", "DejaVu Sans"],
            "font.size": 8.1,
            "axes.labelsize": 8.1,
            "axes.titlesize": 9.0,
            "xtick.labelsize": 7.2,
            "ytick.labelsize": 8.0,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "axes.linewidth": 0.55,
            "xtick.major.width": 0.55,
            "ytick.major.width": 0.0,
            "xtick.major.size": 2.5,
            "ytick.major.size": 0.0,
        }
    )


def load_and_validate() -> pd.DataFrame:
    df = pd.read_csv(DATA)
    expected = df["raw_ndcg_at_10"] - LAMBDA * df["cumulative_cost"]
    if not np.allclose(expected, df["utility_lambda_0p08"], atol=1e-12):
        raise ValueError("Utility column does not equal raw quality - lambda * cost.")
    if len(df) != 8 or df["view"].nunique() != 8:
        raise ValueError("Expected exactly eight unique compression-ladder views.")
    if not np.isfinite(df.select_dtypes("number").to_numpy()).all():
        raise ValueError("All plotted numeric values must be finite.")
    return df


def render(df: pd.DataFrame) -> plt.Figure:
    # Full ACM sigconf text width.  The low aspect ratio preserves page space
    # while giving three metrics enough horizontal room for direct labels.
    fig, axes = plt.subplots(
        1,
        3,
        figsize=(7.0, 2.42),
        sharey=True,
        gridspec_kw={"width_ratios": [1.08, 1.0, 1.08], "wspace": 0.18},
    )
    fig.patch.set_facecolor("white")
    for ax in axes:
        ax.set_facecolor("white")

    # Views are an ordered acquisition ladder, not samples from a continuous
    # response curve.  Keeping them as aligned rows avoids implying interpolation.
    df = df.sort_values("cumulative_cost", kind="stable").reset_index(drop=True)
    y = np.arange(len(df), dtype=float)
    int8_idx = int(df.index[df["view"] == "int8 dense"][0])
    ce_idx = int(df.index[df["view"] == "cross-encoder"][0])

    for ax in axes:
        ax.axhspan(int8_idx - 0.42, int8_idx + 0.42, color=PALE_BLUE, zorder=-4)
        ax.axhspan(ce_idx - 0.42, ce_idx + 0.42, color=PALE_ORANGE, zorder=-4)
        for row_y in y:
            ax.axhline(row_y, color=TRACK_GRAY, linewidth=0.55, zorder=-3)
        ax.spines[["top", "right", "left"]].set_visible(False)
        ax.tick_params(axis="x", colors=INK, pad=2)
        ax.tick_params(axis="y", colors=INK, pad=4)
        ax.set_ylim(len(df) - 0.45, -0.55)

    specs = [
        {
            "column": "cumulative_cost",
            "title": r"(a) Declared cost $C_{\mathrm{op}}$",
            "xlim": (-0.055, 1.28),
            "ticks": [0.0, 0.5, 1.0],
            "value_x": 1.095,
            "track_end": 1.04,
            "fmt": ".2f",
        },
        {
            "column": "raw_ndcg_at_10",
            "title": "(b) Raw NDCG@10: CE wins",
            "xlim": (-0.012, 0.515),
            "ticks": [0.0, 0.2, 0.4],
            "value_x": 0.418,
            "track_end": 0.40,
            "fmt": ".3f",
        },
        {
            "column": "utility_lambda_0p08",
            "title": "(c) Utility: int8 wins",
            "xlim": (-0.012, 0.485),
            "ticks": [0.0, 0.15, 0.30],
            "value_x": 0.366,
            "track_end": 0.35,
            "fmt": ".3f",
        },
    ]

    for ax, spec in zip(axes, specs):
        values = df[spec["column"]].to_numpy(dtype=float)
        # Lollipops use one grammar in every panel; row and marker identity carry
        # across cost, raw quality, and utility.
        for idx, value in enumerate(values):
            color = MID_GRAY
            text_color = INK
            marker = "o"
            face = "white"
            size = 27
            linewidth = 0.9
            line_color = LIGHT_GRAY
            line_width = 1.15
            fontweight = "normal"

            if idx == int8_idx:
                color = BLUE
                text_color = BLUE
                marker = "D"
                face = BLUE
                size = 47
                linewidth = 0.75
                line_color = "#8DC0DD"
                line_width = 1.55
                fontweight = "bold"
            elif idx == ce_idx:
                color = ORANGE
                text_color = ORANGE_TEXT
                marker = "s"
                face = ORANGE
                size = 47
                linewidth = 0.75
                line_color = "#E8C77C"
                line_width = 1.55
                fontweight = "bold"

            ax.hlines(
                y=idx,
                xmin=0.0,
                xmax=value,
                color=line_color,
                linewidth=line_width,
                zorder=1,
            )
            ax.scatter(
                [value],
                [idx],
                s=size,
                marker=marker,
                facecolor=face,
                edgecolor=color if face == "white" else INK,
                linewidth=linewidth,
                zorder=3,
            )

            label = format(value, spec["fmt"])
            ax.text(
                spec["value_x"],
                idx,
                label,
                color=text_color,
                fontsize=7.25,
                fontweight=fontweight,
                ha="left",
                va="center",
                clip_on=False,
            )

        ax.set_xlim(*spec["xlim"])
        ax.set_xticks(spec["ticks"])
        ax.set_title(spec["title"], loc="left", color=INK, fontweight="bold", pad=8)
        ax.spines["bottom"].set_color("#AEB6BA")
        ax.spines["bottom"].set_linewidth(0.55)

    labels = df["view"].tolist()
    axes[0].set_yticks(y, labels=labels)
    for tick, view in zip(axes[0].get_yticklabels(), labels):
        if view == "int8 dense":
            tick.set_color(BLUE)
            tick.set_fontweight("bold")
        elif view == "cross-encoder":
            tick.set_color(ORANGE_TEXT)
            tick.set_fontweight("bold")
        else:
            tick.set_color(INK)
    for ax in axes[1:]:
        ax.tick_params(labelleft=False)

    # Compact, direct summary: the visual conclusion does not require an
    # iso-utility contour or arithmetic by the reader.
    fig.text(
        0.50,
        0.988,
        r"Same 260 queries  ·  routes ordered by cumulative cost",
        ha="center",
        va="top",
        color=MID_GRAY,
        fontsize=7.3,
    )
    fig.subplots_adjust(left=0.155, right=0.982, bottom=0.145, top=0.84, wspace=0.18)
    return fig


def main() -> None:
    configure_style()
    df = load_and_validate()
    fig = render(df)
    out_pdf = OUT.with_suffix(".pdf")
    out_svg = OUT.with_suffix(".svg")
    out_png = OUT.with_suffix(".png")
    out_gray = OUT.parent / f"{OUT.name}_grayscale.png"
    out_deut = OUT.parent / f"{OUT.name}_deuteranopia.png"
    fig.savefig(out_pdf, bbox_inches=None)
    fig.savefig(out_svg, bbox_inches=None)
    fig.savefig(out_png, dpi=300, bbox_inches=None)
    plt.close(fig)

    # Rewrite the grayscale proof from the RGB render to avoid colormap drift.
    with Image.open(out_png) as image:
        image.convert("L").save(out_gray)

        # Color-vision proof only; the publication source remains the vector PDF.
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
            Image.fromarray(
                np.uint8(np.clip(simulated, 0.0, 1.0) * 255)
            ).save(out_deut)
        except Exception as exc:  # fail closed for the QA proof
            raise RuntimeError("Could not create the deuteranopia QA proof.") from exc

    manifest = {
        "figure": "cost-quality inversion",
        "source_data": DATA.name,
        "lambda": LAMBDA,
        "formula": "utility = raw_ndcg_at_10 - 0.08 * cumulative_cost",
        "rows": len(df),
        "design": (
            "Full-width aligned dot-table: one shared row per view and direct "
            "columns for declared cost, raw quality, and utility."
        ),
        "semantic_scope": (
            "FiQA-Compression260: eight-view compression ladder on the frozen "
            "260-query "
            "intersection; no HNSW rows and no incremental-CE purchase curve."
        ),
        "outputs": [
            path.name for path in (out_pdf, out_svg, out_png, out_gray, out_deut)
        ],
    }
    (HERE / "cost_quality_figure_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
