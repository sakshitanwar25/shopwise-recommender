from datetime import UTC, datetime, timedelta

import pytest

from src.recommenders.popularity import PopularityRecommender

REFERENCE_TIME = datetime(2026, 1, 1, tzinfo=UTC)


def make_interaction(
    user_id: int,
    item_id: int,
    days_ago: int = 0,
    rating: float = 5.0,
) -> dict[str, object]:
    return {
        "user_id": user_id,
        "item_id": item_id,
        "event_type": "review",
        "rating": rating,
        "event_ts": REFERENCE_TIME - timedelta(days=days_ago),
    }


def test_popularity_ranking():
    interactions = [
        make_interaction(1, 100),
        make_interaction(2, 100),
        make_interaction(3, 100),
        make_interaction(1, 200),
        make_interaction(2, 200),
        make_interaction(1, 300),
    ]

    recommender = PopularityRecommender()
    recommender.fit(interactions)

    recommendations = recommender.recommend(
        user_id=4,
        k=3,
    )

    assert recommendations == [100, 200, 300]


def test_seen_items_are_excluded():
    interactions = [
        make_interaction(1, 100),
        make_interaction(2, 100),
        make_interaction(1, 200),
        make_interaction(2, 300),
    ]

    recommender = PopularityRecommender()
    recommender.fit(interactions)

    recommendations = recommender.recommend(
        user_id=1,
        k=2,
        history=[100, 200],
    )

    assert recommendations == [300]


def test_k_must_be_positive():
    recommender = PopularityRecommender()

    recommender.fit([
        make_interaction(1, 100),
    ])

    with pytest.raises(ValueError):
        recommender.recommend(
            user_id=1,
            k=0,
        )


def test_recent_interaction_gets_higher_weight():
    interactions = [
        make_interaction(1, 100, days_ago=0),
        make_interaction(2, 200, days_ago=1000),
    ]

    recommender = PopularityRecommender(decay_rate=0.01)
    recommender.fit(interactions)

    recommendations = recommender.recommend(
        user_id=3,
        k=2,
    )

    assert recommendations == [100, 200]


def test_low_rating_review_is_not_counted():
    interactions = [
        make_interaction(1, 100, rating=5.0),
        make_interaction(2, 200, rating=2.0),
    ]

    recommender = PopularityRecommender()
    recommender.fit(interactions)

    recommendations = recommender.recommend(
        user_id=3,
        k=2,
    )

    assert recommendations == [100]


def test_category_specific_popularity():
    interactions = [
        make_interaction(1, 100),
        make_interaction(2, 100),
        make_interaction(1, 200),
        make_interaction(3, 200),
        make_interaction(1, 300),
    ]

    categories = {
        100: "skincare",
        200: "skincare",
        300: "haircare",
    }

    recommender = PopularityRecommender()
    recommender.fit(
        interactions,
        item_categories=categories,
    )

    recommendations = recommender.recommend(
        user_id=4,
        k=2,
        context={"category": "skincare"},
    )

    assert recommendations == [100, 200]