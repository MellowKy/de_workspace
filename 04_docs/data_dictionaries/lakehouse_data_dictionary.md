# Enterprise Data Lakehouse Data Dictionary

## Table: `stg_github_events` (Staging View)
- **Source:** `.data_scratch/processed/parquet/*.parquet`
- **Granularity:** One record per ingested GitHub event.

| Column Name | Data Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `event_id` | BIGINT | PRIMARY KEY, NOT NULL | Unique 64-bit integer identifier for each GitHub event |
| `event_type` | VARCHAR | NOT NULL | Event classification string (e.g., `PushEvent`, `PullRequestEvent`) |
| `actor_username` | VARCHAR | NULLABLE | GitHub login handle of the user executing the action |
| `repository_name` | VARCHAR | NULLABLE | Target repository full name (`org/repo`) |
| `event_date` | DATE | NOT NULL | UTC date of event creation (`YYYY-MM-DD`) |
| `event_time` | VARCHAR | NOT NULL | UTC time string (`HH:MM:SS`) |

---

## Table: `fct_github_activity` (Fact Table Mart)
- **Source:** `stg_github_events`
- **Granularity:** One record per event type per calendar date.

| Column Name | Data Type | Constraint | Description |
| :--- | :--- | :--- | :--- |
| `event_date` | DATE | FOREIGN KEY | Dimension date binding key |
| `event_type` | VARCHAR | NOT NULL | Event classification string |
| `unique_actors` | BIGINT | NOT NULL | Distinct count of active user logins on given date |
| `total_events` | BIGINT | NOT NULL | Aggregate event volume count |
