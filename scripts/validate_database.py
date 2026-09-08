from pathlib import Path

import polars as pl

from src.database.connection import get_engine

BASE_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = BASE_DIR / "data" / "processed"


def get_database_counts() -> dict[str, int]:
    engine = get_engine()

    with engine.connect() as connection:
        users = connection.exec_driver_sql(
            "SELECT COUNT(*) FROM users"
        ).scalar_one()

        items = connection.exec_driver_sql(
            "SELECT COUNT(*) FROM items"
        ).scalar_one()

        interactions = connection.exec_driver_sql(
            "SELECT COUNT(*) FROM interaction_events"
        ).scalar_one()

    return {
        "users": users,
        "items": items,
        "interactions": interactions,
    }


def main() -> None:
    print("=== DATABASE VALIDATION ===")

    expected = {
        "users": len(
            pl.read_parquet(PROCESSED_DIR / "users.parquet")
        ),
        "items": len(
            pl.read_parquet(PROCESSED_DIR / "items.parquet")
        ),
        "interactions": len(
            pl.read_parquet(PROCESSED_DIR / "interactions.parquet")
        ),
    }

    actual = get_database_counts()

    print("\nExpected from Parquet:")
    for table, count in expected.items():
        print(f"{table}: {count:,}")

    print("\nActual in PostgreSQL:")
    for table, count in actual.items():
        print(f"{table}: {count:,}")

    print("\nValidation:")

    if expected != actual:
        raise RuntimeError(
            f"Database counts do not match.\n"
            f"Expected: {expected}\n"
            f"Actual: {actual}"
        )

    print("✓ All row counts match!")
    print("✓ Database validation successful!")


if __name__ == "__main__":
    main()