from __future__ import annotations

from pathlib import Path

import polars as pl

from src.evaluation.evaluator import evaluate_recommender
from src.recommendation.popularity import PopularityRecommender


BASE_DIR = Path("data/processed")


def load_interactions() -> list[dict[str, object]]:
    train = (
        pl.read_parquet(BASE_DIR / "train_interactions.parquet")
        .select(["user_id", "item_id"])
        .with_columns(pl.lit("train").alias("split"))
    )

    validation = (
        pl.read_parquet(BASE_DIR / "validation_interactions.parquet")
        .select(["user_id", "item_id"])
        .with_columns(pl.lit("validation").alias("split"))
    )

    return pl.concat([train, validation]).to_dicts()


def main() -> None:
    interactions = load_interactions()

    train_interactions = [
        (int(row["user_id"]), int(row["item_id"]))
        for row in interactions
        if row["split"] == "train"
    ]

    recommender = PopularityRecommender()
    recommender.fit(train_interactions)

    result = evaluate_recommender(
        interactions=interactions,
        recommender=recommender.recommend,
        k=10,
    )

    print("\nPopularity Baseline — Validation")
    print("=" * 40)
    print(f"Users evaluated : {result.users_evaluated:,}")
    print(f"Precision@10    : {result.precision_at_k:.6f}")
    print(f"Recall@10       : {result.recall_at_k:.6f}")
    print(f"NDCG@10         : {result.ndcg_at_k:.6f}")
    print(f"MAP@10          : {result.map_at_k:.6f}")
    print(f"MRR             : {result.mrr:.6f}")
    print(f"HitRate@10      : {result.hit_rate_at_k:.6f}")


if __name__ == "__main__":
    main()