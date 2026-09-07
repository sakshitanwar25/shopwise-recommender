# Database Schema

## Overview

The ShopWise Recommender uses PostgreSQL as its application and
relational data store.

The database is normalized into four primary tables:

- `users`
- `categories`
- `items`
- `interaction_events`

The design separates source identifiers from internal identifiers
and preserves raw source information where useful for traceability.

---

## 1. users

### Purpose

Stores users who have interacted with products.

The internal `user_id` is used as the primary key, while
`source_user_id` preserves the original Amazon user identifier.

### Columns

| Column | Type | Constraints | Description |
|---|---|---|---|
| `user_id` | TEXT | PRIMARY KEY | Internal user identifier |
| `source_user_id` | TEXT | UNIQUE, NOT NULL | Original Amazon user ID |
| `created_at` | TIMESTAMPTZ | | User creation timestamp if known |
| `updated_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Last update timestamp |

---

## 2. categories

### Purpose

Stores product categories.

The initial Amazon Reviews dataset is category-specific, but the
schema supports multiple category paths for future expansion.

### Columns

| Column | Type | Constraints | Description |
|---|---|---|---|
| `category_id` | BIGSERIAL | PRIMARY KEY | Internal category identifier |
| `category_path` | TEXT | UNIQUE, NOT NULL | Category hierarchy/path |

---

## 3. items

### Purpose

Stores products and their metadata.

The internal `item_id` identifies an item inside ShopWise, while
`source_item_id` preserves the original Amazon product identifier.

### Columns

| Column | Type | Constraints | Description |
|---|---|---|---|
| `item_id` | TEXT | PRIMARY KEY | Internal item identifier |
| `source_item_id` | TEXT | UNIQUE, NOT NULL | Original Amazon item identifier |
| `title` | TEXT | | Product title |
| `description` | TEXT | | Product description |
| `brand` | TEXT | | Product brand |
| `category_id` | BIGINT | FOREIGN KEY | Product category |
| `price` | NUMERIC(12,2) | | Product price |
| `average_rating` | NUMERIC(3,2) | | Average product rating |
| `review_count` | INTEGER | | Number of reviews |
| `item_created_at` | TIMESTAMPTZ | | Product creation timestamp if available |
| `raw_metadata` | JSONB | | Original or additional product metadata |
| `updated_at` | TIMESTAMPTZ | NOT NULL, DEFAULT NOW() | Last update timestamp |

### Relationship

Each item belongs to zero or one category.

```text
categories 1 ───────── N items