from pathlib import Path

import polars as pl

BASE_DIR = Path(__file__).resolve().parents[1]

INPUT_FILE = BASE_DIR / "data" / "interim" / "clean_reviews.parquet"
OUTPUT_DIR = BASE_DIR / "data" / "processed"


TRAIN_RATIO = 0.70
VALIDATION_RATIO = 0.15
TEST_RATIO = 0.15


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading cleaned dataset...")

    df = pl.read_parquet(INPUT_FILE)

    print(f"Total rows: {len(df):,}")

    # Make sure the dataset is chronologically ordered.
    df = df.sort("event_datetime")

    # Calculate chronological boundaries.
    train_boundary = df.select(
        pl.col("event_datetime")
        .quantile(TRAIN_RATIO)
    ).item()

    validation_boundary = df.select(
        pl.col("event_datetime")
        .quantile(TRAIN_RATIO + VALIDATION_RATIO)
    ).item()

    print("\n=== SPLIT BOUNDARIES ===")
    print(f"Train ends before:       {train_boundary}")
    print(f"Validation ends before:  {validation_boundary}")

    # ---------------------------------------------------------
    # Train
    # ---------------------------------------------------------

    train = df.filter(
        pl.col("event_datetime") < train_boundary
    )

    # ---------------------------------------------------------
    # Validation
    # ---------------------------------------------------------

    validation = df.filter(
        (pl.col("event_datetime") >= train_boundary)
        & (pl.col("event_datetime") < validation_boundary)
    )

    # ---------------------------------------------------------
    # Test
    # ---------------------------------------------------------

    test = df.filter(
        pl.col("event_datetime") >= validation_boundary
    )

    # ---------------------------------------------------------
    # Save
    # ---------------------------------------------------------

    train_file = OUTPUT_DIR / "train.parquet"
    validation_file = OUTPUT_DIR / "validation.parquet"
    test_file = OUTPUT_DIR / "test.parquet"

    train.write_parquet(train_file)
    validation.write_parquet(validation_file)
    test.write_parquet(test_file)

    # ---------------------------------------------------------
    # Report
    # ---------------------------------------------------------

    total = len(df)

    print("\n=== SPLIT RESULTS ===")

    print(
        f"Train:       {len(train):,} "
        f"({len(train) / total:.2%})"
    )

    print(
        f"Validation:  {len(validation):,} "
        f"({len(validation) / total:.2%})"
    )

    print(
        f"Test:        {len(test):,} "
        f"({len(test) / total:.2%})"
    )

    print(
        f"Total:       {len(train) + len(validation) + len(test):,}"
    )

    print("\n=== DATE RANGES ===")

    print(
        f"Train:       {train['event_datetime'].min()} "
        f"→ {train['event_datetime'].max()}"
    )

    print(
        f"Validation:  {validation['event_datetime'].min()} "
        f"→ {validation['event_datetime'].max()}"
    )

    print(
        f"Test:        {test['event_datetime'].min()} "
        f"→ {test['event_datetime'].max()}"
    )

    print("\nSplit complete.")


if __name__ == "__main__":
    main()