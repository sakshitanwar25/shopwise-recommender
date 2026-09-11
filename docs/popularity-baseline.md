# Popularity Baseline

## Purpose

The popularity recommender establishes a simple non-personalized benchmark
against which personalized recommendation models can be compared.

Popularity is calculated using training interactions only.

## Validation Results

| Metric | Score |
|---|---:|
| Users evaluated | 6,181 |
| Precision@10 | 0.000841 |
| Recall@10 | 0.007981 |
| NDCG@10 | 0.003638 |
| MAP@10 | 0.002307 |
| MRR | 0.002497 |
| HitRate@10 | 0.008413 |

## Interpretation

The popularity baseline achieves limited recommendation quality.

The low Recall@10 and HitRate@10 indicate that globally popular items
cover only a small fraction of users' future interactions.

This provides a useful benchmark for evaluating personalized models.

## Important Evaluation Note

The current evaluator only evaluates users with at least one training
interaction. Users without training history are excluded from this
warm-start evaluation and should be reported separately in future
evaluation improvements.