from pathlib import Path

import polars as pl

from src.evaluation.evaluator import evaluate_recommender
from src.recommenders.popularity import PopularityRecommender

DATA_DIR = Path("data/processed")


def load_split(filename: str, split_name: str) -> list[dict[str, object]]:
    return (
        pl.read_parquet(DATA_DIR / filename)
        .with_columns(pl.lit(split_name).alias("split"))
        .to_dicts()
    )


def main() -> None:
    train_interactions = load_split(
        "train_interactions.parquet",
        "train",
    )

    validation_interactions = load_split(
        "validation_interactions.parquet",
        "validation",
    )

    test_interactions = load_split(
        "test_interactions.parquet",
        "test",
    )

    all_interactions = (
        train_interactions
        + validation_interactions
        + test_interactions
    )

    recommender = PopularityRecommender(decay_rate=0.001)
    recommender.fit(train_interactions)

    def recommend_for_evaluation(
        user_id: int,
        history: list[int],
        k: int,
    ) -> list[int]:
        return recommender.recommend(
            user_id=user_id,
            k=k,
            history=history,
        )

    for split in ("validation", "test"):
        result = evaluate_recommender(
            interactions=all_interactions,
            recommender=recommend_for_evaluation,
            k=10,
            evaluation_split=split,
        )

        print(f"Popularity Baseline — {split.title()}")
        print("=" * 40)
        print(f"Users evaluated : {result.users_evaluated:,}")
        print(f"Precision@10    : {result.precision_at_k:.6f}")
        print(f"Recall@10       : {result.recall_at_k:.6f}")
        print(f"NDCG@10         : {result.ndcg_at_k:.6f}")
        print(f"MAP@10          : {result.map_at_k:.6f}")
        print(f"MRR             : {result.mrr:.6f}")
        print(f"HitRate@10      : {result.hit_rate_at_k:.6f}")
        print()


if __name__ == "__main__":
    main()