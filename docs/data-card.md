# Data Card — Amazon Reviews 2023

## 1. Dataset Overview

This project uses the **Amazon Reviews 2023** dataset released by the McAuley Lab.

Source:

- Dataset: Amazon Reviews 2023
- Organization: McAuley Lab
- Category used: `All_Beauty`
- Data type: User-product review interactions
- Time span: May 1996 – September 2023

The dataset contains user reviews, ratings, timestamps, product identifiers,
review metadata, and helpfulness information.

The project uses the `All_Beauty` category because it provides a realistic
recommendation setting while keeping the dataset manageable for local
development and experimentation.

---

## 2. Dataset Scale

The complete Amazon Reviews 2023 dataset contains approximately:

| Metric | Count |
|---|---:|
| Reviews | 571.54M |
| Users | 54.51M |
| Items | 48.19M |

For this project, only the `All_Beauty` category is used.

Approximate source-category statistics:

| Metric | Count |
|---|---:|
| Users | 632K |
| Items | 112.6K |
| Ratings | 701.5K |

The locally downloaded raw `All_Beauty` review file contains:

| Metric | Count |
|---|---:|
| Raw rows | 701,528 |
| Unique users | 631,986 |
| Unique ASINs | 115,709 |
| Unique parent ASINs | 112,565 |

---

## 3. Raw Data Fields

The original review data contains the following fields:

| Field | Description |
|---|---|
| `rating` | Explicit rating from 1 to 5 |
| `title` | Review title |
| `text` | Review text |
| `images` | Images associated with the review |
| `asin` | Amazon item identifier |
| `parent_asin` | Parent product identifier |
| `user_id` | Source user identifier |
| `timestamp` | Review timestamp in Unix milliseconds |
| `helpful_vote` | Number of helpful votes |
| `verified_purchase` | Whether the review was associated with a verified purchase |

---

## 4. Identifier Strategy

The original Amazon identifiers are preserved as source identifiers.

The project also creates deterministic internal identifiers for users and
items using a SHA-256 based mapping.

This provides:

- Stable identifiers across pipeline runs
- Database-friendly integer IDs
- Separation between source identifiers and internal identifiers
- Reproducible joins between users, items, and interactions

The project uses `parent_asin` as the item-level identifier for recommendation
interactions because it represents the parent product rather than an individual
variant.

---

## 5. Data Processing Pipeline

The raw dataset goes through the following processing stages:

```text
Raw Parquet
    |
    v
Column selection
    |
    v
Timestamp normalization
    |
    v
Data validation
    |
    v
Deduplication
    |
    v
Stable user/item IDs
    |
    v
Processed Parquet
    |
    +---- PostgreSQL
    |
    +---- Temporal train/validation/test splits