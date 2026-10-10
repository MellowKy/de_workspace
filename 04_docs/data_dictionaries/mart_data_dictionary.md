# Analytics Mart Data Dictionary & Data Contracts

## Model: `fct_github_activity`
- **Location:** `03_projects/02_elt_duckdb_dbt/models/marts/fct_github_activity.sql`
- **Storage Format:** DuckDB Table / Parquet S3 Export
- **Grain:** One row per event type per calendar date.

### Column Specifications
| Column Name | Data Type | Nullable | Primary Key | Description |
| :--- | :--- | :--- | :--- | :--- |
| `event_date` | DATE | No | Yes (Composite) | UTC Calendar date of event occurrence |
| `event_type` | VARCHAR | No | Yes (Composite) | Standardized event action classification |
| `unique_actors` | BIGINT | No | No | Count of distinct user handles performing actions |
| `total_events` | BIGINT | No | No | Total volume of events recorded in window |

### Data Quality Assertions
1. `not_null`: Enforced on `event_type` and `event_date`.
2. `unique`: Enforced on composite key `(event_date, event_type)`.
3. `positive_values`: `total_events` and `unique_actors` must be >= 1.
