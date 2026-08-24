#!/usr/bin/env python3
"""Rebuild the eight FiQA-Compression260 retrieval routes used in the paper."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import urllib.request
import zipfile
from pathlib import Path

import faiss
import numpy as np
import pandas as pd
from sentence_transformers import CrossEncoder, SentenceTransformer

faiss.omp_set_num_threads(1)


DATA_URL = "https://public.ukp.informatik.tu-darmstadt.de/thakur/BEIR/datasets/fiqa.zip"
DATA_SHA256 = "32c7df99ed21252fdfb2cf3f5673502a8d245ee0c44c4a133570d92ce2b3ad02"
ENCODER_ID = "sentence-transformers/all-MiniLM-L6-v2"
ENCODER_REVISION = "c9745ed1d9f207416be6d2e6f8de32d1f16199bf"
CROSS_ENCODER_ID = "cross-encoder/ms-marco-MiniLM-L-6-v2"
CROSS_ENCODER_REVISION = "c5ee24cb16019beea0893ab7796b1df96625c6b8"

ROUTES = [
    ("summary", "Summary", 0.00),
    ("binary", "Binary dense", 0.08),
    ("pq", "IVF--PQ", 0.20),
    ("trunc96", "Trunc-96", 0.26),
    ("int8", "Int8 dense", 0.30),
    ("trunc192", "Trunc-192", 0.40),
    ("full", "Full dense", 0.58),
    ("ce", "Cross-encoder", 1.03),
]

PAPER_MEANS = {
    "summary": 0.019013017416,
    "binary": 0.287420183420,
    "pq": 0.255292326212,
    "trunc96": 0.281337320805,
    "int8": 0.360987395048,
    "trunc192": 0.333659887314,
    "full": 0.363555222750,
    "ce": 0.376116305590,
}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def find_repository(start: Path) -> Path:
    for parent in [start, *start.parents]:
        if (parent / "paper_results" / "replays" / "fiqa260" / "query_membership.parquet").is_file():
            return parent
    raise RuntimeError(
        "Cannot locate paper_results/replays/fiqa260/query_membership.parquet. "
        "Run this adapter from a WorthIR source checkout."
    )


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def check_dataset_archive(path: Path) -> None:
    observed = sha256(path)
    if observed != DATA_SHA256:
        raise RuntimeError(
            f"Unexpected SHA256 for {path}: {observed}. "
            "Remove the archive and rerun after checking the official BEIR download."
        )


def download_dataset(cache: Path) -> Path:
    dataset = cache / "fiqa"
    if (dataset / "corpus.jsonl").is_file() and (dataset / "qrels" / "test.tsv").is_file():
        return dataset
    cache.mkdir(parents=True, exist_ok=True)
    archive = cache / "fiqa.zip"
    if not archive.is_file():
        print(f"Downloading the official BEIR FiQA archive to {archive}", flush=True)
        partial = archive.with_suffix(".zip.part")
        urllib.request.urlretrieve(DATA_URL, partial)
        try:
            check_dataset_archive(partial)
        except Exception:
            partial.unlink(missing_ok=True)
            raise
        partial.replace(archive)
    else:
        check_dataset_archive(archive)
    print(f"Extracting {archive}", flush=True)
    with zipfile.ZipFile(archive) as bundle:
        bundle.extractall(cache)
    if not (dataset / "corpus.jsonl").is_file():
        raise RuntimeError("The downloaded archive does not contain fiqa/corpus.jsonl")
    return dataset


def load_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as stream:
        for line in stream:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def load_qrels(path: Path) -> dict[str, dict[str, int]]:
    result: dict[str, dict[str, int]] = {}
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        for row in reader:
            query_id = str(row["query-id"])
            result.setdefault(query_id, {})[str(row["corpus-id"])] = int(row["score"])
    return result


def load_query_ids(repository: Path, limit: int | None) -> list[str]:
    membership = pd.read_parquet(
        repository / "paper_results" / "replays" / "fiqa260" / "query_membership.parquet"
    )
    order = "ce_boundary_csv_row_index"
    if order in membership:
        membership = membership.sort_values(order, kind="stable")
    values = [str(value).split("::")[-1] for value in membership["query_uid"]]
    return values[:limit] if limit is not None else values


def normalize(matrix: np.ndarray) -> np.ndarray:
    matrix = np.asarray(matrix, dtype=np.float32)
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    return matrix / np.maximum(norms, np.finfo(np.float32).eps)


def encode_corpus(
    dataset: Path,
    cache: Path,
    query_ids: list[str],
) -> tuple[list[str], list[str], np.ndarray, list[str], np.ndarray]:
    doc_path = cache / "document_embeddings.npy"
    doc_ids_path = cache / "document_ids.json"
    corpus_rows = load_jsonl(dataset / "corpus.jsonl")
    doc_ids = [str(row["_id"]) for row in corpus_rows]
    doc_texts = [
        " ".join(part for part in (str(row.get("title", "")).strip(), str(row.get("text", "")).strip()) if part)
        for row in corpus_rows
    ]
    query_lookup = {str(row["_id"]): str(row["text"]) for row in load_jsonl(dataset / "queries.jsonl")}
    absent = [query_id for query_id in query_ids if query_id not in query_lookup]
    if absent:
        raise RuntimeError(f"FiQA archive is missing selected query IDs: {absent[:5]}")
    query_texts = [query_lookup[query_id] for query_id in query_ids]

    model = SentenceTransformer(ENCODER_ID, revision=ENCODER_REVISION)
    model.max_seq_length = 256
    if doc_path.is_file() and doc_ids_path.is_file():
        saved_ids = read_json(doc_ids_path)
        if saved_ids != doc_ids:
            raise RuntimeError("Cached document IDs do not match the downloaded FiQA corpus")
        doc_embeddings = np.load(doc_path, mmap_mode="r")
    else:
        print(f"Encoding {len(doc_texts):,} FiQA documents with {ENCODER_ID}", flush=True)
        encoded = model.encode(
            doc_texts,
            batch_size=256,
            show_progress_bar=True,
            convert_to_numpy=True,
            normalize_embeddings=True,
        ).astype(np.float32)
        np.save(doc_path, encoded)
        write_json(doc_ids_path, doc_ids)
        doc_embeddings = np.load(doc_path, mmap_mode="r")
    query_embeddings = model.encode(
        query_texts,
        batch_size=256,
        show_progress_bar=False,
        convert_to_numpy=True,
        normalize_embeddings=True,
    ).astype(np.float32)
    return doc_ids, doc_texts, doc_embeddings, query_texts, query_embeddings


def topk(scores: np.ndarray, k: int) -> tuple[np.ndarray, np.ndarray]:
    k = min(k, scores.shape[1])
    partition = np.argpartition(scores, -k, axis=1)[:, -k:]
    values = np.take_along_axis(scores, partition, axis=1)
    order = np.argsort(-values, axis=1, kind="stable")
    indices = np.take_along_axis(partition, order, axis=1)
    values = np.take_along_axis(values, order, axis=1)
    return values.astype(np.float32), indices.astype(np.int64)


def exact_search(query: np.ndarray, documents: np.ndarray, k: int) -> tuple[np.ndarray, np.ndarray]:
    index = faiss.IndexFlatIP(documents.shape[1])
    index.add(np.ascontiguousarray(documents, dtype=np.float32))
    scores, indices = index.search(np.ascontiguousarray(query, dtype=np.float32), k)
    return scores, indices


def build_summary_index(documents: np.ndarray, cache: Path) -> tuple[np.ndarray, np.ndarray]:
    centroids_path = cache / "summary_centroids.npy"
    representatives_path = cache / "summary_representatives.npy"
    if centroids_path.is_file() and representatives_path.is_file():
        return np.load(centroids_path), np.load(representatives_path)
    print("Building the 512-cell summary index", flush=True)
    data = np.ascontiguousarray(documents, dtype=np.float32)
    kmeans = faiss.Kmeans(
        data.shape[1],
        512,
        niter=25,
        spherical=True,
        seed=1234,
        verbose=True,
        gpu=False,
    )
    kmeans.train(data)
    centroids = normalize(kmeans.centroids)
    _, assignments = kmeans.index.search(data, 1)
    representatives = np.full((512, 10), -1, dtype=np.int64)
    for cluster in range(512):
        members = np.flatnonzero(assignments[:, 0] == cluster)
        if not len(members):
            continue
        similarities = data[members] @ centroids[cluster]
        ranked = np.argsort(-similarities, kind="stable")[:10]
        representatives[cluster, : len(ranked)] = members[ranked]
    np.save(centroids_path, centroids)
    np.save(representatives_path, representatives)
    return centroids, representatives


def summary_search(
    query: np.ndarray,
    documents: np.ndarray,
    cache: Path,
    k: int = 10,
) -> tuple[np.ndarray, np.ndarray]:
    centroids, representatives = build_summary_index(documents, cache)
    centroid_scores, cells = topk(query @ centroids.T, 80)
    rankings = representatives[cells[:, 0], :k].copy()
    return centroid_scores[:, :k], rankings


def pq_search(query: np.ndarray, documents: np.ndarray, cache: Path, k: int = 10) -> tuple[np.ndarray, np.ndarray]:
    index_path = cache / "ivfpq.index"
    if index_path.is_file():
        index = faiss.read_index(str(index_path))
    else:
        print("Training the IVF--PQ route", flush=True)
        quantizer = faiss.IndexFlatIP(documents.shape[1])
        index = faiss.IndexIVFPQ(
            quantizer,
            documents.shape[1],
            512,
            24,
            8,
            faiss.METRIC_INNER_PRODUCT,
        )
        rng = np.random.default_rng(17)
        sample = rng.choice(len(documents), size=min(40960, len(documents)), replace=False)
        index.train(np.ascontiguousarray(documents[sample], dtype=np.float32))
        index.add(np.ascontiguousarray(documents, dtype=np.float32))
        faiss.write_index(index, str(index_path))
    index.nprobe = 32
    return index.search(np.ascontiguousarray(query, dtype=np.float32), k)


def ndcg_at_10(ranking: np.ndarray, doc_ids: list[str], relevant: dict[str, int]) -> float:
    gains = [relevant.get(doc_ids[index], 0) if index >= 0 else 0 for index in ranking[:10]]
    dcg = sum((2**gain - 1) / math.log2(rank + 2) for rank, gain in enumerate(gains))
    ideal = sorted(relevant.values(), reverse=True)[:10]
    idcg = sum((2**gain - 1) / math.log2(rank + 2) for rank, gain in enumerate(ideal))
    return dcg / idcg if idcg else 0.0


def legal_features(query: np.ndarray, summary_scores: np.ndarray) -> dict[str, float]:
    values: dict[str, float] = {
        f"query_emb_head_{position:02d}": float(query[position]) for position in range(16)
    }
    values.update(
        {
            "query_emb_mean": float(query.mean()),
            "query_emb_std": float(query.std()),
            "query_emb_min": float(query.min()),
            "query_emb_max": float(query.max()),
            "query_emb_positive_fraction": float((query > 0).mean()),
        }
    )
    finite = summary_scores[np.isfinite(summary_scores)]
    if not len(finite):
        finite = np.zeros(1, dtype=np.float32)
    shifted = finite - finite.max()
    probabilities = np.exp(shifted) / np.exp(shifted).sum()
    values.update(
        {
            "summary_top1": float(finite[0]),
            "summary_margin": float(finite[0] - finite[1]) if len(finite) > 1 else 0.0,
            "summary_mean_top10": float(finite.mean()),
            "summary_std_top10": float(finite.std()),
            "summary_span_top10": float(finite.max() - finite.min()),
            "summary_entropy_top10": float(-(probabilities * np.log(probabilities + 1e-12)).sum()),
        }
    )
    return values


def write_sources(
    output: Path,
    query_ids: list[str],
    query_embeddings: np.ndarray,
    summary_scores: np.ndarray,
    effectiveness: dict[str, list[float]],
) -> None:
    output.mkdir(parents=True, exist_ok=True)
    write_json(
        output / "task.json",
        {
            "task_id": "fiqa-compression260",
            "metric": {"name": "NDCG@10", "minimum": 0, "maximum": 1, "higher_is_better": True},
            "cost_profile": {
                "profile_id": "fiqa-compression260-operator-cost-v1",
                "provenance": "Registered task-specific operator costs from the WorthIR paper",
                "lambda": 0.08,
                "availability": "known_at_commitment",
            },
            "development_selected_fixed_route": "int8",
        },
    )
    query_rows = []
    for position, query_id in enumerate(query_ids):
        row = {"query_uid": f"beir-fiqa-test::{query_id}"}
        row.update(legal_features(query_embeddings[position], summary_scores[position]))
        query_rows.append(row)
    with (output / "queries.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(query_rows[0]))
        writer.writeheader()
        writer.writerows(query_rows)
    with (output / "routes.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=["route_id", "label", "prerequisites", "cost", "development_selected"],
        )
        writer.writeheader()
        for route_id, label, cost in ROUTES:
            if route_id == "summary":
                prerequisites = ""
            elif route_id == "ce":
                prerequisites = "full"
            else:
                prerequisites = "summary"
            writer.writerow(
                {
                    "route_id": route_id,
                    "label": label,
                    "prerequisites": prerequisites,
                    "cost": cost,
                    "development_selected": "true" if route_id == "int8" else "false",
                }
            )
    with (output / "outcomes.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["query_uid", "route_id", "effectiveness"])
        writer.writeheader()
        for position, query_id in enumerate(query_ids):
            for route_id, _, _ in ROUTES:
                writer.writerow(
                    {
                        "query_uid": f"beir-fiqa-test::{query_id}",
                        "route_id": route_id,
                        "effectiveness": f"{effectiveness[route_id][position]:.12g}",
                    }
                )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    config = read_json(args.config.resolve())
    workspace = args.config.resolve().parent
    repository = find_repository(Path(__file__).resolve())
    cache = workspace / "cache"
    dataset = download_dataset(cache / "dataset")
    query_ids = load_query_ids(repository, args.limit)
    doc_ids, doc_texts, documents, query_texts, queries = encode_corpus(
        dataset, cache, query_ids
    )

    rankings: dict[str, np.ndarray] = {}
    scores: dict[str, np.ndarray] = {}
    scores["summary"], rankings["summary"] = summary_search(queries, documents, cache)
    binary_documents = normalize(np.where(np.asarray(documents) >= 0, 1.0, -1.0))
    binary_queries = normalize(np.where(queries >= 0, 1.0, -1.0))
    scores["binary"], rankings["binary"] = exact_search(binary_queries, binary_documents, 10)
    scores["pq"], rankings["pq"] = pq_search(queries, documents, cache)
    trunc96_documents = normalize(np.asarray(documents)[:, :96])
    trunc96_queries = normalize(queries[:, :96])
    scores["trunc96"], rankings["trunc96"] = exact_search(trunc96_queries, trunc96_documents, 10)
    int8_documents = normalize(np.rint(np.asarray(documents) * 127).clip(-127, 127).astype(np.int8))
    int8_queries = normalize(np.rint(queries * 127).clip(-127, 127).astype(np.int8))
    scores["int8"], rankings["int8"] = exact_search(int8_queries, int8_documents, 10)
    trunc192_documents = normalize(np.asarray(documents)[:, :192])
    trunc192_queries = normalize(queries[:, :192])
    scores["trunc192"], rankings["trunc192"] = exact_search(trunc192_queries, trunc192_documents, 10)
    scores["full"], rankings["full"] = exact_search(queries, documents, 50)

    ce_cache = cache / f"ce_rankings_{len(query_ids)}.npy"
    ce_ids_cache = cache / f"ce_query_ids_{len(query_ids)}.json"
    if ce_cache.is_file() and ce_ids_cache.is_file() and read_json(ce_ids_cache) == query_ids:
        ce_rankings = np.load(ce_cache)
    else:
        print(f"Cross-encoding {len(query_ids) * 50:,} query--document pairs", flush=True)
        reranker = CrossEncoder(CROSS_ENCODER_ID, revision=CROSS_ENCODER_REVISION, max_length=512)
        pairs = [
            (query_text, doc_texts[index])
            for query_text, candidates in zip(query_texts, rankings["full"])
            for index in candidates
        ]
        predictions = np.asarray(
            reranker.predict(pairs, batch_size=64, show_progress_bar=True)
        ).reshape(len(query_ids), 50)
        ce_rankings = np.full((len(query_ids), 10), -1, dtype=np.int64)
        for position, candidates in enumerate(rankings["full"]):
            order = np.argsort(-predictions[position], kind="stable")[:10]
            ce_rankings[position] = candidates[order]
        np.save(ce_cache, ce_rankings)
        write_json(ce_ids_cache, query_ids)
    rankings["ce"] = ce_rankings

    qrels = load_qrels(dataset / "qrels" / "test.tsv")
    effectiveness: dict[str, list[float]] = {}
    for route_id, _, _ in ROUTES:
        effectiveness[route_id] = [
            ndcg_at_10(ranking, doc_ids, qrels.get(query_id, {}))
            for query_id, ranking in zip(query_ids, rankings[route_id])
        ]
    write_sources(
        args.output.resolve(), query_ids, queries, scores["summary"][:, :10], effectiveness
    )

    summary = {
        "task": config.get("task", "fiqa260"),
        "query_count": len(query_ids),
        "route_count": len(ROUTES),
        "means": {route_id: float(np.mean(values)) for route_id, values in effectiveness.items()},
        "paper_means": PAPER_MEANS if args.limit is None else None,
    }
    if args.limit is None:
        runtime_sensitive = {"summary", "binary", "pq"}
        summary["paper_comparison"] = {
            route_id: {
                "rebuilt": summary["means"][route_id],
                "paper": PAPER_MEANS[route_id],
                "absolute_difference": abs(summary["means"][route_id] - PAPER_MEANS[route_id]),
                "status": (
                    "runtime-sensitive replay"
                    if route_id in runtime_sensitive
                    else (
                        "exact within 0.000001"
                        if abs(summary["means"][route_id] - PAPER_MEANS[route_id]) <= 1e-6
                        else "does not match"
                    )
                ),
            }
            for route_id, _, _ in ROUTES
        }
    write_json(workspace / "fiqa260_rebuild_summary.json", summary)
    print(f"WROTE: {args.output.resolve()}")
    print(json.dumps(summary["means"], indent=2))


if __name__ == "__main__":
    main()
