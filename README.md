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
- Deterministic synthetic dataset with automated validation

Additional approved modules are under active development: Issue Register,
Closure Review and Thematic Analysis.

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

