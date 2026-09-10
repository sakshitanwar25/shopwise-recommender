from pathlib import Path

import polars as pl

from src.data.transformations import filter_interactions

BASE_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = BASE_DIR / "data" / "processed"

USERS_FILE = PROCESSED_DIR / "users.parquet"
ITEMS_FILE = PROCESSED_DIR / "items.parquet"
INTERACTIONS_FILE = PROCESSED_DIR / "interactions.parquet"


def calculate_sparsity(
    users: int,
    items: int,
    interactions: int,
) -> float:
    if users == 0 or items == 0:
        return 1.0

    return 1.0 - interactions / (users * items)


def main() -> None:
    print("=== FILTER THRESHOLD COMPARISON ===")

    users = pl.read_parquet(USERS_FILE)
    items = pl.read_parquet(ITEMS_FILE)
    interactions = pl.read_parquet(INTERACTIONS_FILE)

    original_users = len(users)
    original_items = len(items)
    original_interactions = len(interactions)

    print("\nOriginal dataset:")
    print(f"Users: {original_users:,}")
    print(f"Items: {original_items:,}")
    print(f"Interactions: {original_interactions:,}")

    print("\nThreshold comparison:")
    print(
        f"{'Threshold':<12}"
        f"{'Users':>12}"
        f"{'Items':>12}"
        f"{'Interactions':>16}"
        f"{'Retention':>14}"
        f"{'Sparsity':>14}"
    )

    print("-" * 80)

    for threshold in range(1, 6):
        filtered = filter_interactions(
            interactions,
            min_user_interactions=threshold,
            min_item_interactions=threshold,
        )

        filtered_users = (
            filtered.select("user_id").unique().height
        )

        filtered_items = (
            filtered.select("item_id").unique().height
        )

        filtered_interactions = len(filtered)

        retention = (
            filtered_interactions / original_interactions
        )

        sparsity = calculate_sparsity(
            filtered_users,
            filtered_items,
            filtered_interactions,
        )

        print(
            f"{f'{threshold}/{threshold}':<12}"
            f"{filtered_users:>12,}"
            f"{filtered_items:>12,}"
            f"{filtered_interactions:>16,}"
            f"{retention:>13.2%}"
            f"{sparsity:>13.6%}"
        )


if __name__ == "__main__":
    main()