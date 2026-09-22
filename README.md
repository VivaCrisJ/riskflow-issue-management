# RiskFlow

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

The core MVP modules are implemented. Deployment and interview packaging are in
progress.

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
