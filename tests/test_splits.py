from pathlib import Path

import polars as pl

BASE_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = BASE_DIR / "data" / "processed"

TRAIN_FILE = PROCESSED_DIR / "train_interactions.parquet"
VALIDATION_FILE = PROCESSED_DIR / "validation_interactions.parquet"
TEST_FILE = PROCESSED_DIR / "test_interactions.parquet"


def load_splits() -> tuple[
    pl.DataFrame,
    pl.DataFrame,
    pl.DataFrame,
]:
    train = pl.read_parquet(TRAIN_FILE)
    validation = pl.read_parquet(VALIDATION_FILE)
    test = pl.read_parquet(TEST_FILE)

    return train, validation, test


def test_split_files_exist() -> None:
    assert TRAIN_FILE.exists()
    assert VALIDATION_FILE.exists()
    assert TEST_FILE.exists()


def test_splits_are_not_empty() -> None:
    train, validation, test = load_splits()

    assert len(train) > 0
    assert len(validation) > 0
    assert len(test) > 0


def test_temporal_ordering() -> None:
    train, validation, test = load_splits()

    train_max = train["event_ts"].max()
    validation_min = validation["event_ts"].min()

    validation_max = validation["event_ts"].max()
    test_min = test["event_ts"].min()

    assert train_max <= validation_min
    assert validation_max <= test_min


def test_no_overlapping_events() -> None:
    train, validation, test = load_splits()

    train_timestamps = set(
        train["event_ts"].to_list()
    )

    validation_timestamps = set(
        validation["event_ts"].to_list()
    )

    test_timestamps = set(
        test["event_ts"].to_list()
    )

    assert not (
        train_timestamps & validation_timestamps
    )

    assert not (
        train_timestamps & test_timestamps
    )

    assert not (
        validation_timestamps & test_timestamps
    )


def test_split_counts() -> None:
    train, validation, test = load_splits()

    assert len(train) == 485_976
    assert len(validation) == 104_138
    assert len(test) == 104_138


def test_all_interactions_are_preserved() -> None:
    train, validation, test = load_splits()

    total = (
        len(train)
        + len(validation)
        + len(test)
    )

    assert total == 694_252