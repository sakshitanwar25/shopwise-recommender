from pathlib import Path

import matplotlib.pyplot as plt
import polars as pl
import yaml

from src.data.transformations import (
    filter_interactions,
    recompute_dimensions,
)

BASE_DIR = Path(__file__).resolve().parents[1]
CONFIG_FILE = BASE_DIR / "config" / "pipeline.yaml"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
FILTERED_DIR = PROCESSED_DIR / "filtered"
REPORT_FILE = BASE_DIR / "docs" / "filtering-profile.md"
PLOTS_DIR = BASE_DIR / "docs" / "plots"


def load_config() -> dict:
    with CONFIG_FILE.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def calculate_sparsity(
    users: int,
    items: int,
    interactions: pl.DataFrame,
) -> float:
    if users == 0 or items == 0:
        return 1.0

    unique_pairs = interactions.select(
        ["user_id", "item_id"]
    ).unique().height

    return 1.0 - unique_pairs / (users * items)


def profile_dataset(
    users: pl.DataFrame,
    items: pl.DataFrame,
    interactions: pl.DataFrame,
) -> dict:
    user_counts = interactions.group_by("user_id").len()
    item_counts = interactions.group_by("item_id").len()

    interaction_count = len(interactions)

    unique_user_item_pairs = interactions.select(
        ["user_id", "item_id"]
    ).unique().height

    user_count = len(users)
    item_count = len(items)

    return {
        "users": user_count,
        "items": item_count,
        "interactions": interaction_count,
        "unique_user_item_pairs": unique_user_item_pairs,
        "sparsity": calculate_sparsity(
            user_count,
            item_count,
            interactions,
        ),
        "avg_interactions_per_user": (
            interaction_count / user_count
            if user_count
            else 0
        ),
        "avg_interactions_per_item": (
            interaction_count / item_count
            if item_count
            else 0
        ),
        "user_counts": user_counts,
        "item_counts": item_counts,
    }


def create_plots(
    before: dict,
    after: dict,
) -> None:
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    # User interaction distribution
    plt.figure(figsize=(8, 5))
    plt.hist(
        before["user_counts"]["len"].to_list(),
        bins=50,
    )
    plt.xlabel("Interactions per user")
    plt.ylabel("Number of users")
    plt.title("User Interaction Distribution - Before Filtering")
    plt.tight_layout()
    plt.savefig(
        PLOTS_DIR / "user_interactions_before.png",
        dpi=150,
    )
    plt.close()

    # Item interaction distribution
    plt.figure(figsize=(8, 5))
    plt.hist(
        before["item_counts"]["len"].to_list(),
        bins=50,
    )
    plt.xlabel("Interactions per item")
    plt.ylabel("Number of items")
    plt.title("Item Interaction Distribution - Before Filtering")
    plt.tight_layout()
    plt.savefig(
        PLOTS_DIR / "item_interactions_before.png",
        dpi=150,
    )
    plt.close()

    # Item long-tail distribution
    sorted_items = before["item_counts"].sort(
        "len",
        descending=True,
    )

    cumulative = (
        sorted_items
        .with_columns(
            pl.col("len")
            .cum_sum()
            .alias("cumulative_interactions")
        )
        .with_columns(
            (
                pl.col("cumulative_interactions")
                / before["interactions"]
            ).alias("cumulative_share")
        )
    )

    plt.figure(figsize=(8, 5))
    plt.plot(
        range(1, len(cumulative) + 1),
        cumulative["cumulative_share"].to_list(),
    )
    plt.xlabel("Items ranked by interaction count")
    plt.ylabel("Cumulative share of interactions")
    plt.title("Item Interaction Long Tail")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(
        PLOTS_DIR / "item_long_tail.png",
        dpi=150,
    )
    plt.close()


def create_report(
    before: dict,
    after: dict,
    min_user_interactions: int,
    min_item_interactions: int,
) -> None:
    top_1_percent = max(
        1,
        int(len(before["item_counts"]) * 0.01),
    )

    top_5_percent = max(
        1,
        int(len(before["item_counts"]) * 0.05),
    )

    top_10_percent = max(
        1,
        int(len(before["item_counts"]) * 0.10),
    )

    sorted_items = before["item_counts"].sort(
        "len",
        descending=True,
    )

    total = before["interactions"]

    top_1_share = (
        sorted_items.head(top_1_percent)["len"].sum()
        / total
    )

    top_5_share = (
        sorted_items.head(top_5_percent)["len"].sum()
        / total
    )

    top_10_share = (
        sorted_items.head(top_10_percent)["len"].sum()
        / total
    )

    report = f"""# Filtering and Data Profile

## Filtering configuration

- Minimum user interactions: `{min_user_interactions}`
- Minimum item interactions: `{min_item_interactions}`
- Filtering method: iterative user/item k-core filtering

## Dataset comparison

| Metric | Before | After |
|---|---:|---:|
| Users | {before["users"]:,} | {after["users"]:,} |
| Items | {before["items"]:,} | {after["items"]:,} |
| Interactions | {before["interactions"]:,} | {after["interactions"]:,} |
| Unique user-item pairs | {before["unique_user_item_pairs"]:,} | {after["unique_user_item_pairs"]:,} |
| Sparsity | {before["sparsity"]:.6%} | {after["sparsity"]:.6%} |
| Avg interactions/user | {before["avg_interactions_per_user"]:.2f} | {after["avg_interactions_per_user"]:.2f} |
| Avg interactions/item | {before["avg_interactions_per_item"]:.2f} | {after["avg_interactions_per_item"]:.2f} |

## Long-tail concentration

Share of all interactions generated by the most popular items:

| Item segment | Interaction share |
|---|---:|
| Top 1% | {top_1_share:.2%} |
| Top 5% | {top_5_share:.2%} |
| Top 10% | {top_10_share:.2%} |

## Interpretation

The filtering step removes users and items with insufficient interaction
history for collaborative recommendation modeling.

The filtering threshold was selected after comparing multiple
user/item interaction thresholds. A 2/2 threshold provides a more
useful balance between reducing extreme cold-start cases and retaining
enough users, items, and interactions for recommendation experiments.

The long-tail measurements show how concentrated user activity is among
popular items. This is important because a recommender that optimizes
only aggregate accuracy can become overly biased toward popular products.

Sparsity is calculated using unique user-item pairs rather than raw
interaction events because multiple events between the same user and
item occupy the same cell in a recommendation matrix.

Plots are available in `docs/plots/`.

"""

    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.write_text(report, encoding="utf-8")


def main() -> None:
    print("=== SHOPWISE DATA PROFILING ===")

    config = load_config()

    min_user_interactions = config["data"]["min_user_interactions"]
    min_item_interactions = config["data"]["min_item_interactions"]

    print("\n1. Loading processed data...")

    users = pl.read_parquet(
        PROCESSED_DIR / "users.parquet"
    )

    items = pl.read_parquet(
        PROCESSED_DIR / "items.parquet"
    )

    interactions = pl.read_parquet(
        PROCESSED_DIR / "interactions.parquet"
    )

    print(f"Users: {len(users):,}")
    print(f"Items: {len(items):,}")
    print(f"Interactions: {len(interactions):,}")

    print("\n2. Profiling before filtering...")

    before = profile_dataset(
        users,
        items,
        interactions,
    )

    print(
        f"Unique user-item pairs: "
        f"{before['unique_user_item_pairs']:,}"
    )

    print(
        f"Sparsity: {before['sparsity']:.6%}"
    )

    print("\n3. Applying interaction filters...")

    filtered_interactions = filter_interactions(
        interactions,
        min_user_interactions=min_user_interactions,
        min_item_interactions=min_item_interactions,
    )

    filtered_users, filtered_items = recompute_dimensions(
        users,
        items,
        filtered_interactions,
    )

    print("\n4. Profiling after filtering...")

    after = profile_dataset(
        filtered_users,
        filtered_items,
        filtered_interactions,
    )

    print(f"Users: {after['users']:,}")
    print(f"Items: {after['items']:,}")
    print(f"Interactions: {after['interactions']:,}")

    print(
        f"Unique user-item pairs: "
        f"{after['unique_user_item_pairs']:,}"
    )

    print(
        f"Sparsity: {after['sparsity']:.6%}"
    )

    print("\n5. Saving filtered datasets...")

    FILTERED_DIR.mkdir(parents=True, exist_ok=True)

    filtered_users.write_parquet(
        FILTERED_DIR / "users.parquet"
    )

    filtered_items.write_parquet(
        FILTERED_DIR / "items.parquet"
    )

    filtered_interactions.write_parquet(
        FILTERED_DIR / "interactions.parquet"
    )

    print(f"Saved to: {FILTERED_DIR}")

    print("\n6. Creating plots...")

    create_plots(
        before,
        after,
    )

    print("\n7. Creating report...")

    create_report(
        before,
        after,
        min_user_interactions,
        min_item_interactions,
    )

    print(f"Report: {REPORT_FILE}")

    print("\n=== PROFILING COMPLETE ===")


if __name__ == "__main__":
    main()