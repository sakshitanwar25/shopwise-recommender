from pathlib import Path

import polars as pl

REQUIRED_COLUMNS = [
    "rating",
    "title",
    "text",
    "asin",
    "parent_asin",
    "user_id",
    "timestamp",
    "helpful_vote",
    "verified_purchase",
]


def read_raw_data(path: Path, limit: int | None = None) -> pl.DataFrame:
    """Read the raw Amazon reviews dataset."""
    df = pl.read_parquet(path)

    if limit is not None:
        df = df.head(limit)

    return df


def select_relevant_columns(df: pl.DataFrame) -> pl.DataFrame:
    """Keep only columns required by the ingestion pipeline."""
    available_columns = [
        column for column in REQUIRED_COLUMNS if column in df.columns
    ]

    return df.select(available_columns)


def normalize_timestamps(df: pl.DataFrame) -> pl.DataFrame:
    """Convert Unix timestamps in milliseconds to UTC datetimes."""
    return df.with_columns(
        pl.from_epoch(
            pl.col("timestamp"),
            time_unit="ms",
        )
        .dt.replace_time_zone("UTC")
        .alias("event_ts")
    )