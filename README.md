# Glovo Lakehouse on Azure Databricks

End-to-end data engineering project for a food-delivery platform: batch files, streaming
order events and REST APIs land in a Unity Catalog lakehouse on Azure Databricks, flow
through a Bronze → Silver → Gold (Medallion) architecture, and serve Power BI, an ML
delivery-time model and a GenAI layer. Infrastructure and deployments are fully automated.

> **Status:** 🚧 Phase 0 — data profiling. This README grows with the project.

## Architecture (target)

| Layer | What happens | Tools |
| --- | --- | --- |
| Ingestion | Daily files, order events, weather + holiday APIs | Azure Data Factory, Event Hubs (Kafka), Auto Loader |
| Bronze | Raw data as received, plus audit columns | Delta Lake, Structured Streaming |
| Silver | Typed, cleaned, deduplicated, validated; bad rows quarantined | Lakeflow Declarative Pipelines (DLT), expectations, SCD Type 2 |
| Gold | Star schema + business marts | Spark SQL, Unity Catalog |
| Serving | Reports, ETA model, LLM classification, Genie | Power BI, MLflow, `ai_query()` |
| Platform | Infrastructure, CI/CD, governance, cost | Terraform, Databricks Asset Bundles, GitHub Actions, Azure DevOps |

## Dataset

Synthetic Glovo Poland data: 10 tables, ~300k rows, 36 Polish cities, 2023–2024, PLN.
Data-quality problems are intentional (mixed timestamp formats, comma decimals,
duplicates, orphan foreign keys, outliers). See [`docs/data_dictionary.md`](docs/data_dictionary.md).

The source system delivers the data as **10 Parquet files**. The data is **not stored in Git**:
download `glovo_parquet.zip` from the [Releases](../../releases) page and unzip it into
`data/landing/`.

## Business questions

1. What drives late deliveries: distance, hour, city, restaurant or courier?
2. How does the cancellation rate vary by city, hour and cuisine?
3. Which restaurants are slowest and lowest rated, and does rating follow delivery time?
4. How do payment methods and order values differ across cities and city tiers?
5. Where is courier supply short of peak-hour demand?

## Repository layout

```text
.github/workflows/   CI (lint + unit tests on every pull request)
infra/terraform/     Azure + Unity Catalog infrastructure as code
adf/                 Azure Data Factory pipelines (exported JSON)
resources/           Databricks Asset Bundle jobs and pipelines
src/glovo/           Python package: bronze, silver, gold, ml, genai, utils
notebooks/           Thin notebooks that call src/ (profiling, demos)
tools/               Helper scripts (event producer)
sql/analytics/       Business SQL queries
tests/               Unit and integration tests
powerbi/             Report files and screenshots
docs/                Data dictionary, decision records (ADRs), cost report
```

## Quick start (local)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pre-commit install
pytest
```

## Roadmap

- [ ] Phase 0 — Data profiling and data dictionary
- [ ] Phase 1 — Infrastructure as code (Terraform) + CI
- [ ] Phase 2 — Bronze ingestion (ADF + Auto Loader + APIs)
- [ ] Phase 3 — Silver pipeline with data-quality rules
- [ ] Phase 4 — Gold star schema, orchestration, Power BI
- [ ] Phase 5 — Streaming order events
- [ ] Phase 6 — Governance, monitoring, performance, FinOps
- [ ] Phase 7 — Full CI/CD with Azure DevOps
- [ ] Phase 8 — ML (MLflow) and GenAI
- [ ] Phase 9 — Documentation and demo video

## Decisions

Architecture decision records live in [`docs/adr/`](docs/adr/).
