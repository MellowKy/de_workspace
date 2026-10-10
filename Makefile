.PHONY: help env-up lint clean-scratch

help:
	@echo "Data Engineering Workspace Commands:"
	@echo "  make env-up        - Activate Python environment via uv"
	@echo "  make lint          - Run SQL and Python linters"
	@echo "  make clean-scratch - Purge local data scratch space"

env-up:
	@source .venv/bin/activate

lint:
	uv run sqlfluff lint 03_projects/
	uv run ruff check .

clean-scratch:
	rm -rf .data_scratch/raw/* .data_scratch/processed/*
	@echo "[CLEARED] Local data scratch directory wiped."
