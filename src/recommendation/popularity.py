from __future__ import annotations

from collections import Counter
from collections.abc import Iterable


class PopularityRecommender:
    """Recommend the most popular unseen items."""

    def __init__(self) -> None:
        self._ranking: list[int] = []

    def fit(
        self,
        interactions: Iterable[tuple[int, int]],
    ) -> PopularityRecommender:
        """
        Fit popularity ranking using training interactions.

        Parameters
        ----------
        interactions:
            Iterable of (user_id, item_id) pairs.
        """
        item_counts = Counter(item_id for _, item_id in interactions)

        self._ranking = [
            item_id
            for item_id, _ in item_counts.most_common()
        ]

        return self

    def recommend(
        self,
        user_id: int,
        history: Iterable[int],
        k: int = 10,
    ) -> list[int]:
        """
        Return top-k popular items the user has not interacted with.
        """
        if k <= 0:
            raise ValueError("k must be greater than 0")

        seen_items = set(history)

        recommendations: list[int] = []

        for item_id in self._ranking:
            if item_id in seen_items:
                continue

            recommendations.append(item_id)

            if len(recommendations) == k:
                break

        return recommendations