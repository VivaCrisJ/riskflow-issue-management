"""Transparent business rules and management information for RiskFlow."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


REPORTING_DATE = pd.Timestamp("2026-09-30")

DATE_COLUMNS = [
    "date_identified",
    "original_target_date",
    "current_target_date",
    "last_update_date",
    "closure_review_date",
    "date_closed",
]

SEVERITY_POINTS = {"Critical": 40, "High": 28, "Medium": 16, "Low": 6}


def load_issues(path: str | Path) -> pd.DataFrame:
    """Load source records while preserving blanks and normalising data types."""
    frame = pd.read_csv(path)
    for column in DATE_COLUMNS:
        frame[column] = pd.to_datetime(frame[column], errors="coerce")
    frame["repeat_issue"] = frame["repeat_issue"].astype(str).str.lower().eq("true")
    frame["extension_count"] = pd.to_numeric(frame["extension_count"], errors="coerce").fillna(0).astype(int)
    frame["evidence_rejection_count"] = pd.to_numeric(
        frame["evidence_rejection_count"], errors="coerce"
    ).fillna(0).astype(int)
    frame["financial_impact_gbp"] = pd.to_numeric(
        frame["financial_impact_gbp"], errors="coerce"
    )
    return frame


def _days_overdue(row: pd.Series, reporting_date: pd.Timestamp) -> int:
    target = row["current_target_date"]
    if pd.isna(target) or row["status"] == "Closed" or target >= reporting_date:
        return 0
    return int((reporting_date - target).days)


def priority_factors(row: pd.Series) -> list[tuple[str, int]]:
    """Return the explainable components of one issue's priority score."""
    factors: list[tuple[str, int]] = [
        (f"{row['severity']} severity", SEVERITY_POINTS[str(row["severity"])])
    ]
    days_overdue = int(row["days_overdue"])
    if days_overdue > 60:
        factors.append(("More than 60 days overdue", 18))
    elif days_overdue > 30:
        factors.append(("31–60 days overdue", 14))
    elif days_overdue > 0:
        factors.append(("1–30 days overdue", 8))

    if row["customer_impact"] == "Actual":
        factors.append(("Actual customer impact", 10))
    elif row["customer_impact"] == "Potential":
        factors.append(("Potential customer impact", 4))

    if row["regulatory_impact"] == "Actual":
        factors.append(("Actual regulatory impact", 12))
    elif row["regulatory_impact"] == "Potential":
        factors.append(("Potential regulatory impact", 5))

    if bool(row["repeat_issue"]):
        factors.append(("Repeat issue", 6))

    extensions = int(row["extension_count"])
    if extensions >= 2:
        factors.append(("Two or more target extensions", 7))
    elif extensions == 1:
        factors.append(("One target extension", 3))

    if row["status"] == "Reopened":
        factors.append(("Reopened after prior closure", 8))
    elif row["status"] == "Further Evidence Required":
        factors.append(("Further closure evidence required", 6))
    elif row["status"] == "Awaiting Closure Review":
        factors.append(("Awaiting independent closure review", 4))

    rejected = min(int(row["evidence_rejection_count"]), 2)
    if rejected:
        factors.append((f"Closure evidence returned {rejected} time(s)", rejected * 4))
    return factors


def _priority_score(row: pd.Series) -> int:
    return min(100, sum(points for _, points in priority_factors(row)))


def _priority_band(row: pd.Series) -> str:
    if row["severity"] == "Critical":
        return "Immediate"
    if row["severity"] == "High" and int(row["days_overdue"]) > 30:
        return "Immediate"
    score = int(row["priority_score"])
    if score >= 75:
        return "Immediate"
    if score >= 55:
        return "High"
    if score >= 30:
        return "Standard"
    return "Monitor"


def enrich_issues(
    frame: pd.DataFrame, reporting_date: pd.Timestamp = REPORTING_DATE
) -> pd.DataFrame:
    """Add transparent, reproducible management-information fields."""
    result = frame.copy()
    end_dates = result["date_closed"].fillna(reporting_date)
    result["days_open"] = (end_dates - result["date_identified"]).dt.days.clip(lower=0)
    result["days_overdue"] = result.apply(
        lambda row: _days_overdue(row, reporting_date), axis=1
    )
    result["overdue_flag"] = result["days_overdue"].gt(0)

    severity_trigger = result["severity"].eq("Critical")
    high_overdue_trigger = result["severity"].eq("High") & result["days_overdue"].gt(30)
    extension_trigger = (
        result["severity"].isin(["Critical", "High"])
        & result["extension_count"].ge(2)
        & result["status"].ne("Closed")
    )
    impact_trigger = (
        result["severity"].isin(["Critical", "High"])
        & (
            result["customer_impact"].eq("Actual")
            | result["regulatory_impact"].eq("Actual")
        )
    )
    evidence_trigger = result["evidence_rejection_count"].ge(2)
    result["escalation_required"] = (
        severity_trigger
        | high_overdue_trigger
        | extension_trigger
        | impact_trigger
        | evidence_trigger
    ) & result["status"].ne("Closed")

    result["priority_score"] = result.apply(_priority_score, axis=1)
    result["priority_band"] = result.apply(_priority_band, axis=1)
    result["issue_age_band"] = pd.cut(
        result["days_open"],
        bins=[-1, 30, 60, 90, float("inf")],
        labels=["0–30 days", "31–60 days", "61–90 days", "90+ days"],
    )
    return result


def summary_metrics(frame: pd.DataFrame) -> dict[str, int]:
    open_mask = frame["status"].ne("Closed")
    return {
        "Open issues": int(open_mask.sum()),
        "Open high & critical": int(
            (open_mask & frame["severity"].isin(["Critical", "High"])).sum()
        ),
        "Overdue": int((open_mask & frame["overdue_flag"]).sum()),
        "Awaiting closure": int(frame["status"].eq("Awaiting Closure Review").sum()),
        "Escalation required": int((open_mask & frame["escalation_required"]).sum()),
    }


def priority_queue(frame: pd.DataFrame, limit: int = 8) -> pd.DataFrame:
    rank = {"Immediate": 0, "High": 1, "Standard": 2, "Monitor": 3}
    open_issues = frame.loc[frame["status"].ne("Closed")].copy()
    open_issues["_band_rank"] = open_issues["priority_band"].map(rank)
    return (
        open_issues.sort_values(
            ["_band_rank", "priority_score", "days_overdue"],
            ascending=[True, False, False],
        )
        .head(limit)
        .drop(columns="_band_rank")
    )


def filter_issues(
    frame: pd.DataFrame,
    *,
    search: str = "",
    business_areas: list[str] | None = None,
    severities: list[str] | None = None,
    statuses: list[str] | None = None,
    risk_categories: list[str] | None = None,
    root_causes: list[str] | None = None,
    overdue_only: bool = False,
    escalation_only: bool = False,
    repeat_only: bool = False,
) -> pd.DataFrame:
    """Apply the Issue Register filters without mutating the source frame."""
    result = frame.copy()
    query = search.strip().lower()
    if query:
        searchable = (
            result["issue_id"].fillna("")
            + " "
            + result["issue_title"].fillna("")
            + " "
            + result["issue_description"].fillna("")
            + " "
            + result["affected_process"].fillna("")
        ).str.lower()
        terms = [term for term in query.split() if term]
        matches = pd.Series(True, index=result.index)
        for term in terms:
            matches &= searchable.str.contains(term, regex=False)
        result = result.loc[matches]

    filters = {
        "business_area": business_areas,
        "severity": severities,
        "status": statuses,
        "risk_category": risk_categories,
        "root_cause_category": root_causes,
    }
    for column, values in filters.items():
        if values:
            result = result.loc[result[column].isin(values)]
    if overdue_only:
        result = result.loc[result["overdue_flag"]]
    if escalation_only:
        result = result.loc[result["escalation_required"]]
    if repeat_only:
        result = result.loc[result["repeat_issue"]]
    return result
