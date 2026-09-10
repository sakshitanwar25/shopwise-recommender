# ShopWise Recommender

Production-oriented personalized recommendation engine built from real-world Amazon review data.

The project demonstrates an end-to-end recommendation system workflow covering data engineering, validation, temporal evaluation, recommendation baselines, candidate generation, ranking, API serving, and deployment.

---

## Project Status

### Phase 1 — Data Engineering & Evaluation Setup

**Status: Complete**

Completed:

- [x] Project structure and environment
- [x] Raw dataset download
- [x] Data ingestion with Polars
- [x] Data cleaning and deduplication
- [x] PostgreSQL schema
- [x] PostgreSQL bulk loading
- [x] Data validation
- [x] Interaction filtering analysis
- [x] 2/2 k-core candidate filtering analysis
- [x] Temporal 70/15/15 train/validation/test split
- [x] Automated validation tests
- [x] Phase 1 documentation

Upcoming:

- [ ] Train-only filtering / eligibility
- [ ] Popularity baseline
- [ ] Collaborative filtering baseline
- [ ] Candidate generation
- [ ] Ranking model
- [ ] Offline Top-K evaluation
- [ ] FastAPI serving
- [ ] Dockerized inference
- [ ] Monitoring and deployment

---

## Dataset

This project uses the **Amazon Reviews 2023** dataset from McAuley Lab.

**Category:** `All_Beauty`

The dataset contains user reviews, ratings, timestamps, helpfulness information, user identifiers, product identifiers, and review metadata.

The original dataset spans May 1996 to September 2023.

See [`docs/data-card.md`](docs/data-card.md) for dataset details, processing decisions, and limitations.

---

## Recommendation Objective

The goal is **personalized Top-K recommendation**, not simply rating prediction.

Given a user's historical interactions, the system will:

1. Generate candidate products.
2. Rank the candidates according to the user's preferences.
3. Return the Top-K products most likely to be relevant to the user.

The system will eventually evaluate:

- Candidate retrieval quality
- Ranking quality
- Precision@K
- Recall@K
- NDCG@K
- Popularity bias
- Cold-start behavior
- Inference latency
- Serving reliability

---

## Phase 1 Pipeline

```text
                Amazon Reviews
                       |
                       v
                Raw Parquet Data
                       |
                       v
              Ingestion + Cleaning
                       |
                       v
                Deduplication
                       |
                       v
             Stable User/Item IDs
                       |
              +--------+--------+
              |                 |
              v                 v
      Processed Parquet     PostgreSQL
              |                 |
              +--------+--------+
                       |
                       v
                 Data Validation
                       |
                       v
              Filtering Analysis
                       |
                       v
             Temporal Splitting
                       |
              +--------+--------+
              |        |        |
              v        v        v
            Train  Validation  Test