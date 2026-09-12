from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass

from src.evaluation.metrics import (
    hit_rate_at_k,
    map_at_k,
    mrr,
    ndcg_at_k,
    precision_at_k,
    recall_at_k,
)


@dataclass(frozen=True)
class EvaluationResult:
    precision_at_k: float
    recall_at_k: float
    ndcg_at_k: float
    map_at_k: float
    mrr: float
    hit_rate_at_k: float
    users_evaluated: int


Recommender = Callable[
    [int, Sequence[int], int],
    Sequence[int],
]


def evaluate_recommender(
    interactions: Sequence[Mapping[str, object]],
    recommender: Recommender,
    k: int = 10,
    evaluation_split: str = "validation",
) -> EvaluationResult:
    """
    Evaluate a recommender using one held-out split.

    Each interaction must contain:
        user_id
        item_id
        split

    The recommender receives:
        user_id
        training_history
        k

    and must return a ranked sequence of item IDs.
    """
    if k <= 0:
        raise ValueError("k must be greater than 0")

    if evaluation_split not in {"validation", "test"}:
        raise ValueError(
            "evaluation_split must be 'validation' or 'test'"
        )

    train_history: dict[int, list[int]] = {}
    held_out_items: dict[int, set[int]] = {}

    for interaction in interactions:
        user_id = int(interaction["user_id"])
        item_id = int(interaction["item_id"])
        split = str(interaction["split"])

        if split == "train":
            train_history.setdefault(user_id, []).append(item_id)

        elif split == evaluation_split:
            held_out_items.setdefault(user_id, set()).add(item_id)

        elif split in {"validation", "test"}:
            continue

        else:
            raise ValueError(f"Unsupported split: {split}")

    metric_totals = {
        "precision": 0.0,
        "recall": 0.0,
        "ndcg": 0.0,
        "map": 0.0,
        "mrr": 0.0,
        "hit_rate": 0.0,
    }

    users_evaluated = 0

    for user_id, relevant_items in held_out_items.items():
        history = train_history.get(user_id, [])

        if not history:
            continue

        recommendations = recommender(user_id, history, k)

        metric_totals["precision"] += precision_at_k(
            recommendations,
            relevant_items,
            k,
        )

        metric_totals["recall"] += recall_at_k(
            recommendations,
            relevant_items,
            k,
        )

        metric_totals["ndcg"] += ndcg_at_k(
            recommendations,
            relevant_items,
            k,
        )

        metric_totals["map"] += map_at_k(
            recommendations,
            relevant_items,
            k,
        )

        metric_totals["mrr"] += mrr(
            recommendations,
            relevant_items,
        )

        metric_totals["hit_rate"] += hit_rate_at_k(
            recommendations,
            relevant_items,
            k,
        )

        users_evaluated += 1

    if users_evaluated == 0:
        return EvaluationResult(
            precision_at_k=0.0,
            recall_at_k=0.0,
            ndcg_at_k=0.0,
            map_at_k=0.0,
            mrr=0.0,
            hit_rate_at_k=0.0,
            users_evaluated=0,
        )

    return EvaluationResult(
        precision_at_k=metric_totals["precision"] / users_evaluated,
        recall_at_k=metric_totals["recall"] / users_evaluated,
        ndcg_at_k=metric_totals["ndcg"] / users_evaluated,
        map_at_k=metric_totals["map"] / users_evaluated,
        mrr=metric_totals["mrr"] / users_evaluated,
        hit_rate_at_k=metric_totals["hit_rate"] / users_evaluated,
        users_evaluated=users_evaluated,
    )