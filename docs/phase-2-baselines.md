# Phase 2 — Popularity Baselines

## Objective

Establish a simple, non-personalized recommendation baseline that future
recommendation models must outperform.

The baseline uses interaction popularity with event-type weighting and
time decay.

---

## Methodology

The popularity score for an item is:

\[
score(i) = \sum_e w_{type}(e) \times e^{-\lambda \Delta t_e}
\]

where:

- \(w_{type}(e)\) is the weight assigned to the interaction type.
- \(\lambda\) is the time-decay rate.
- \(\Delta t_e\) is the age of the interaction in days.
- The reference time is the latest interaction timestamp in the training data.

### Interaction weights

| Interaction | Weight |
|---|---:|
| View | 1 |
| Like / Save | 3 |
| Cart | 5 |
| Purchase | 8 |
| Review with rating >= 4 | 8 |
| Review with rating < 4 | 0 |

The current dataset primarily contains review interactions, so the review
rating determines whether an interaction contributes positively to popularity.

The baseline uses:

```text
decay_rate = 0.001