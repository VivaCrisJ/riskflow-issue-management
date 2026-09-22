from pathlib import Path

from utils.analytics import enrich_issues, load_issues, priority_queue, summary_metrics


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

