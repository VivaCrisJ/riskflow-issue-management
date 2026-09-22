"""Validate RiskFlow synthetic records against core lifecycle rules."""

from __future__ import annotations

import csv
from collections import Counter
from datetime import date, datetime
from pathlib import Path


REPORTING_DATE = date(2026, 9, 30)
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "synthetic_issues.csv"


def parse_date(value: str) -> date | None:
    return datetime.strptime(value, "%Y-%m-%d").date() if value else None


def main() -> None:
    with DATA_PATH.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    errors: list[str] = []
    issue_ids = [row["issue_id"] for row in rows]
    if len(rows) != 48:
        errors.append(f"Expected 48 rows; found {len(rows)}")
    if len(issue_ids) != len(set(issue_ids)):
        errors.append("Issue IDs are not unique")

    overdue = 0
    escalations = 0
    for row in rows:
        issue_id = row["issue_id"]
        status = row["status"]
        target = parse_date(row["current_target_date"])
        is_overdue = bool(target and target < REPORTING_DATE and status != "Closed")
        overdue += int(is_overdue)

        if status == "Closed":
            required = {
                "date_closed": bool(row["date_closed"]),
                "evidence_status": row["evidence_status"] == "Validated",
                "control_design_rating": row["control_design_rating"] == "Effective",
                "operating_effectiveness_rating": row["operating_effectiveness_rating"] == "Effective",
                "reviewer_decision": row["reviewer_decision"] == "Approve Closure",
            }
            for field, valid in required.items():
                if not valid:
                    errors.append(f"{issue_id}: invalid closed-state field {field}")
        elif row["date_closed"]:
            errors.append(f"{issue_id}: open issue has a closure date")

        if status in {"Identified", "Under Assessment"}:
            if row["remediation_action"] or row["current_target_date"]:
                errors.append(f"{issue_id}: assessment-stage issue has an agreed action or target")

        if status == "Further Evidence Required":
            if row["evidence_status"] != "Further Evidence Required" or row["reviewer_decision"] != "Request Further Evidence":
                errors.append(f"{issue_id}: further-evidence workflow is inconsistent")

        severity_trigger = row["severity"] == "Critical"
        high_overdue_trigger = row["severity"] == "High" and target and (REPORTING_DATE - target).days > 30 and status != "Closed"
        extension_trigger = int(row["extension_count"]) >= 2 and status != "Closed"
        impact_trigger = row["customer_impact"] == "Actual" or row["regulatory_impact"] == "Actual"
        evidence_trigger = int(row["evidence_rejection_count"]) >= 2
        escalations += int(any((severity_trigger, high_overdue_trigger, extension_trigger, impact_trigger, evidence_trigger)))

    if errors:
        raise ValueError("\n".join(errors))

    print("Synthetic data validation passed")
    print(f"Rows: {len(rows)}")
    print(f"Overdue open issues: {overdue}")
    print(f"Issues meeting initial escalation rules: {escalations}")
    print(f"Statuses: {dict(Counter(row['status'] for row in rows))}")
    print(f"Severities: {dict(Counter(row['severity'] for row in rows))}")


if __name__ == "__main__":
    main()
