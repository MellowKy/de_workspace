import pathlib
import subprocess
import sys

def run_step(name, command):
    print(f"==> [CHECK] Verifying {name}...")
    try:
        subprocess.run(command, shell=True, check=True, capture_output=True, text=True)  # nosec B602
        print(f"[OK] {name} Passed.")
    except subprocess.CalledProcessError as e:
        print(f"[FAIL] {name} Failed!\nError Output:\n{e.stderr}")
        sys.exit(1)

def verify_docs():
    print("==> [CHECK] Verifying Enterprise Governance Documentation...")
    required_docs = [
        "01_research/adrs/ADR-001-polars-vs-pyspark-stream-ingestion.md",
        "01_research/adrs/ADR-002-duckdb-dbt-vs-snowflake-warehouse.md",
        "01_research/adrs/ADR-003-dagster-sda-vs-airflow-dag.md",
        "04_docs/architecture_diagrams/system_architecture.md",
        "04_docs/architecture_diagrams/epdp_architecture.png",
        "04_docs/data_dictionaries/lakehouse_data_dictionary.md",
        "04_docs/data_dictionaries/mart_data_dictionary.md",
        "04_docs/runbooks/incident_response_playbook.md",
        "04_docs/runbooks/disaster_recovery_runbook.md",
        "ARCHITECTURE.md",
        "README.md",
    ]
    for doc in required_docs:
        if not pathlib.Path(doc).exists():
            print(f"[FAIL] Missing Documentation Asset: {doc}")
            sys.exit(1)
    print("[OK] All Architecture, Dictionary, and Runbook Artifacts Verified.")

def main():
    print("==================================================")
    print(" EPDP Monorepo Platform Health Check Verification ")
    print("==================================================")

    verify_docs()
    run_step("Bandit SAST Security Scan", "uv run bandit -r 03_projects/ scripts/ -ll -ii")
    run_step("Python & SQL Quality Gates", "uv run --no-project ruff check .")
    run_step("Real-Time Polars Lakehouse", "uv run --no-project python3 03_projects/05_realtime_lakehouse/realtime_lakehouse.py")
    run_step("dbt Dimensional Modeling", "cd 03_projects/02_elt_duckdb_dbt && uv run --no-project dbt run --profiles-dir ~/.dbt")
    run_step("dbt Data Assertions", "cd 03_projects/02_elt_duckdb_dbt && uv run --no-project dbt test --profiles-dir ~/.dbt")
    run_step("Dagster SDA & Qdrant Catalog", "uv run --no-project dagster asset materialize --select '*' -f 03_projects/06_dagster_orchestration/repository.py")
    run_step("Terraform Infrastructure Code", "cd 03_projects/03_devops_terraform_cicd && terraform validate")
    run_step("AI Vector Catalog Search", "uv run --no-project python3 scripts/ai_catalog_query.py --query 'user`activity'")

    print("==================================================")
    print("[SUCCESS] All Monorepo Security & Pipeline Gates Validated!")

if __name__ == "__main__":
    main()
