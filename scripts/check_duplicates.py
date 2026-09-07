from pathlib import Path

import polars as pl

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_FILE = BASE_DIR / "data" / "raw" / "all_beauty_reviews.parquet"


def main() -> None:
    df = pl.read_parquet(RAW_FILE)

    print("=== DUPLICATE INVESTIGATION ===")

    duplicate_count = len(df) - df.unique().height
    print(f"Exact duplicate rows: {duplicate_count:,}")

    duplicates = (
        df.group_by(
            [
                "user_id",
                "asin",
                "parent_asin",
                "timestamp",
                "rating",
            ]
        )
        .agg(pl.len().alias("count"))
        .filter(pl.col("count") > 1)
        .sort("count", descending=True)
    )

    print("\n=== REPEATED USER-ITEM-TIMESTAMP RECORDS ===")
    print(f"Groups: {len(duplicates):,}")

    print("\nTop repeated records:")
    print(duplicates.head(10))

    print("\n=== REPEATED USER-ITEM PAIRS ===")

    repeated_pairs = (
        df.group_by(["user_id", "parent_asin"])
        .agg(pl.len().alias("interaction_count"))
        .filter(pl.col("interaction_count") > 1)
        .sort("interaction_count", descending=True)
    )

    print(f"Repeated user-item pairs: {len(repeated_pairs):,}")

    print("\nTop repeated user-item pairs:")
    print(repeated_pairs.head(10))


if __name__ == "__main__":
    main()