import math

import pytest

from src.evaluation.metrics import (
    hit_rate_at_k,
    map_at_k,
    mrr,
    ndcg_at_k,
    precision_at_k,
    recall_at_k,
)


def test_precision_at_k():
    recommended = [1, 2, 3, 4, 5]
    relevant = {2, 4}

    assert precision_at_k(recommended, relevant, 5) == pytest.approx(0.4)


def test_recall_at_k():
    recommended = [1, 2, 3, 4, 5]
    relevant = {2, 4}

    assert recall_at_k(recommended, relevant, 5) == pytest.approx(1.0)


def test_precision_at_k_only_uses_top_k():
    recommended = [1, 2, 3, 4, 5]
    relevant = {5}

    assert precision_at_k(recommended, relevant, 3) == pytest.approx(0.0)


def test_recall_at_k_only_uses_top_k():
    recommended = [1, 2, 3, 4, 5]
    relevant = {4, 5}

    assert recall_at_k(recommended, relevant, 3) == pytest.approx(0.0)


def test_ndcg_binary_perfect_ranking():
    recommended = [1, 2, 3]
    relevant = {1, 2, 3}

    assert ndcg_at_k(recommended, relevant, 3) == pytest.approx(1.0)


def test_ndcg_binary_worse_ranking():
    recommended = [3, 2, 1]
    relevant = {1, 2, 3}

    assert ndcg_at_k(recommended, relevant, 3) == pytest.approx(1.0)


def test_ndcg_graded_relevance():
    recommended = [1, 2, 3]
    relevant = {1, 2, 3}
    graded_relevance = {
        1: 5.0,
        2: 3.0,
        3: 1.0,
    }

    assert ndcg_at_k(
        recommended,
        relevant,
        3,
        graded_relevance=graded_relevance,
    ) == pytest.approx(1.0)


def test_ndcg_graded_relevance_penalizes_bad_order():
    recommended = [3, 2, 1]
    relevant = {1, 2, 3}
    graded_relevance = {
        1: 5.0,
        2: 3.0,
        3: 1.0,
    }

    expected_dcg = (
        1.0 / math.log2(2)
        + 3.0 / math.log2(3)
        + 5.0 / math.log2(4)
    )

    ideal_dcg = (
        5.0 / math.log2(2)
        + 3.0 / math.log2(3)
        + 1.0 / math.log2(4)
    )

    assert ndcg_at_k(
        recommended,
        relevant,
        3,
        graded_relevance=graded_relevance,
    ) == pytest.approx(expected_dcg / ideal_dcg)


def test_map_at_k():
    recommended = [1, 2, 3, 4]
    relevant = {2, 4}

    expected = ((1 / 2) + (2 / 4)) / 2

    assert map_at_k(recommended, relevant, 4) == pytest.approx(expected)


def test_mrr():
    recommended = [1, 2, 3, 4]
    relevant = {3}

    assert mrr(recommended, relevant) == pytest.approx(1 / 3)


def test_mrr_no_hit():
    recommended = [1, 2, 3]
    relevant = {10}

    assert mrr(recommended, relevant) == pytest.approx(0.0)


def test_hit_rate_at_k_with_hit():
    recommended = [1, 2, 3, 4]
    relevant = {3}

    assert hit_rate_at_k(recommended, relevant, 3) == pytest.approx(1.0)


def test_hit_rate_at_k_without_hit():
    recommended = [1, 2, 3, 4]
    relevant = {4}

    assert hit_rate_at_k(recommended, relevant, 3) == pytest.approx(0.0)


def test_empty_relevant_set():
    recommended = [1, 2, 3]

    assert precision_at_k(recommended, set(), 3) == 0.0
    assert recall_at_k(recommended, set(), 3) == 0.0
    assert ndcg_at_k(recommended, set(), 3) == 0.0
    assert map_at_k(recommended, set(), 3) == 0.0
    assert mrr(recommended, set()) == 0.0
    assert hit_rate_at_k(recommended, set(), 3) == 0.0


def test_invalid_k():
    with pytest.raises(ValueError):
        precision_at_k([1, 2, 3], {1}, 0)
        

from src.evaluation.evaluator import evaluate_recommender


def test_evaluate_recommender():
    interactions = [
        {"user_id": 1, "item_id": 10, "split": "train"},
        {"user_id": 1, "item_id": 20, "split": "train"},
        {"user_id": 1, "item_id": 30, "split": "validation"},
        {"user_id": 2, "item_id": 40, "split": "train"},
        {"user_id": 2, "item_id": 50, "split": "validation"},
    ]

    def dummy_recommender(user_id, history, k):
        if user_id == 1:
            return [30, 99, 100][:k]

        return [999, 50, 1000][:k]

    result = evaluate_recommender(
        interactions,
        dummy_recommender,
        k=3,
    )

    assert result.users_evaluated == 2
    assert result.precision_at_k == pytest.approx(1 / 3)
    assert result.recall_at_k == pytest.approx(1.0)
    assert result.hit_rate_at_k == pytest.approx(1.0)
    assert result.mrr == pytest.approx((1.0 + 0.5) / 2)