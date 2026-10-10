#!/usr/bin/env zsh
set -euo pipefail

echo "=================================================="
echo " Module 2: Out-of-Core ELT & dbt Warehouse Build  "
echo "=================================================="

# Activate workspace virtual environment
source "$HOME/de_workspace/.venv/bin/activate"

# Verify dbt-duckdb installation
if ! command -v dbt &> /dev/null; then
    echo "==> Installing missing dbt-duckdb package..."
    uv pip install dbt-duckdb
fi

echo "==> Step 1: Compiling and executing dbt transformations..."
dbt run --project-dir . --profiles-dir ~/.dbt

echo ""
echo "==> Step 2: Running automated data quality assertions..."
dbt test --project-dir . --profiles-dir ~/.dbt

echo ""
echo "==> Step 3: Inspecting final Star Schema table inside DuckDB..."
duckdb /Users/kyreesullivan/de_workspace/.data_scratch/analytics_lakehouse.duckdb -c "
    SELECT * FROM fct_github_activity LIMIT 10;
"

echo "=================================================="
echo "[SUCCESS] Dimensional Warehouse Transformation Built."
