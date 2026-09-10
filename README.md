# ShopWise Recommender

Production-oriented personalized recommendation engine built from real-world Amazon review data.

The project is designed to demonstrate an end-to-end recommendation system pipeline including data ingestion, validation, temporal evaluation, collaborative filtering, ranking, API serving, PostgreSQL, and deployment.

## Project Status

### Phase 1 — Data Engineering & Evaluation Setup

Status: **Complete**

Completed:

- [x] Project structure and environment
- [x] Raw dataset download
- [x] Data ingestion with Polars
- [x] Data cleaning and deduplication
- [x] PostgreSQL schema
- [x] PostgreSQL bulk loading
- [x] Data validation
- [x] Interaction filtering analysis
- [x] 2/2 k-core candidate filtering
- [x] Temporal 70/15/15 train/validation/test split
- [x] Automated validation tests
- [x] Phase 1 documentation

Upcoming:

- [ ] Train-only filtering / eligibility
- [ ] Baseline recommender
- [ ] Candidate generation
- [ ] Ranking model
- [ ] Offline evaluation
- [ ] FastAPI serving
- [ ] Dockerized inference
- [ ] Monitoring and deployment

---

## Dataset

This project uses the **Amazon Reviews 2023** dataset from McAuley Lab.

Source:

- Hugging Face: `McAuley-Lab/Amazon-Reviews-2023`
- Category used: `All_Beauty`

The dataset contains user reviews, ratings, timestamps, helpfulness information, and item metadata.

The original All_Beauty category contains approximately:

- 632K users
- 112.6K items
- 701.5K ratings

See [docs/data-card.md](docs/data-card.md) for the dataset details and limitations.

---

## Phase 1 Dataset Pipeline

```text
Raw Amazon Reviews
        |
        v
Parquet ingestion
        |
        v
Cleaning + normalization
        |
        v
Deduplication
        |
        v
PostgreSQL + processed Parquet
        |
        v
Validation
        |
        v
Filtering analysis
        |
        v
Temporal splitting
        |
        +---- Train
        +---- Validation
        +---- Test
