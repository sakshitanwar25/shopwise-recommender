# Phase 1 — Exploratory Data Analysis Summary

## Dataset

- Dataset: Amazon Reviews 2023
- Source: McAuley-Lab/Amazon-Reviews-2023
- Category: All_Beauty
- Dataset revision:
  `749931181c9cdd70bfa6408d8fe8b4ddd6107248`
- Full review count: 701,528
- Exploration sample: 10,000 reviews

## Schema

| Column | Type | Description |
|---|---|---|
| `rating` | Float64 | User rating from 1–5 |
| `title` | String | Review title |
| `text` | String | Review text |
| `images` | List[Struct] | Images associated with review |
| `asin` | String | Amazon product identifier |
| `parent_asin` | String | Parent product identifier |
| `user_id` | String | User identifier |
| `timestamp` | Int64 | Review timestamp in milliseconds |
| `helpful_vote` | Int64 | Number of helpful votes |
| `verified_purchase` | Boolean | Whether purchase was verified |

## Missing Values

The 10,000-row exploration sample contained no null values in any of the observed columns.

This result applies only to the sample. The full dataset will be validated separately during the cleaning stage.

## Interaction Statistics

Fill in the following values from the notebook:

- Unique users: **TODO**
- Unique ASINs: **TODO**
- Unique parent ASINs: **TODO**
- Total interactions in sample: **10,000**
- Average interactions per user: **TODO**
- Median interactions per user: **TODO**
- Maximum interactions per user: **TODO**
- Average interactions per item: **TODO**
- Median interactions per item: **TODO**
- Maximum interactions per item: **TODO**

## Rating Distribution

| Rating | Reviews | Percentage |
|---:|---:|---:|
| 1 | TODO | TODO |
| 2 | TODO | TODO |
| 3 | TODO | TODO |
| 4 | TODO | TODO |
| 5 | TODO | TODO |

The rating distribution was visualized in the exploration notebook.

## Time Range

- Earliest interaction: **TODO**
- Latest interaction: **TODO**

Timestamps are stored as Unix epoch milliseconds and were converted to UTC datetime values for analysis.

## Data Quality Checks

### Exact duplicate rows

- Exact duplicate rows: **TODO**

### Repeated user-item pairs

- User-item pairs with multiple reviews: **TODO**

Repeated user-item interactions were measured but not removed during EDA. Deduplication rules will be defined during the cleaning stage based on the dataset's actual interaction identifiers.

### Rating validation

- Invalid ratings outside the `[1, 5]` range: **TODO**

Invalid ratings, if present, will be dropped or quarantined during cleaning rather than clipped.

## Sparsity

- Users: **TODO**
- Items: **TODO**
- Observed interactions: **10,000**
- User-item matrix sparsity: **TODO**

The dataset is expected to be highly sparse, which is typical for recommendation systems.

## Initial Observations

1. The dataset contains explicit ratings that can be used as a preference signal.
2. `user_id`, `asin`, `rating`, and `timestamp` provide the core information required for collaborative recommendation.
3. Review text and metadata can potentially support content-based recommendation and cold-start strategies.
4. The timestamp enables chronological train/validation/test splitting.
5. The full dataset must be validated before final filtering and modeling decisions are made.
6. Minimum user/item interaction thresholds should be selected using the full dataset distribution rather than the 10,000-row sample alone.

## Next Steps

1. Download/use the full All_Beauty dataset.
2. Validate the complete dataset.
3. Apply reproducible cleaning rules.
4. Create internal surrogate user/item/category IDs while preserving source IDs.
5. Create chronological train/validation/test splits.
6. Store curated data in Parquet.
7. Load the curated interaction data into PostgreSQL.