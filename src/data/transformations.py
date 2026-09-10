import polars as pl


def filter_interactions(
    interactions: pl.DataFrame,
    min_user_interactions: int = 5,
    min_item_interactions: int = 5,
) -> pl.DataFrame:
    """Keep interactions belonging to sufficiently active users/items."""

    filtered = interactions

    while True:
        original_count = len(filtered)

        user_counts = filtered.group_by("user_id").len().rename(
            {"len": "user_interaction_count"}
        )

        filtered = filtered.join(
            user_counts,
            on="user_id",
            how="inner",
        ).filter(
            pl.col("user_interaction_count")
            >= min_user_interactions
        ).drop("user_interaction_count")

        item_counts = filtered.group_by("item_id").len().rename(
            {"len": "item_interaction_count"}
        )

        filtered = filtered.join(
            item_counts,
            on="item_id",
            how="inner",
        ).filter(
            pl.col("item_interaction_count")
            >= min_item_interactions
        ).drop("item_interaction_count")

        if len(filtered) == original_count:
            break

    return filtered


def recompute_dimensions(
    users: pl.DataFrame,
    items: pl.DataFrame,
    interactions: pl.DataFrame,
) -> tuple[pl.DataFrame, pl.DataFrame]:
    """Keep only users and items present in filtered interactions."""

    filtered_users = users.join(
        interactions.select("user_id").unique(),
        on="user_id",
        how="inner",
    )

    filtered_items = items.join(
        interactions.select("item_id").unique(),
        on="item_id",
        how="inner",
    )

    return filtered_users, filtered_items