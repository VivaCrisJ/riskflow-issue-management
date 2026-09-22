# RiskFlow

[![CI](https://github.com/VivaCrisJ/riskflow-issue-management/actions/workflows/ci.yml/badge.svg)](https://github.com/VivaCrisJ/riskflow-issue-management/actions/workflows/ci.yml)

RiskFlow is an interactive portfolio prototype exploring how structured data,
workflow automation and human-reviewed thematic analysis can support the
issue-management lifecycle in financial services.

The project uses entirely synthetic data and contains no client, employer or
personal information.

## Current build

- Executive risk and controls overview
- Transparent priority scoring
- Priority review queue and issue-level score explanation
- Searchable Issue Register with composable filters, CSV export and drill-down
- Independent Closure Review with evidence gates and a demonstration audit trail
- Cross-business thematic analysis and explainable assisted classification
- Deterministic synthetic dataset with automated validation

The core MVP modules are implemented and the repository is configured for
Streamlit Community Cloud deployment and GitHub Actions validation.

## Assisted classification

The first version uses transparent keyword and business rules to demonstrate
how AI-assisted issue classification could support risk triage. It exposes the
matched terms and suggested investigation areas, and explicitly requires human
review. It does not claim to be an autonomous risk decision system.

## Run locally

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

## Validate the data and analytics

```bash
python scripts/validate_synthetic_data.py
pytest
```

## Deploy on Streamlit Community Cloud

No API keys or application secrets are required for this synthetic-data MVP.

1. Sign in to [Streamlit Community Cloud](https://share.streamlit.io/) with the
   GitHub account that owns this repository.
2. Choose **Create app** and select **Deploy a public app from GitHub**.
3. Use these settings:
   - Repository: `VivaCrisJ/riskflow-issue-management`
   - Branch: `main`
   - Main file path: `app.py`
4. Choose an available app URL and select **Deploy**.

The checked-in `.streamlit/config.toml` supplies the presentation theme, while
`requirements.txt` supplies the runtime dependencies.
