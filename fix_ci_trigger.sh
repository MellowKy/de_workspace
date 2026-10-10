#!/usr/bin/env zsh
set -euo pipefail

echo "=================================================="
echo " Fixing & Triggering GitHub Actions CI/CD Pipeline "
echo "=================================================="

# Ensure directory tree exists
mkdir -p .github/workflows

# Write GitHub Actions Workflow Configuration
cat << 'WORKFLOW' > .github/workflows/data_pipeline_ci.yml
name: Data Engineering CI/CD Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  code-quality-and-warehouse:
    name: Code Quality & Warehouse Validation
    runs-on: ubuntu-latest

    steps:
      - name: Checkout Source Code
        uses: actions/checkout@v4

      - name: Install uv & Set Up Python 3.12
        uses: astral-sh/setup-uv@v3
        with:
          version: "latest"
          enable-cache: true

      - name: Install Python Toolchain
        run: |
          uv venv .venv
          source .venv/bin/activate
          uv pip install sqlfluff ruff dbt-duckdb polars pyarrow qdrant-client requests

      - name: Run Ruff Python Linter
        run: |
          source .venv/bin/activate
          ruff check .

      - name: Run SQLFluff Quality Checks
        run: |
          source .venv/bin/activate
          sqlfluff lint 03_projects/02_elt_duckdb_dbt/models/ --dialect duckdb

      - name: Configure Transient dbt Profile & Build Models
        run: |
          source .venv/bin/activate
          mkdir -p ~/.dbt
          cat << 'PROFILE' > ~/.dbt/profiles.yml
          analytics_warehouse:
            target: dev
            outputs:
              dev:
                type: duckdb
                path: "/tmp/analytics_lakehouse.duckdb"
                threads: 4
          PROFILE
          
          python3 03_projects/05_realtime_lakehouse/realtime_lakehouse.py
          
          cd 03_projects/02_elt_duckdb_dbt
          dbt run --profiles-dir ~/.dbt
          dbt test --profiles-dir ~/.dbt

  terraform-infrastructure:
    name: Validate Infrastructure as Code
    runs-on: ubuntu-latest
    needs: code-quality-and-warehouse

    steps:
      - name: Checkout Source Code
        uses: actions/checkout@v4

      - name: Setup Terraform CLI
        uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: "1.6.0"

      - name: Terraform Format Check
        run: terraform fmt -check -recursive

      - name: Initialize & Validate Terraform Code
        run: |
          cd 03_projects/03_devops_terraform_cicd
          terraform init -backend=false
          terraform validate
WORKFLOW

echo "==> Force-staging .github/workflows/data_pipeline_ci.yml into Git tracking..."
git add -f .github/workflows/data_pipeline_ci.yml
git add .

if git diff-index --quiet HEAD --; then
    echo "[INFO] Working tree is clean. Making empty commit to trigger CI..."
    git commit --allow-empty -m "ci: trigger GitHub Actions pipeline build"
else
    git commit -m "ci: add GitHub Actions workflow manifest"
fi

echo "==> Pushing commits to GitHub..."
git push origin main

echo "=================================================="
echo "[SUCCESS] Workflow committed and pushed."
