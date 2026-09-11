# Phase 2 Readiness

## Status

**Ready to begin Phase 2**

Phase 1 established the data engineering and evaluation foundation for the
recommendation system.

---

## 1. Dataset Splits

The cleaned interaction dataset was split chronologically into training,
validation, and test periods.

| Split | Interactions |
|---|---:|
| Train | 485,976 |
| Validation | 104,138 |
| Test | 104,138 |
| **Total** | **694,252** |

### Date ranges

| Split | Start | End |
|---|---|---|
| Train | 2000-11-01 04:24:18 UTC | 2020-12-06 02:25:18.241 UTC |
| Validation | 2020-12-06 02:25:37.757 UTC | 2021-09-02 16:49:59.806 UTC |
| Test | 2021-09-02 16:54:37.825 UTC | 2023-09-09 00:39:36.666 UTC |

The split is chronological rather than random so that future interactions are
not used to train the recommendation models.

---

## 2. PostgreSQL Readiness

The PostgreSQL database contains the following core tables:

- `users`
- `items`
- `categories`
- `interaction_events`

The database also contains indexes supporting common user-history,
item-history, and category queries.

---

## 3. Data Loading

The train, validation, and test interaction datasets can be loaded using
Polars.

The processed user and item datasets can also be joined with the interaction
datasets using:

```text
user_id
item_id