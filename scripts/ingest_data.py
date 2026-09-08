import argparse
import hashlib
from pathlib import Path

import polars as pl

from src.data.cleaning import clean_interactions
from src.data.loaders import (
    normalize_timestamps,
    read_raw_data,
    select_relevant_columns,
)

BASE_DIR = Path(__file__).resolve().parents[1]

RAW_FILE = BASE_DIR / "data" / "raw" / "all_beauty_reviews.parquet"

INTERIM_DIR = BASE_DIR / "data" / "interim"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

RAW_CLEAN_FILE = INTERIM_DIR / "raw_clean.parquet"
USERS_FILE = PROCESSED_DIR / "users.parquet"
ITEMS_FILE = PROCESSED_DIR / "items.parquet"
INTERACTIONS_FILE = PROCESSED_DIR / "interactions.parquet"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Ingest Amazon reviews into normalized Parquet files."
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional number of rows to process.",
    )

    return parser.parse_args()


def stable_id(source_id: str) -> int:
    """Convert a source ID into a stable positive BIGINT."""
    digest = hashlib.sha256(source_id.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], byteorder="big") & 0x7FFFFFFFFFFFFFFF


def create_deterministic_ids(
    df: pl.DataFrame,
) -> tuple[pl.DataFrame, pl.DataFrame, pl.DataFrame]:
    users = (
        df.select("user_id")
        .unique()
        .sort("user_id")
        .with_columns(
            pl.col("user_id")
            .map_elements(
                stable_id,
                return_dtype=pl.Int64,
            )
            .alias("internal_user_id")
        )
        .rename({"user_id": "source_user_id"})
        .select(["internal_user_id", "source_user_id"])
        .rename({"internal_user_id": "user_id"})
    )

    items = (
        df.select(["parent_asin", "title"])
        .unique(subset=["parent_asin"])
        .sort("parent_asin")
        .with_columns(
            pl.col("parent_asin")
            .map_elements(
                stable_id,
                return_dtype=pl.Int64,
            )
            .alias("internal_item_id")
        )
        .rename({"parent_asin": "source_item_id"})
        .select(["internal_item_id", "source_item_id", "title"])
        .rename({"internal_item_id": "item_id"})
    )

    interactions = (
        df.rename(
            {
                "user_id": "source_user_id",
                "parent_asin": "source_item_id",
            }
        )
        .join(
            users,
            on="source_user_id",
            how="inner",
        )
        .join(
            items,
            on="source_item_id",
            how="inner",
        )
        .select(
            [
                "user_id",
                "item_id",
                "event_type",
                "rating",
                "text",
                "event_ts",
                "helpful_vote",
                "verified_purchase",
            ]
        )
        .rename({"text": "review_text"})
    )

    return users, items, interactions

def main() -> None:
    args = parse_args()

    INTERIM_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    print("=== SHOPWISE DATA INGESTION ===")

    print("\n1. Reading raw data...")
    df = read_raw_data(RAW_FILE, args.limit)

    print(f"Raw rows: {len(df):,}")

    print("\n2. Selecting relevant columns...")
    df = select_relevant_columns(df)

    print("\n3. Normalizing timestamps...")
    df = normalize_timestamps(df)

    print("\n4. Cleaning interactions...")
    df = clean_interactions(df)

    print(f"Clean rows: {len(df):,}")

    # ---------------------------------------------------------
    # Save cleaned intermediate data
    # ---------------------------------------------------------
    df.write_parquet(RAW_CLEAN_FILE)

    print(f"\nSaved: {RAW_CLEAN_FILE}")

    # ---------------------------------------------------------
    # Create normalized datasets
    # ---------------------------------------------------------
    print("\n5. Creating deterministic internal IDs...")

    users, items, interactions = create_deterministic_ids(df)

    # ---------------------------------------------------------
    # Save users
    # ---------------------------------------------------------
    users.write_parquet(USERS_FILE)

    print(f"Users: {len(users):,}")
    print(f"Saved: {USERS_FILE}")

    # ---------------------------------------------------------
    # Save items
    # ---------------------------------------------------------
    items.write_parquet(ITEMS_FILE)

    print(f"Items: {len(items):,}")
    print(f"Saved: {ITEMS_FILE}")

    # ---------------------------------------------------------
    # Save interactions
    # ---------------------------------------------------------
    interactions.write_parquet(INTERACTIONS_FILE)

    print(f"Interactions: {len(interactions):,}")
    print(f"Saved: {INTERACTIONS_FILE}")

    print("\n=== INGESTION COMPLETE ===")


if __name__ == "__main__":
    main()