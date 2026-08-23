"""Shared, frozen feature construction for the MuSiQue admission baseline."""

from __future__ import annotations

import pandas as pd

ROUTES = ["V0", "V1", "V2", "V3"]
QUERY_FEATURES = [
    "question_token_count",
    "n_context",
    "n_decomposition",
    "hop_count",
    "decomposition_length_mean",
    "decomposition_length_std",
    "title_length_mean",
    "title_length_std",
    "title_length_max",
    "paragraph_length_mean",
    "paragraph_length_std",
    "paragraph_length_max",
    "title_overlap_mean",
    "title_overlap_max",
    "base_score_top",
    "base_score_margin",
    "base_score_entropy",
    "cost_V0",
    "cost_V1",
    "cost_V2",
    "cost_V3",
]
ACTION_FEATURES = ["route_cost"] + [f"route_is_{route}" for route in ROUTES]
FEATURE_COLUMNS = QUERY_FEATURES + ACTION_FEATURES


def build_long_features(state: pd.DataFrame) -> pd.DataFrame:
    """Create one legal predictor row per query-route pair."""
    required = {"query_uid", "split", *QUERY_FEATURES}
    missing = sorted(required - set(state.columns))
    if missing:
        raise RuntimeError(f"Missing policy-state fields: {missing}")
    frames = []
    for route in ROUTES:
        frame = state[["query_uid", "split", *QUERY_FEATURES]].copy()
        frame["route"] = route
        frame["route_cost"] = frame[f"cost_{route}"]
        for candidate in ROUTES:
            frame[f"route_is_{candidate}"] = float(route == candidate)
        frames.append(frame)
    result = pd.concat(frames, ignore_index=True)
    return result.sort_values(["query_uid", "route"]).reset_index(drop=True)

