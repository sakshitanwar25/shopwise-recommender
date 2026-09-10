from pathlib import Path

import polars as pl

BASE_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = BASE_DIR / "data" / "processed"

INTERACTIONS_FILE = PROCESSED_DIR / "interactions.parquet"

TRAIN_FILE = PROCESSED_DIR / "train_interactions.parquet"
VALIDATION_FILE = PROCESSED_DIR / "validation_interactions.parquet"
TEST_FILE = PROCESSED_DIR / "test_interactions.parquet"

TRAIN_RATIO = 0.70
VALIDATION_RATIO = 0.15
TEST_RATIO = 0.15


def split_interactions(
    interactions: pl.DataFrame,
) -> tuple[pl.DataFrame, pl.DataFrame, pl.DataFrame]:
    interactions = interactions.sort("event_ts")

    total_rows = len(interactions)

    train_end = int(total_rows * TRAIN_RATIO)
    validation_end = int(
        total_rows * (TRAIN_RATIO + VALIDATION_RATIO)
    )

    train = interactions[:train_end]

    validation = interactions[
        train_end:validation_end
    ]

    test = interactions[
        validation_end:
    ]

    return train, validation, test


def validate_splits(
    train: pl.DataFrame,
    validation: pl.DataFrame,
    test: pl.DataFrame,
) -> None:
    if train.is_empty():
        raise ValueError("Training split is empty.")

    if validation.is_empty():
        raise ValueError("Validation split is empty.")

    if test.is_empty():
        raise ValueError("Test split is empty.")

    train_max = train["event_ts"].max()
    validation_min = validation["event_ts"].min()
    validation_max = validation["event_ts"].max()
    test_min = test["event_ts"].min()

    if train_max > validation_min:
        raise ValueError(
            "Temporal leakage: training data extends "
            "beyond validation data."
        )

    if validation_max > test_min:
        raise ValueError(
            "Temporal leakage: validation data extends "
            "beyond test data."
        )

    train_events = set(
        train["event_ts"].to_list()
    )
    validation_events = set(
        validation["event_ts"].to_list()
    )
    test_events = set(
        test["event_ts"].to_list()
    )

    if train_events & validation_events:
        raise ValueError(
            "Overlapping event timestamps between "
            "train and validation."
        )

    if train_events & test_events:
        raise ValueError(
            "Overlapping event timestamps between "
            "train and test."
        )

    if validation_events & test_events:
        raise ValueError(
            "Overlapping event timestamps between "
            "validation and test."
        )


def calculate_split_stats(
    split: pl.DataFrame,
    total_users: int,
    total_items: int,
) -> dict:
    users = split.select("user_id").unique().height
    items = split.select("item_id").unique().height
    interactions = len(split)

    return {
        "users": users,
        "items": items,
        "interactions": interactions,
        "user_percentage": (
            users / total_users * 100
            if total_users
            else 0
        ),
        "item_percentage": (
            items / total_items * 100
            if total_items
            else 0
        ),
    }


def create_report(
    interactions: pl.DataFrame,
    train: pl.DataFrame,
    validation: pl.DataFrame,
    test: pl.DataFrame,
) -> None:
    report_file = BASE_DIR / "docs" / "split-report.md"
    report_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    total_users = (
        interactions.select("user_id").unique().height
    )

    total_items = (
        interactions.select("item_id").unique().height
    )

    train_stats = calculate_split_stats(
        train,
        total_users,
        total_items,
    )

    validation_stats = calculate_split_stats(
        validation,
        total_users,
        total_items,
    )

    test_stats = calculate_split_stats(
        test,
        total_users,
        total_items,
    )

    train_min = train["event_ts"].min()
    train_max = train["event_ts"].max()

    validation_min = validation["event_ts"].min()
    validation_max = validation["event_ts"].max()

    test_min = test["event_ts"].min()
    test_max = test["event_ts"].max()

    report = f"""# Temporal Split Report

## Split strategy

The interaction dataset is split chronologically using:

- Training: earliest 70%
- Validation: next 15%
- Test: final 15%

The split is based on `event_ts` and does not randomly shuffle
interactions.

This prevents future interactions from being used to train the
recommendation model.

## Overall dataset

- Total users: {total_users:,}
- Total items: {total_items:,}
- Total interactions: {len(interactions):,}

## Split boundaries

| Split | Start | End |
|---|---|---|
| Train | {train_min} | {train_max} |
| Validation | {validation_min} | {validation_max} |
| Test | {test_min} | {test_max} |

## Split statistics

| Split | Interactions | Users | % Users | Items | % Items |
|---|---:|---:|---:|---:|---:|
| Train | {train_stats["interactions"]:,} | {train_stats["users"]:,} | {train_stats["user_percentage"]:.2f}% | {train_stats["items"]:,} | {train_stats["item_percentage"]:.2f}% |
| Validation | {validation_stats["interactions"]:,} | {validation_stats["users"]:,} | {validation_stats["user_percentage"]:.2f}% | {validation_stats["items"]:,} | {validation_stats["item_percentage"]:.2f}% |
| Test | {test_stats["interactions"]:,} | {test_stats["users"]:,} | {test_stats["user_percentage"]:.2f}% | {test_stats["items"]:,} | {test_stats["item_percentage"]:.2f}% |

## Leakage checks

- `max(train.event_ts) <= min(validation.event_ts)`
- `max(validation.event_ts) <= min(test.event_ts)`
- No overlapping event timestamps between splits

All checks passed during split generation.

## Important modeling note

User and item eligibility for recommendation training should be
determined using the training period only. Future validation and test
interactions must not influence training-time filtering decisions.

"""

    report_file.write_text(
        report,
        encoding="utf-8",
    )

    print(f"Report saved to: {report_file}")


def main() -> None:
    print("=== TEMPORAL DATA SPLITTING ===")

    print("\n1. Loading interactions...")

    interactions = pl.read_parquet(
        INTERACTIONS_FILE
    )

    print(f"Interactions: {len(interactions):,}")

    print("\n2. Creating chronological splits...")

    train, validation, test = split_interactions(
        interactions
    )

    print(f"Train: {len(train):,}")
    print(f"Validation: {len(validation):,}")
    print(f"Test: {len(test):,}")

    print("\n3. Validating splits...")

    validate_splits(
        train,
        validation,
        test,
    )

    print("Temporal ordering: PASS")
    print("Overlap checks: PASS")

    print("\n4. Saving splits...")

    train.write_parquet(TRAIN_FILE)
    validation.write_parquet(VALIDATION_FILE)
    test.write_parquet(TEST_FILE)

    print(f"Train: {TRAIN_FILE}")
    print(f"Validation: {VALIDATION_FILE}")
    print(f"Test: {TEST_FILE}")

    print("\n5. Creating split report...")

    create_report(
        interactions,
        train,
        validation,
        test,
    )

    print("\n=== SPLITTING COMPLETE ===")


if __name__ == "__main__":
    main()