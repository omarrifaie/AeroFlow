# AeroFlow — developer task runner.
#
# Quickstart:
#     make setup      # create .venv and install deps
#     make all        # ingest -> load -> dbt build (models + tests)
#     make dashboard  # run the Evidence dashboard (needs Node 18+)
#
# The pipeline steps are driven through the Python CLI so the working directory
# is handled consistently on every platform.

PYTHON ?= python
VENV := .venv
ROOT := $(CURDIR)

# venv interpreter differs between Windows and POSIX.
ifeq ($(OS),Windows_NT)
	VENV_PY := $(VENV)/Scripts/python.exe
else
	VENV_PY := $(VENV)/bin/python
endif

DBT := "$(ROOT)/$(VENV_PY)" -m dbt.cli.main

.DEFAULT_GOAL := help
.PHONY: help setup ingest load build test docs dashboard all lint clean

help: ## Show this help
	@echo "AeroFlow targets:"
	@echo "  setup      Create .venv and install Python deps (editable + dev extras)"
	@echo "  ingest     Download raw OpenFlights files into data/raw/"
	@echo "  load       Load raw files into DuckDB (schema raw)"
	@echo "  build      dbt deps + dbt build (models and tests)"
	@echo "  test       dbt test (data tests only)"
	@echo "  docs       Generate dbt docs (transform/target/)"
	@echo "  all        ingest -> load -> build"
	@echo "  lint       Run ruff + sqlfluff"
	@echo "  dashboard  Install + run the Evidence dashboard (Node 18+)"
	@echo "  clean      Remove build artifacts, data and the warehouse"

setup: ## Create venv and install dependencies
	$(PYTHON) -m venv $(VENV)
	$(VENV_PY) -m pip install --upgrade pip
	$(VENV_PY) -m pip install -e ".[dev]"

ingest: ## Download raw data
	$(VENV_PY) -m pipeline.cli ingest

load: ## Load raw data into DuckDB
	$(VENV_PY) -m pipeline.cli load

build: ## dbt deps + dbt build (models + tests)
	$(VENV_PY) -m pipeline.cli transform

all: ## Full pipeline: ingest -> load -> transform
	$(VENV_PY) -m pipeline.cli all

test: ## Run dbt data tests
	cd transform && $(DBT) test --profiles-dir .

docs: ## Generate dbt documentation
	cd transform && $(DBT) docs generate --profiles-dir .

lint: ## Lint Python (ruff) and SQL (sqlfluff)
	$(VENV_PY) -m ruff check .
	$(VENV_PY) -m ruff format --check .
	$(VENV_PY) -m sqlfluff lint transform/models transform/tests

dashboard: ## Install and run the Evidence dashboard (Node 18+)
	cd dashboard && npm install && npm run sources && npm run dev

clean: ## Remove generated artifacts
	rm -rf data \
		transform/target transform/dbt_packages transform/logs \
		transform/aeroflow.duckdb transform/aeroflow.duckdb.wal \
		dashboard/.evidence dashboard/build
