import subprocess
import sys


def run_step(name, command):
    print(f"==> [CHECK] Verifying {name}...")
    try:
        subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"[OK] {name} Passed.")
    except subprocess.CalledProcessError as e:
        print(f"[FAIL] {name} Failed!\nError Output:\n{e.stderr}")
        sys.exit(1)


def main():
    print("==================================================")
    print(" EPDP Monorepo Platform Health Check Verification ")
    print("==================================================")

    run_step("Python & SQL Quality Gates", "uv run --no-project ruff check .")
    run_step(
        "Real-Time Polars Lakehouse",
        "uv run --no-project python3 03_projects/05_realtime_lakehouse/realtime_lakehouse.py",
    )
    run_step(
        "dbt Dimensional Modeling",
        "cd 03_projects/02_elt_duckdb_dbt && uv run --no-project dbt run --profiles-dir ~/.dbt",
    )
    run_step(
        "dbt Data Assertions",
        "cd 03_projects/02_elt_duckdb_dbt && uv run --no-project dbt test --profiles-dir ~/.dbt",
    )
    run_step(
        "Dagster SDA & Qdrant Catalog",
        "uv run --no-project dagster asset materialize --select '*' -f 03_projects/06_dagster_orchestration/repository.py",
    )
    run_step(
        "Terraform Infrastructure Code",
        "cd 03_projects/03_devops_terraform_cicd && terraform validate",
    )
    run_step(
        "AI Vector Catalog Search",
        "uv run --no-project python3 scripts/ai_catalog_query.py --query 'user activity'",
    )

    print("==================================================")
    print("[SUCCESS] All Monorepo Modules Operational & Validated!")


if __name__ == "__main__":
    main()
