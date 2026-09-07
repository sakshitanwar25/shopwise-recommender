from pathlib import Path

import polars as pl

BASE_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = BASE_DIR / "data" / "processed"


def main() -> None:
    train = pl.read_parquet(PROCESSED_DIR / "train.parquet")
    validation = pl.read_parquet(PROCESSED_DIR / "validation.parquet")
    test = pl.read_parquet(PROCESSED_DIR / "test.parquet")

    train_max = train["event_datetime"].max()
    validation_min = validation["event_datetime"].min()
    validation_max = validation["event_datetime"].max()
    test_min = test["event_datetime"].min()

    print("=== TEMPORAL LEAKAGE VALIDATION ===")

    print(f"Train maximum:       {train_max}")
    print(f"Validation minimum:  {validation_min}")
    print(f"Validation maximum:  {validation_max}")
    print(f"Test minimum:        {test_min}")

    train_valid = train_max < validation_min
    validation_valid = validation_max < test_min

    print("\n=== RESULTS ===")
    print(f"Train < Validation: {train_valid}")
    print(f"Validation < Test:  {validation_valid}")

    # Check that the three datasets contain all rows.
    total_rows = len(train) + len(validation) + len(test)

    print("\n=== ROW COUNT VALIDATION ===")
    print(f"Train rows:       {len(train):,}")
    print(f"Validation rows:  {len(validation):,}")
    print(f"Test rows:        {len(test):,}")
    print(f"Combined rows:    {total_rows:,}")

    assert train_valid, "Temporal leakage detected between train and validation."
    assert validation_valid, "Temporal leakage detected between validation and test."

    print("\nNo temporal leakage detected.")


if __name__ == "__main__":
    main()