from pathlib import Path

import polars as pl
import psycopg

from src.config import (
    DB_HOST,
    DB_NAME,
    DB_PASSWORD,
    DB_PORT,
    DB_USER,
)

BASE_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = BASE_DIR / "data" / "processed"

USERS_FILE = PROCESSED_DIR / "users.parquet"
ITEMS_FILE = PROCESSED_DIR / "items.parquet"
INTERACTIONS_FILE = PROCESSED_DIR / "interactions.parquet"


def get_connection() -> psycopg.Connection:
    """Create a PostgreSQL connection."""
    return psycopg.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )


def load_users(
    conn: psycopg.Connection,
    users: pl.DataFrame,
) -> None:
    """Bulk-load users into PostgreSQL."""
    rows = users.iter_rows()

    with conn.cursor() as cur, cur.copy(
        """
            COPY users (user_id, source_user_id)
            FROM STDIN
            """
    ) as copy:
        for row in rows:
            copy.write_row(row)


def load_items(
    conn: psycopg.Connection,
    items: pl.DataFrame,
) -> None:
    """Bulk-load items into PostgreSQL."""
    rows = items.iter_rows()

    with conn.cursor() as cur, cur.copy(
        """
            COPY items (item_id, source_item_id, title)
            FROM STDIN
            """
    ) as copy:
        for row in rows:
            copy.write_row(row)


def load_interactions(
    conn: psycopg.Connection,
    interactions: pl.DataFrame,
) -> None:
    """Bulk-load interaction events into PostgreSQL."""

    rows = interactions.iter_rows()

    with conn.cursor() as cur, cur.copy(
        """
            COPY interaction_events (
                user_id,
                item_id,
                event_type,
                rating,
                review_text,
                event_ts,
                raw_event
            )
            FROM STDIN
            """
    ) as copy:
        for row in rows:
            (
                user_id,
                item_id,
                event_type,
                rating,
                review_text,
                event_ts,
                helpful_vote,
                verified_purchase,
            ) = row

            raw_event = {
                "helpful_vote": helpful_vote,
                "verified_purchase": verified_purchase,
            }

            copy.write_row(
                (
                    user_id,
                    item_id,
                    event_type,
                    rating,
                    review_text,
                    event_ts,
                    psycopg.types.json.Jsonb(raw_event),
                )
            )


def main() -> None:
    print("=== POSTGRESQL DATA LOAD ===")

    print("\n1. Reading processed Parquet files...")

    users = pl.read_parquet(USERS_FILE)
    items = pl.read_parquet(ITEMS_FILE)
    interactions = pl.read_parquet(INTERACTIONS_FILE)

    print(f"Users: {len(users):,}")
    print(f"Items: {len(items):,}")
    print(f"Interactions: {len(interactions):,}")

    print("\n2. Connecting to PostgreSQL...")

    with get_connection() as conn:
        print("PostgreSQL connection successful.")

        print("\n3. Clearing existing Phase 1 data...")

        with conn.cursor() as cur:
            cur.execute(
                """
                TRUNCATE
                    interaction_events,
                    items,
                    users
                RESTART IDENTITY CASCADE
                """
            )

        print("Existing data cleared.")

        print("\n4. Loading users...")
        load_users(conn, users)
        print(f"Loaded {len(users):,} users.")

        print("\n5. Loading items...")
        load_items(conn, items)
        print(f"Loaded {len(items):,} items.")

        print("\n6. Loading interactions...")
        load_interactions(conn, interactions)
        print(f"Loaded {len(interactions):,} interactions.")

        conn.commit()

    print("\n=== POSTGRESQL LOAD COMPLETE ===")


if __name__ == "__main__":
    main()