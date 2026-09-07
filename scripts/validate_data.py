from pathlib import Path

import polars as pl

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_FILE = BASE_DIR / "data" / "raw" / "all_beauty_reviews.parquet"


def main() -> None:
    print("Loading raw dataset...")

    df = pl.read_parquet(RAW_FILE)

    print("\n=== BASIC INFO ===")
    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")
    print(f"Column names: {df.columns}")

    print("\n=== SCHEMA ===")
    print(df.schema)

    print("\n=== NULL VALUES ===")
    print(df.null_count())

    print("\n=== UNIQUE COUNTS ===")
    print(f"Unique users: {df['user_id'].n_unique():,}")
    print(f"Unique ASINs: {df['asin'].n_unique():,}")
    print(f"Unique parent ASINs: {df['parent_asin'].n_unique():,}")

    print("\n=== RATING RANGE ===")
    print(f"Minimum rating: {df['rating'].min()}")
    print(f"Maximum rating: {df['rating'].max()}")

    print("\n=== TIMESTAMP RANGE ===")
    print(f"Earliest timestamp: {df['timestamp'].min()}")
    print(f"Latest timestamp: {df['timestamp'].max()}")

    print("\n=== EXACT DUPLICATES ===")
    print(f"Duplicate rows: {len(df) - df.unique().height:,}")

    print("\n=== RATING DISTRIBUTION ===")
    print(
        df.group_by("rating")
        .agg(pl.len().alias("count"))
        .sort("rating")
    )

    print("\nValidation complete.")


if __name__ == "__main__":
    main()