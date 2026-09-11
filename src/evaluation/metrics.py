from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import TypeAlias


Item: TypeAlias = int | str
GradedRelevance: TypeAlias = Mapping[Item, float]


def _validate_k(k: int) -> None:
    if k <= 0:
        raise ValueError("k must be greater than 0")


def _top_k(recommended: Sequence[Item], k: int) -> list[Item]:
    _validate_k(k)
    return list(recommended[:k])


def _binary_relevance(
    relevant: Sequence[Item] | set[Item],
) -> set[Item]:
    return set(relevant)


def precision_at_k(
    recommended: Sequence[Item],
    relevant: Sequence[Item] | set[Item],
    k: int,
) -> float:
    """
    Precision@K = relevant recommended items / K.

    Binary relevance:
        An item is either relevant or not relevant.
    """
    top_k = _top_k(recommended, k)

    if not top_k:
        return 0.0

    relevant_set = _binary_relevance(relevant)
    hits = sum(item in relevant_set for item in top_k)

    return hits / k


def recall_at_k(
    recommended: Sequence[Item],
    relevant: Sequence[Item] | set[Item],
    k: int,
) -> float:
    """
    Recall@K = relevant recommended items / total relevant items.
    """
    relevant_set = _binary_relevance(relevant)

    if not relevant_set:
        return 0.0

    top_k = _top_k(recommended, k)
    hits = sum(item in relevant_set for item in top_k)

    return hits / len(relevant_set)


def ndcg_at_k(
    recommended: Sequence[Item],
    relevant: Sequence[Item] | set[Item],
    k: int,
    graded_relevance: GradedRelevance | None = None,
) -> float:
    """
    NDCG@K.

    If graded_relevance is not provided, relevance is binary:
        relevant item -> 1
        non-relevant item -> 0

    If graded_relevance is provided, its values are used as relevance
    grades, for example rating 1-5.
    """
    top_k = _top_k(recommended, k)

    if graded_relevance is None:
        relevance_lookup = {
            item: 1.0 for item in _binary_relevance(relevant)
        }
    else:
        relevance_lookup = dict(graded_relevance)

    if not relevance_lookup:
        return 0.0

    dcg = sum(
        relevance_lookup.get(item, 0.0) / math.log2(rank + 1)
        for rank, item in enumerate(top_k, start=1)
    )

    ideal_relevances = sorted(
        relevance_lookup.values(),
        reverse=True,
    )[:k]

    idcg = sum(
        relevance / math.log2(rank + 1)
        for rank, relevance in enumerate(ideal_relevances, start=1)
    )

    if idcg == 0.0:
        return 0.0

    return dcg / idcg


def map_at_k(
    recommended: Sequence[Item],
    relevant: Sequence[Item] | set[Item],
    k: int,
) -> float:
    """
    Mean Average Precision@K for a single user's recommendation list.

    For one user, this is Average Precision@K.
    """
    relevant_set = _binary_relevance(relevant)

    if not relevant_set:
        return 0.0

    top_k = _top_k(recommended, k)

    hits = 0
    precision_sum = 0.0

    for rank, item in enumerate(top_k, start=1):
        if item in relevant_set:
            hits += 1
            precision_sum += hits / rank

    return precision_sum / min(len(relevant_set), k)


def mrr(
    recommended: Sequence[Item],
    relevant: Sequence[Item] | set[Item],
) -> float:
    """
    Mean Reciprocal Rank for a single user's recommendation list.

    Returns the reciprocal rank of the first relevant item.
    Returns 0 if no relevant item is recommended.
    """
    relevant_set = _binary_relevance(relevant)

    if not relevant_set:
        return 0.0

    for rank, item in enumerate(recommended, start=1):
        if item in relevant_set:
            return 1.0 / rank

    return 0.0


def hit_rate_at_k(
    recommended: Sequence[Item],
    relevant: Sequence[Item] | set[Item],
    k: int,
) -> float:
    """
    Hit Rate@K = 1 if at least one relevant item appears in Top-K,
    otherwise 0.
    """
    relevant_set = _binary_relevance(relevant)

    if not relevant_set:
        return 0.0

    top_k = _top_k(recommended, k)

    return float(any(item in relevant_set for item in top_k))