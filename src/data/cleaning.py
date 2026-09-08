import polars as pl


def clean_interactions(df: pl.DataFrame) -> pl.DataFrame:
    """Clean and normalize raw interaction data."""

    # ---------------------------------------------------------
    # Required fields
    # ---------------------------------------------------------
    df = df.filter(
        pl.col("user_id").is_not_null()
        & pl.col("parent_asin").is_not_null()
        & pl.col("timestamp").is_not_null()
    )

    # ---------------------------------------------------------
    # Valid ratings
    # ---------------------------------------------------------
    df = df.filter(
        pl.col("rating").is_between(1.0, 5.0)
    )

    # ---------------------------------------------------------
    # Remove exact duplicate records
    # ---------------------------------------------------------
    df = df.unique(
        subset=[
        "user_id",
        "parent_asin",
        "timestamp",
        "rating",
        "text",
        "title",
        ],
        keep="first",
    )

    # ---------------------------------------------------------
    # Normalize event type
    # ---------------------------------------------------------
    df = df.with_columns(
        pl.lit("review").alias("event_type")
    )

    # ---------------------------------------------------------
    # Sort chronologically
    # ---------------------------------------------------------
    df = df.sort("event_ts")

    return df