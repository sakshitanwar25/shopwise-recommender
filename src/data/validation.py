import polars as pl


def validate_users(df: pl.DataFrame) -> dict[str, int]:
    """Validate the users dimension table."""
    null_user_ids = df.filter(
        pl.col("user_id").is_null()
    ).height

    duplicate_user_ids = (
        df.group_by("user_id")
        .len()
        .filter(pl.col("len") > 1)
        .height
    )

    invalid = null_user_ids + duplicate_user_ids

    return {
        "count": len(df),
        "null_ids": null_user_ids,
        "duplicate_ids": duplicate_user_ids,
        "invalid": invalid,
    }


def validate_items(df: pl.DataFrame) -> dict[str, int]:
    """Validate the items dimension table."""
    null_item_ids = df.filter(
        pl.col("item_id").is_null()
    ).height

    duplicate_item_ids = (
        df.group_by("item_id")
        .len()
        .filter(pl.col("len") > 1)
        .height
    )

    invalid = null_item_ids + duplicate_item_ids

    return {
        "count": len(df),
        "null_ids": null_item_ids,
        "duplicate_ids": duplicate_item_ids,
        "invalid": invalid,
    }


def validate_interactions(df: pl.DataFrame) -> dict[str, int]:
    """Validate the interaction fact table."""

    null_user_ids = df.filter(
        pl.col("user_id").is_null()
    ).height

    null_item_ids = df.filter(
        pl.col("item_id").is_null()
    ).height

    invalid_ratings = df.filter(
        pl.col("rating").is_null()
        | ~pl.col("rating").is_between(1.0, 5.0)
    ).height

    invalid_timestamps = df.filter(
        pl.col("event_ts").is_null()
    ).height

    future_timestamps = df.filter(
        pl.col("event_ts") > pl.datetime(
            2026,
            9,
            8,
            time_zone="UTC",
        )
    ).height

    duplicate_identity = (
        df.group_by(
            [
                "user_id",
                "item_id",
                "event_ts",
                "event_type",
                "rating",
            ]
        )
        .len()
        .filter(pl.col("len") > 1)
        .height
    )

    invalid = (
        null_user_ids
        + null_item_ids
        + invalid_ratings
        + invalid_timestamps
        + future_timestamps
        + duplicate_identity
    )

    return {
        "count": len(df),
        "null_user_ids": null_user_ids,
        "null_item_ids": null_item_ids,
        "invalid_ratings": invalid_ratings,
        "invalid_timestamps": invalid_timestamps,
        "future_timestamps": future_timestamps,
        "duplicate_identity": duplicate_identity,
        "invalid": invalid,
    }


def validate_referential_integrity(
    users_df: pl.DataFrame,
    items_df: pl.DataFrame,
    interactions_df: pl.DataFrame,
) -> dict[str, int]:
    """Ensure every interaction references an existing user and item."""

    user_issues = (
        interactions_df
        .join(
            users_df.select("user_id"),
            on="user_id",
            how="anti",
        )
        .height
    )

    item_issues = (
        interactions_df
        .join(
            items_df.select("item_id"),
            on="item_id",
            how="anti",
        )
        .height
    )

    return {
        "user_issues": user_issues,
        "item_issues": item_issues,
        "total_issues": user_issues + item_issues,
    }