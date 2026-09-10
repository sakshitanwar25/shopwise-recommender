# Temporal Split Report

## Split strategy

The interaction dataset is split chronologically using:

- Training: earliest 70%
- Validation: next 15%
- Test: final 15%

The split is based on `event_ts` and does not randomly shuffle
interactions.

This prevents future interactions from being used to train the
recommendation model.

## Overall dataset

- Total users: 631,986
- Total items: 112,565
- Total interactions: 694,252

## Split boundaries

| Split | Start | End |
|---|---|---|
| Train | 2000-11-01 04:24:18+00:00 | 2020-12-06 02:25:18.241000+00:00 |
| Validation | 2020-12-06 02:25:37.757000+00:00 | 2021-09-02 16:49:59.806000+00:00 |
| Test | 2021-09-02 16:54:37.825000+00:00 | 2023-09-09 00:39:36.666000+00:00 |

## Split statistics

| Split | Interactions | Users | % Users | Items | % Items |
|---|---:|---:|---:|---:|---:|
| Train | 485,976 | 448,899 | 71.03% | 78,488 | 69.73% |
| Validation | 104,138 | 97,964 | 15.50% | 32,029 | 28.45% |
| Test | 104,138 | 98,164 | 15.53% | 29,752 | 26.43% |

## Leakage checks

- `max(train.event_ts) <= min(validation.event_ts)`
- `max(validation.event_ts) <= min(test.event_ts)`
- No overlapping event timestamps between splits

All checks passed during split generation.

## Important modeling note

User and item eligibility for recommendation training should be
determined using the training period only. Future validation and test
interactions must not influence training-time filtering decisions.

