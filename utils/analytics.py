"""Transparent business rules and management information for RiskFlow."""

from __future__ import annotations

from pathlib import Path
import re

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

RISK_CATEGORY_RULES = {
    "Financial Crime": ["aml", "sanction", "screening", "transaction monitoring", "pep", "suspicious activity", "sar"],
    "Technology & Cyber Risk": ["access", "privileged", "cyber", "vulnerability", "server", "service account", "system security"],
    "Conduct Risk": ["vulnerable", "complaint", "forbearance", "affordability", "customer outcome", "redress"],
    "Credit Risk": ["credit", "collateral", "valuation", "underwriting", "loan decision", "affordability assessment"],
    "Third-Party Risk": ["supplier", "vendor", "third party", "third-party", "outsourced", "outsourcing"],
    "Regulatory Compliance": ["regulatory", "disclosure", "compliance breach", "regulator", "return submission"],
    "Financial Reporting Risk": ["journal", "financial reporting", "month-end", "ledger", "suspense account"],
    "Operational Risk": ["payment", "reconciliation", "duplicate", "processing", "operational", "error", "delay", "failure"],
}

ROOT_CAUSE_RULES = {
    "Manual Process Dependency": ["manual", "manually", "spreadsheet", "rekey", "re-key", "manual reconciliation"],
    "Access Governance": ["access", "privileged", "permission", "leaver", "segregation", "user role"],
    "Data Quality": ["data quality", "incomplete data", "inaccurate", "missing data", "migration", "population incomplete"],
    "System Limitation": ["system limitation", "system could not", "no automated", "interface failure", "batch job", "alert failure"],
    "Inadequate Monitoring": ["monitoring", "not detected", "delayed detection", "exception monitoring", "threshold", "review overdue"],
    "Training and Capability": ["training", "guidance", "staff capability", "knowledge gap", "inconsistent application"],
    "Third-Party Failure": ["supplier", "vendor", "third party", "third-party", "outsourced", "service provider"],
    "Change Management": ["change", "deployment", "release", "implementation update", "configuration change"],
    "Roles and Responsibilities": ["ownership", "owner unclear", "responsibility", "accountability", "handoff"],
    "Inadequate Process Design": ["process design", "procedure", "workflow", "control gap", "control missing", "unclear process"],
}

RISK_THEME_RULES = {
    "Payment Processing": ["payment", "duplicate", "standing order", "refund"],
    "Identity and Access Management": ["access", "privileged", "permission", "leaver", "service account"],
    "Screening Controls": ["aml", "sanction", "screening", "pep"],
    "Customer Outcomes": ["vulnerable", "complaint", "forbearance", "affordability", "redress"],
    "Data Quality": ["data", "migration", "population", "incomplete", "inaccurate"],
    "Operational Resilience": ["outage", "recovery", "continuity", "backup", "supplier failure"],
    "Reconciliations": ["reconciliation", "journal", "ledger", "suspense"],
    "Control Governance": ["approval", "owner", "review", "evidence", "escalation"],
}

INVESTIGATION_AREAS = {
    "Manual Process Dependency": ["automation opportunities", "exception monitoring", "maker-checker controls", "reconciliation completeness"],
    "Access Governance": ["least-privilege design", "access approval", "periodic recertification", "joiner-mover-leaver controls"],
    "Data Quality": ["source-data validation", "population completeness", "reconciliation to source", "exception ownership"],
    "System Limitation": ["automated validation", "alert coverage", "interface monitoring", "manual fallback controls"],
    "Inadequate Monitoring": ["risk-based thresholds", "management information", "exception ageing", "documented follow-up"],
    "Training and Capability": ["role-based guidance", "quality assurance", "competency assessment", "supervisory review"],
    "Third-Party Failure": ["supplier assurance", "service-level monitoring", "business continuity", "exit planning"],
    "Change Management": ["control-impact assessment", "testing evidence", "approval governance", "post-implementation review"],
    "Roles and Responsibilities": ["accountable ownership", "RACI clarity", "handoff controls", "escalation routes"],
    "Inadequate Process Design": ["end-to-end control design", "preventive controls", "detective controls", "exception escalation"],
}


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


def overview_segment(frame: pd.DataFrame, segment: str) -> pd.DataFrame:
    """Return the issue population represented by an executive KPI."""
    open_mask = frame["status"].ne("Closed")
    masks = {
        "open": open_mask,
        "high_critical": open_mask & frame["severity"].isin(["Critical", "High"]),
        "overdue": open_mask & frame["overdue_flag"],
        "awaiting_closure": frame["status"].eq("Awaiting Closure Review"),
        "escalation": open_mask & frame["escalation_required"],
    }
    if segment not in masks:
        raise ValueError(f"Unknown overview segment: {segment}")
    return frame.loc[masks[segment]].copy()


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


def closure_readiness(issue: pd.Series) -> list[dict[str, object]]:
    """Assess the evidence gates required before an issue can be closed."""
    checks = [
        {
            "check": "Remediation action completed",
            "passed": issue["status"] in {"Awaiting Closure Review", "Further Evidence Required", "Closed"},
            "detail": "The business owner has submitted the issue for independent closure review.",
        },
        {
            "check": "Closure evidence submitted",
            "passed": issue["evidence_status"] in {"Submitted", "Under Review", "Validated", "Further Evidence Required"},
            "detail": f'Evidence status: {issue["evidence_status"]}.',
        },
        {
            "check": "Control design effective",
            "passed": issue["control_design_rating"] == "Effective",
            "detail": f'Design assessment: {issue["control_design_rating"]}.',
        },
        {
            "check": "Operating effectiveness demonstrated",
            "passed": issue["operating_effectiveness_rating"] == "Effective",
            "detail": f'Operating assessment: {issue["operating_effectiveness_rating"]}.',
        },
        {
            "check": "Evidence independently validated",
            "passed": issue["evidence_status"] == "Validated",
            "detail": "Independent validation is required before closure approval.",
        },
        {
            "check": "No unresolved material exceptions",
            "passed": issue["operating_effectiveness_rating"] == "Effective" and int(issue["evidence_rejection_count"]) == 0,
            "detail": "Open testing exceptions or returned evidence prevent closure.",
        },
    ]
    return checks


def closure_approval_blockers(issue: pd.Series) -> list[str]:
    """Return failed closure gates that block an Approve Closure decision."""
    return [str(item["check"]) for item in closure_readiness(issue) if not item["passed"]]


def closure_decision_outcome(decision: str) -> dict[str, str]:
    """Map a reviewer decision to the demonstration's resulting workflow state."""
    outcomes = {
        "Approve Closure": {
            "status": "Closed",
            "evidence_status": "Validated",
            "governance_action": "Remove from the open-issue population and retain the closure audit trail.",
        },
        "Request Further Evidence": {
            "status": "Further Evidence Required",
            "evidence_status": "Further Evidence Required",
            "governance_action": "Return the issue to the action owner with an evidenced follow-up requirement.",
        },
        "Escalate Issue": {
            "status": "Awaiting Closure Review",
            "evidence_status": "Under Review",
            "governance_action": "Escalate to the relevant risk governance forum and retain the issue as open.",
        },
    }
    if decision not in outcomes:
        raise ValueError(f"Unsupported closure decision: {decision}")
    return outcomes[decision]


def thematic_summary(frame: pd.DataFrame) -> pd.DataFrame:
    """Aggregate root causes into transparent cross-business risk themes."""
    records: list[dict[str, object]] = []
    for root_cause, group in frame.groupby("root_cause_category"):
        business_areas = sorted(group["business_area"].unique())
        open_group = group.loc[group["status"].ne("Closed")]
        records.append(
            {
                "root_cause_category": root_cause,
                "issue_count": int(len(group)),
                "open_issues": int(len(open_group)),
                "business_area_count": int(len(business_areas)),
                "business_areas": ", ".join(business_areas),
                "high_critical": int(group["severity"].isin(["Critical", "High"]).sum()),
                "overdue": int(group["overdue_flag"].sum()),
                "repeat_issues": int(group["repeat_issue"].sum()),
                "systemic_theme": len(group) >= 5 and len(business_areas) >= 3,
            }
        )
    return pd.DataFrame(records).sort_values(
        ["systemic_theme", "issue_count", "business_area_count"],
        ascending=[False, False, False],
    ).reset_index(drop=True)


def _rule_scores(text: str, rules: dict[str, list[str]]) -> tuple[dict[str, int], dict[str, list[str]]]:
    normalised = re.sub(r"\s+", " ", text.lower()).strip()
    scores: dict[str, int] = {}
    matches: dict[str, list[str]] = {}
    for label, terms in rules.items():
        matched = [term for term in terms if term in normalised]
        scores[label] = len(matched)
        matches[label] = matched
    return scores, matches


def _best_rule_match(
    text: str, rules: dict[str, list[str]], fallback: str
) -> tuple[str, int, list[str]]:
    scores, matches = _rule_scores(text, rules)
    label = max(scores, key=scores.get)
    score = scores[label]
    if score == 0:
        return fallback, 0, []
    return label, score, matches[label]


def classify_issue_text(text: str) -> dict[str, object]:
    """Return explainable, rule-assisted classification suggestions."""
    cleaned = text.strip()
    if not cleaned:
        raise ValueError("Issue description is required")

    risk, risk_score, risk_terms = _best_rule_match(
        cleaned, RISK_CATEGORY_RULES, "Further assessment required"
    )
    root, root_score, root_terms = _best_rule_match(
        cleaned, ROOT_CAUSE_RULES, "Further root-cause analysis required"
    )
    theme, theme_score, theme_terms = _best_rule_match(
        cleaned, RISK_THEME_RULES, "General control governance"
    )
    total_score = risk_score + root_score + theme_score
    if total_score >= 6:
        match_strength = "Strong rule match"
    elif total_score >= 3:
        match_strength = "Moderate rule match"
    else:
        match_strength = "Limited rule match"

    investigation = INVESTIGATION_AREAS.get(
        root,
        ["process walkthrough", "control design assessment", "evidence testing", "accountable owner review"],
    )
    return {
        "risk_category": risk,
        "root_cause_category": root,
        "risk_theme": theme,
        "match_strength": match_strength,
        "matched_terms": sorted(set(risk_terms + root_terms + theme_terms)),
        "suggested_investigation_areas": investigation,
        "method": "Transparent keyword and business-rule prototype",
    }
