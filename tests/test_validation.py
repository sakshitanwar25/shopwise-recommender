import polars as pl

from src.data.validation import (
    validate_interactions,
    validate_items,
    validate_referential_integrity,
    validate_users,
)


def test_validate_users_detects_null_ids():
    df = pl.DataFrame(
        {
            "user_id": [1, None, 3],
            "source_user_id": ["u1", "u2", "u3"],
        }
    )

    result = validate_users(df)

    assert result["count"] == 3
    assert result["null_ids"] == 1
    assert result["invalid"] >= 1


def test_validate_users_detects_duplicate_ids():
    df = pl.DataFrame(
        {
            "user_id": [1, 1, 2],
            "source_user_id": ["u1", "u1_duplicate", "u2"],
        }
    )

    result = validate_users(df)

    assert result["duplicate_ids"] == 1
    assert result["invalid"] >= 1


def test_validate_items_detects_null_ids():
    df = pl.DataFrame(
        {
            "item_id": [1, None, 3],
            "source_item_id": ["i1", "i2", "i3"],
            "title": ["A", "B", "C"],
        }
    )

    result = validate_items(df)

    assert result["count"] == 3
    assert result["null_ids"] == 1
    assert result["invalid"] >= 1


def test_validate_items_detects_duplicate_ids():
    df = pl.DataFrame(
        {
            "item_id": [1, 1, 2],
            "source_item_id": ["i1", "i1_duplicate", "i2"],
            "title": ["A", "B", "C"],
        }
    )

    result = validate_items(df)

    assert result["duplicate_ids"] == 1
    assert result["invalid"] >= 1


def test_validate_interactions_detects_invalid_rating():
    df = pl.DataFrame(
        {
            "user_id": [1, 2, 3],
            "item_id": [10, 20, 30],
            "event_type": ["review", "review", "review"],
            "rating": [5.0, 0.0, 6.0],
            "review_text": ["A", "B", "C"],
            "event_ts": [
                "2023-01-01T00:00:00Z",
                "2023-01-02T00:00:00Z",
                "2023-01-03T00:00:00Z",
            ],
        }
    ).with_columns(
        pl.col("event_ts").str.to_datetime(time_zone="UTC")
    )

    result = validate_interactions(df)

    assert result["invalid_ratings"] == 2
    assert result["invalid"] >= 2


def test_validate_interactions_detects_null_ids():
    df = pl.DataFrame(
        {
            "user_id": [1, None],
            "item_id": [10, 20],
            "event_type": ["review", "review"],
            "rating": [5.0, 4.0],
            "review_text": ["A", "B"],
            "event_ts": [
                "2023-01-01T00:00:00Z",
                "2023-01-02T00:00:00Z",
            ],
        }
    ).with_columns(
        pl.col("event_ts").str.to_datetime(time_zone="UTC")
    )

    result = validate_interactions(df)

    assert result["null_user_ids"] == 1
    assert result["invalid"] >= 1


def test_validate_interactions_detects_future_timestamp():
    df = pl.DataFrame(
        {
            "user_id": [1],
            "item_id": [10],
            "event_type": ["review"],
            "rating": [5.0],
            "review_text": ["Test"],
            "event_ts": ["2027-01-01T00:00:00Z"],
        }
    ).with_columns(
        pl.col("event_ts").str.to_datetime(time_zone="UTC")
    )

    result = validate_interactions(df)

    assert result["future_timestamps"] == 1
    assert result["invalid"] >= 1


def test_validate_interactions_detects_duplicate_identity():
    df = pl.DataFrame(
        {
            "user_id": [1, 1],
            "item_id": [10, 10],
            "event_type": ["review", "review"],
            "rating": [5.0, 5.0],
            "review_text": ["Same review", "Same review"],
            "event_ts": [
                "2023-01-01T00:00:00Z",
                "2023-01-01T00:00:00Z",
            ],
        }
    ).with_columns(
        pl.col("event_ts").str.to_datetime(time_zone="UTC")
    )

    result = validate_interactions(df)

    assert result["duplicate_identity"] == 1
    assert result["invalid"] >= 1


def test_validate_referential_integrity_detects_missing_user():
    users = pl.DataFrame({"user_id": [1, 2]})

    items = pl.DataFrame({"item_id": [10, 20]})

    interactions = pl.DataFrame(
        {
            "user_id": [1, 3],
            "item_id": [10, 20],
        }
    )

    result = validate_referential_integrity(
        users,
        items,
        interactions,
    )

    assert result["user_issues"] == 1
    assert result["item_issues"] == 0
    assert result["total_issues"] == 1


def test_validate_referential_integrity_detects_missing_item():
    users = pl.DataFrame({"user_id": [1, 2]})

    items = pl.DataFrame({"item_id": [10, 20]})

    interactions = pl.DataFrame(
        {
            "user_id": [1, 2],
            "item_id": [10, 99],
        }
    )

    result = validate_referential_integrity(
        users,
        items,
        interactions,
    )

    assert result["user_issues"] == 0
    assert result["item_issues"] == 1
    assert result["total_issues"] == 1