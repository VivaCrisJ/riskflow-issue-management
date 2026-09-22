from pathlib import Path

from utils.analytics import (
    closure_approval_blockers,
    closure_decision_outcome,
    closure_readiness,
    classify_issue_text,
    enrich_issues,
    filter_issues,
    load_issues,
    overview_segment,
    priority_queue,
    summary_metrics,
    thematic_summary,
)


DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "synthetic_issues.csv"


def test_summary_metrics_and_core_issue_logic():
    data = enrich_issues(load_issues(DATA_PATH))
    metrics = summary_metrics(data)

    assert len(data) == 48
    assert metrics["Open issues"] == 37
    assert metrics["Overdue"] == 7
    assert metrics["Awaiting closure"] == 7

    duplicate_payment = data.loc[data["issue_id"].eq("ISS-024")].iloc[0]
    assert duplicate_payment["days_overdue"] == 15
    assert duplicate_payment["priority_band"] == "High"
    assert duplicate_payment["priority_score"] == 59

    forbearance = data.loc[data["issue_id"].eq("ISS-011")].iloc[0]
    assert forbearance["priority_band"] == "Immediate"
    assert bool(forbearance["escalation_required"])


def test_closed_issues_are_not_overdue_and_queue_excludes_them():
    data = enrich_issues(load_issues(DATA_PATH))
    closed = data.loc[data["status"].eq("Closed")]
    assert not closed["overdue_flag"].any()

    queue = priority_queue(data, limit=len(data))
    assert not queue["status"].eq("Closed").any()
    assert queue.iloc[0]["priority_band"] == "Immediate"


def test_executive_kpi_segments_reconcile_to_summary_metrics():
    data = enrich_issues(load_issues(DATA_PATH))
    metrics = summary_metrics(data)

    assert len(overview_segment(data, "open")) == metrics["Open issues"]
    assert len(overview_segment(data, "high_critical")) == metrics["Open high & critical"]
    assert len(overview_segment(data, "overdue")) == metrics["Overdue"]
    assert len(overview_segment(data, "awaiting_closure")) == metrics["Awaiting closure"]
    assert len(overview_segment(data, "escalation")) == metrics["Escalation required"]


def test_issue_register_filters_are_composable():
    data = enrich_issues(load_issues(DATA_PATH))

    search_result = filter_issues(data, search="duplicate payments")
    assert search_result["issue_id"].tolist() == ["ISS-024"]

    filtered = filter_issues(
        data,
        business_areas=["Technology"],
        severities=["High"],
        overdue_only=True,
        escalation_only=True,
    )
    assert filtered["issue_id"].tolist() == ["ISS-018"]


def test_closure_rules_block_premature_approval():
    data = enrich_issues(load_issues(DATA_PATH))
    duplicate_payment = data.loc[data["issue_id"].eq("ISS-024")].iloc[0]
    checks = closure_readiness(duplicate_payment)
    blockers = closure_approval_blockers(duplicate_payment)

    assert len(checks) == 6
    assert "Operating effectiveness demonstrated" in blockers
    assert "Evidence independently validated" in blockers

    closed = data.loc[data["issue_id"].eq("ISS-005")].iloc[0]
    assert closure_approval_blockers(closed) == []


def test_closure_decision_outcomes_are_explicit():
    further_evidence = closure_decision_outcome("Request Further Evidence")
    assert further_evidence["status"] == "Further Evidence Required"
    assert further_evidence["evidence_status"] == "Further Evidence Required"


def test_thematic_summary_identifies_cross_business_patterns():
    data = enrich_issues(load_issues(DATA_PATH))
    themes = thematic_summary(data)
    manual = themes.loc[
        themes["root_cause_category"].eq("Manual Process Dependency")
    ].iloc[0]

    assert manual["issue_count"] == 11
    assert manual["business_area_count"] >= 4
    assert bool(manual["systemic_theme"])


def test_rule_assisted_classification_is_explainable():
    result = classify_issue_text(
        "Manual reconciliation resulted in delayed detection of duplicate customer payments."
    )
    assert result["risk_category"] == "Operational Risk"
    assert result["root_cause_category"] == "Manual Process Dependency"
    assert result["risk_theme"] == "Payment Processing"
    assert "manual" in result["matched_terms"]
    assert result["match_strength"] == "Strong rule match"
