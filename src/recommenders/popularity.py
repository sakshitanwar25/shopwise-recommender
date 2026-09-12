from __future__ import annotations

import math
from collections.abc import Iterable, Mapping
from datetime import datetime
from typing import ClassVar


class PopularityRecommender:
    """Time-decayed weighted popularity recommender."""

    EVENT_WEIGHTS: ClassVar[dict[str, float]] = {
        "view": 1.0,
        "like": 3.0,
        "save": 3.0,
        "cart": 5.0,
        "purchase": 8.0,
        "review": 8.0,
    }

    def __init__(self, decay_rate: float = 0.001) -> None:
        if decay_rate < 0:
            raise ValueError("decay_rate must be non-negative")

        self.decay_rate = decay_rate
        self._ranking: list[int] = []
        self._category_rankings: dict[str, list[int]] = {}

    def fit(
        self,
        interactions: Iterable[Mapping[str, object]],
        item_categories: Mapping[int, str] | None = None,
    ) -> PopularityRecommender:
        """Fit global and optional category-specific popularity."""

        rows = list(interactions)

        if not rows:
            self._ranking = []
            self._category_rankings = {}
            return self

        timestamps = [
            row["event_ts"]
            for row in rows
            if isinstance(row["event_ts"], datetime)
        ]

        if not timestamps:
            raise TypeError("event_ts must be datetime")

        reference_time = max(timestamps)

        global_scores: dict[int, float] = {}
        category_scores: dict[str, dict[int, float]] = {}

        for row in rows:
            item_id = int(row["item_id"])
            event_type = str(row["event_type"])
            rating = row.get("rating")

            weight = self._get_weight(event_type, rating)

            if weight == 0:
                continue

            event_ts = row["event_ts"]

            if not isinstance(event_ts, datetime):
                raise TypeError("event_ts must be datetime")

            age_days = (
                reference_time - event_ts
            ).total_seconds() / 86_400

            score = weight * math.exp(
                -self.decay_rate * age_days
            )

            global_scores[item_id] = (
                global_scores.get(item_id, 0.0) + score
            )

            if item_categories and item_id in item_categories:
                category = item_categories[item_id]

                if category not in category_scores:
                    category_scores[category] = {}

                category_scores[category][item_id] = (
                    category_scores[category].get(item_id, 0.0)
                    + score
                )

        self._ranking = self._sort_scores(global_scores)

        self._category_rankings = {
            category: self._sort_scores(scores)
            for category, scores in category_scores.items()
        }

        return self

    def recommend(
        self,
        user_id: int,
        k: int = 10,
        context: Mapping[str, object] | None = None,
        history: Iterable[int] | None = None,
    ) -> list[int]:
        """Return top-k popular unseen items."""

        del user_id

        if k <= 0:
            raise ValueError("k must be greater than 0")

        seen_items = set(history or [])

        ranking = self._ranking

        if context and context.get("category"):
            category = str(context["category"])
            ranking = self._category_rankings.get(
                category,
                self._ranking,
            )

        return [
            item_id
            for item_id in ranking
            if item_id not in seen_items
        ][:k]

    @classmethod
    def _get_weight(
        cls,
        event_type: str,
        rating: object,
    ) -> float:
        if event_type == "review":
            if rating is None:
                return 0.0

            if float(rating) < 4:
                return 0.0

        return cls.EVENT_WEIGHTS.get(event_type, 0.0)

    @staticmethod
    def _sort_scores(scores: Mapping[int, float]) -> list[int]:
        return [
            item_id
            for item_id, _ in sorted(
                scores.items(),
                key=lambda pair: (-pair[1], pair[0]),
            )
        ]