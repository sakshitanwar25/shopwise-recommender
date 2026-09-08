from pathlib import Path

import polars as pl

from src.data.validation import (
    validate_interactions,
    validate_items,
    validate_referential_integrity,
    validate_users,
)

BASE_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = BASE_DIR / "data" / "processed"


def main() -> None:
    print("=== SHOPWISE DATA VALIDATION ===")

    print("\n1. Loading processed Parquet files...")

    users = pl.read_parquet(PROCESSED_DIR / "users.parquet")
    items = pl.read_parquet(PROCESSED_DIR / "items.parquet")
    interactions = pl.read_parquet(
        PROCESSED_DIR / "interactions.parquet"
    )

    print(f"Users: {len(users):,}")
    print(f"Items: {len(items):,}")
    print(f"Interactions: {len(interactions):,}")

    print("\n2. Validating users...")
    user_result = validate_users(users)

    print(
        f"Users: {user_result['count']:,}, "
        f"invalid: {user_result['invalid']:,}"
    )

    print("\n3. Validating items...")
    item_result = validate_items(items)

    print(
        f"Items: {item_result['count']:,}, "
        f"invalid: {item_result['invalid']:,}"
    )

    print("\n4. Validating interactions...")
    interaction_result = validate_interactions(interactions)

    print(
        f"Interactions: {interaction_result['count']:,}, "
        f"invalid: {interaction_result['invalid']:,}"
    )

    print("\n5. Checking referential integrity...")

    integrity_result = validate_referential_integrity(
        users,
        items,
        interactions,
    )

    print(
        "Referential integrity issues: "
        f"{integrity_result['total_issues']:,}"
    )

    print("\n=== VALIDATION SUMMARY ===")

    print(
        f"Users: {user_result['count']:,}, "
        f"invalid: {user_result['invalid']:,}"
    )

    print(
        f"Items: {item_result['count']:,}, "
        f"invalid: {item_result['invalid']:,}"
    )

    print(
        f"Interactions: {interaction_result['count']:,}, "
        f"invalid: {interaction_result['invalid']:,}"
    )

    print(
        "Duplicates detected: "
        f"{interaction_result['duplicate_identity']:,}"
    )

    print(
        "Referential integrity issues: "
        f"{integrity_result['total_issues']:,}"
    )

    critical_issues = (
        user_result["invalid"]
        + item_result["invalid"]
        + interaction_result["invalid"]
        + integrity_result["total_issues"]
    )

    print(f"\nTotal critical issues: {critical_issues:,}")

    if critical_issues > 0:
        raise SystemExit(
            "Validation failed: critical data-quality issues detected."
        )

    print("\n✓ Validation passed!")
    print("✓ No critical data-quality issues found.")


if __name__ == "__main__":
    main()