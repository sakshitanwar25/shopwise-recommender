import pytest

from src.recommendation.popularity import PopularityRecommender


def test_popularity_ranking():
    interactions = [
        (1, 100),
        (1, 200),
        (2, 100),
        (2, 300),
        (3, 100),
    ]

    recommender = PopularityRecommender()
    recommender.fit(interactions)

    recommendations = recommender.recommend(
        user_id=4,
        history=[],
        k=3,
    )

    assert recommendations == [100, 200, 300]


def test_seen_items_are_excluded():
    interactions = [
        (1, 100),
        (1, 200),
        (2, 100),
        (2, 300),
        (3, 100),
    ]

    recommender = PopularityRecommender()
    recommender.fit(interactions)

    recommendations = recommender.recommend(
        user_id=1,
        history=[100, 200],
        k=2,
    )

    assert recommendations == [300]


def test_k_must_be_positive():
    recommender = PopularityRecommender()

    recommender.fit([(1, 100)])

    with pytest.raises(ValueError):
        recommender.recommend(
            user_id=1,
            history=[],
            k=0,
        )