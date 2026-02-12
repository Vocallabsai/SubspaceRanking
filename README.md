
# Admin Lambda Ranking System

## Project Structure & Folders

- **(root folder)**: Contains main scripts for ranking, configuration, data fetching, output handling, and requirements.
- **ranking_experiments/**: Experimental scripts for alternative admin ranking formulas (e.g., normalization, weighting). Outputs CSV and Excel results for experiments.
- **ranking_min_calls/**: Experiments that rank only admins with a minimum(10) (or exact) number of recent calls. Outputs CSV and Excel results for these filtered rankings.


A comprehensive system for ranking admins based on performance metrics using a lambda formula.

## Formula
```
lambda = cr50 + 1/cdt50 + r50 + 1/lr1m
```

Where:
- **cr50**: Average internal_rating for last 50 calls
- **1/cdt50**: Inverse of average credentials_delivery_time for last 50 calls
- **r50**: Average chat rating for last 50 ratings

# Admin Ranking System: Quick Reference

## 1. main.py — What it did & Formula Used

Ranks all admins using the formula:

   lambda = cr50 + 1/cdt50 + r50 + 1/lr1m

Where:
- **cr50**: Average internal_rating for last 50 calls
- **cdt50**: Average credentials_delivery_time for last 50 calls (lower is better)
- **r50**: Average chat rating for last 50 ratings
- **lr1m**: Leave requests count in last month (lower is better)

Admins are sorted by lambda (higher is better). Output: CSV, Excel, JSON report.

## 2. ranking_experiments/experiment_ranking.py — What it did & Formula Used

Ranks admins using a normalized and weighted formula:

   exp_lambda = 2·cr50_norm + 2·r50_norm + 1·cdt50_norm + 1·lr1m_norm

Where each metric is normalized to [0,1]:
- cr50_norm = cr50/5
- r50_norm = r50/5
- cdt50_norm = min(60/avg_delivery_time, 1)
- lr1m_norm = 1/(leave_count+1)

Output: CSV and Excel with normalized columns.

## 3. Tables & Columns Used

- **whatsub_delivery_time**: `admin_id`, `admin_name`, `internal_rating`, `credentials_delivery_time`, `created_at`
- **whatsub_admin_ratings**: `user_id` (admin), `rating`, `created_at`
- **whatsub_room_user_mapping**: `user_id` (admin), `created_at`

## 4. Result Sample Data

### main.py output (CSV):

| rank | admin_name      | lambda_score | cr50 | cdt50_inverse | r50 | lr1m_inverse |
|------|----------------|--------------|------|---------------|-----|--------------|
| 1    | 🌷Ayansh🌷      | 12.500       | 5.0  | 1.5           | 5.0 | 1.0          |
| 2    | Pratap R       | 11.003       | 5.0  | 0.003         | 5.0 | 1.0          |
| ...  | ...            | ...          | ...  | ...           | ... | ...          |

### experiment_ranking.py output (CSV):

| admin_name      | exp_lambda_score | cr50 | cr50_norm | r50 | r50_norm | cdt50 | cdt50_norm | lr1m | lr1m_norm | rank |
|----------------|------------------|------|-----------|-----|----------|-------|------------|------|-----------|------|
| 🌷Ayansh🌷      | 6.0              | 5.0  | 1.0       | 5.0 | 1.0      | 0.67  | 1.0        | 0    | 1.0       | 1    |
| Gautam Kumar   | 5.94             | 4.86 | 0.97      | 5.0 | 1.0      | 19.0  | 1.0        | 0    | 1.0       | 2    |
| ...            | ...              | ...  | ...       | ... | ...      | ...   | ...        | ...  | ...       | ...  |

---