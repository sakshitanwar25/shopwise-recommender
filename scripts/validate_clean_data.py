from pathlib import Path

import polars as pl

BASE_DIR = Path(__file__).resolve().parents[1]
CLEAN_FILE = BASE_DIR / "data" / "interim" / "clean_reviews.parquet"


def main() -> None:
    df = pl.read_parquet(CLEAN_FILE)

    print("=== CLEAN DATA VALIDATION ===")

    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")

    print("\n=== NULL VALUES ===")
    print(df.null_count())

    print("\n=== RATING VALIDATION ===")
    print(f"Minimum rating: {df['rating'].min()}")
    print(f"Maximum rating: {df['rating'].max()}")

    invalid_ratings = df.filter(
        ~pl.col("rating").is_between(1.0, 5.0)
    )

    print(f"Invalid ratings: {len(invalid_ratings):,}")

    print("\n=== USER / ITEM VALIDATION ===")
    print(f"Unique users: {df['user_id'].n_unique():,}")
    print(f"Unique products: {df['parent_asin'].n_unique():,}")

    print("\n=== TIMESTAMP VALIDATION ===")
    print(f"Earliest: {df['event_datetime'].min()}")
    print(f"Latest: {df['event_datetime'].max()}")

    print("\n=== DUPLICATE VALIDATION ===")
    print(f"Exact duplicate rows: {len(df) - df.unique().height:,}")

    print("\n=== SORT VALIDATION ===")
    sorted_df = df.sort("event_datetime")
    is_sorted = df["event_datetime"].equals(sorted_df["event_datetime"])
    print(f"Chronologically sorted: {is_sorted}")

    print("\nValidation complete.")


if __name__ == "__main__":
    main()