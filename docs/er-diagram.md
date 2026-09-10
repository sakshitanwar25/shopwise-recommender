# Entity Relationship Diagram

## 1. Overview

ShopWise uses PostgreSQL as the application-oriented relational database.

The main entities are:

- `users`
- `items`
- `categories`
- `interaction_events`

The central relationship is between users, items, and their interaction
events.

---

## 2. ER Diagram

```mermaid
erDiagram

    USERS ||--o{ INTERACTION_EVENTS : creates
    ITEMS ||--o{ INTERACTION_EVENTS : receives
    CATEGORIES ||--o{ ITEMS : contains

    USERS {
        BIGINT user_id PK
        TEXT source_user_id UK
        TIMESTAMPTZ created_at
        TIMESTAMPTZ updated_at
    }

    ITEMS {
        BIGINT item_id PK
        TEXT source_item_id UK
        TEXT title
        TEXT description
        TEXT brand
        BIGINT category_id FK
        NUMERIC price
        NUMERIC average_rating
        INTEGER review_count
        TIMESTAMPTZ item_created_at
        JSONB raw_metadata
        TIMESTAMPTZ updated_at
    }

    CATEGORIES {
        BIGINT category_id PK
        TEXT category_path UK
    }

    INTERACTION_EVENTS {
        BIGINT event_id PK
        BIGINT user_id FK
        BIGINT item_id FK
        TEXT event_type
        NUMERIC rating
        NUMERIC event_value
        TEXT review_text
        TIMESTAMPTZ event_ts
        TEXT source
        JSONB raw_event
        TIMESTAMPTZ created_at
    }