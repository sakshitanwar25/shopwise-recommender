CREATE TABLE IF NOT EXISTS categories (
    category_id BIGSERIAL PRIMARY KEY,
    category_path TEXT UNIQUE NOT NULL
);


CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    source_user_id TEXT UNIQUE NOT NULL,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


CREATE TABLE IF NOT EXISTS items (
    item_id TEXT PRIMARY KEY,
    source_item_id TEXT UNIQUE NOT NULL,
    title TEXT,
    description TEXT,
    brand TEXT,
    category_id BIGINT REFERENCES categories(category_id),
    price NUMERIC(12, 2),
    average_rating NUMERIC(3, 2),
    review_count INTEGER,
    item_created_at TIMESTAMPTZ,
    raw_metadata JSONB,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);


CREATE TABLE IF NOT EXISTS interaction_events (
    event_id BIGSERIAL PRIMARY KEY,

    user_id TEXT NOT NULL
        REFERENCES users(user_id),

    item_id TEXT NOT NULL
        REFERENCES items(item_id),

    event_type TEXT NOT NULL,

    rating NUMERIC(2, 1),

    event_value NUMERIC,

    review_text TEXT,

    event_ts TIMESTAMPTZ NOT NULL,

    source TEXT NOT NULL DEFAULT 'amazon_reviews_2023',

    raw_event JSONB,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT valid_event_type
        CHECK (
            event_type IN (
                'review',
                'rating',
                'view',
                'cart',
                'purchase',
                'like'
            )
        )
);