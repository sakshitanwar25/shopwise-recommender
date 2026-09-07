# Entity Relationship Diagram

## ShopWise Recommender Database

```mermaid
erDiagram

    CATEGORIES ||--o{ ITEMS : contains

    USERS ||--o{ INTERACTION_EVENTS : creates

    ITEMS ||--o{ INTERACTION_EVENTS : receives


    CATEGORIES {
        BIGINT category_id PK
        TEXT category_path UK
    }

    USERS {
        TEXT user_id PK
        TEXT source_user_id UK
        TIMESTAMPTZ created_at
        TIMESTAMPTZ updated_at
    }

    ITEMS {
        TEXT item_id PK
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

    INTERACTION_EVENTS {
        BIGINT event_id PK
        TEXT user_id FK
        TEXT item_id FK
        TEXT event_type
        NUMERIC rating
        NUMERIC event_value
        TEXT review_text
        TIMESTAMPTZ event_ts
        TEXT source
        JSONB raw_event
        TIMESTAMPTZ created_at
    }