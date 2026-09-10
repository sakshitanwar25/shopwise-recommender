# Phase 1 — Exploratory Data Analysis Summary

## 1. Objective

The objective of Phase 1 EDA was to understand the structure, quality,
distribution, sparsity, and temporal characteristics of the Amazon
`All_Beauty` interaction dataset before building recommendation models.

The analysis focused on:

- Dataset scale
- User activity
- Item activity
- Rating distribution
- Duplicate interactions
- User-item sparsity
- Long-tail behavior
- Filtering sensitivity
- Temporal structure

---

# 2. Dataset Size

The raw dataset contains:

| Metric | Count |
|---|---:|
| Raw interaction rows | 701,528 |
| Unique users | 631,986 |
| Unique ASINs | 115,709 |
| Unique parent ASINs | 112,565 |

The distinction between ASIN and `parent_asin` is important.

Multiple ASINs can represent variants of the same parent product, so the
recommendation pipeline uses `parent_asin` as the item-level identifier.

---

# 3. Data Quality

The raw dataset was validated before modeling.

### Null values

No null values were found in the required raw fields used by the pipeline.

### Rating range

All ratings fall within the expected range:

```text
1.0 <= rating <= 5.0