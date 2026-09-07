from pathlib import Path

import polars as pl

BASE_DIR = Path(__file__).resolve().parents[1]

RAW_FILE = BASE_DIR / "data" / "raw" / "all_beauty_reviews.parquet"
INTERIM_DIR = BASE_DIR / "data" / "interim"
OUTPUT_FILE = INTERIM_DIR / "clean_reviews.parquet"


def main() -> None:
    INTERIM_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading raw dataset...")
    df = pl.read_parquet(RAW_FILE)

    original_rows = len(df)

    print(f"Original rows: {original_rows:,}")

    # ---------------------------------------------------------
    # 1. Remove exact duplicate rows
    # ---------------------------------------------------------
    df = df.unique()

    duplicates_removed = original_rows - len(df)

    print(f"Exact duplicates removed: {duplicates_removed:,}")

    # ---------------------------------------------------------
    # 2. Validate required fields
    # ---------------------------------------------------------
    df = df.filter(
        pl.col("user_id").is_not_null()
        & pl.col("parent_asin").is_not_null()
        & pl.col("timestamp").is_not_null()
    )

    # ---------------------------------------------------------
    # 3. Keep only valid ratings
    # ---------------------------------------------------------
    df = df.filter(
        pl.col("rating").is_between(1.0, 5.0)
    )

    # ---------------------------------------------------------
    # 4. Convert Unix milliseconds → UTC datetime
    # ---------------------------------------------------------
    df = df.with_columns(
        pl.from_epoch(
            pl.col("timestamp"),
            time_unit="ms",
        ).alias("event_datetime")
    )

    # ---------------------------------------------------------
    # 5. Remove impossible timestamps
    # ---------------------------------------------------------
    df = df.filter(
        pl.col("event_datetime").is_not_null()
    )

    # ---------------------------------------------------------
    # 6. Sort chronologically
    # ---------------------------------------------------------
    df = df.sort("event_datetime")

    # ---------------------------------------------------------
    # Save cleaned dataset
    # ---------------------------------------------------------
    df.write_parquet(OUTPUT_FILE)

    print(f"Final rows: {len(df):,}")
    print(f"Rows removed: {original_rows - len(df):,}")
    print(f"Clean dataset saved to: {OUTPUT_FILE}")

    print("\n=== CLEAN DATA SCHEMA ===")
    print(df.schema)

    print("\n=== DATE RANGE ===")
    print(f"Earliest: {df['event_datetime'].min()}")
    print(f"Latest: {df['event_datetime'].max()}")

    print("\nCleaning complete.")


if __name__ == "__main__":
    main()