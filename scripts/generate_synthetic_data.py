"""Generate the deterministic synthetic dataset used by the RiskFlow demo."""

from __future__ import annotations

import csv
from collections import Counter
from datetime import date, datetime, timedelta
from pathlib import Path


REPORTING_DATE = date(2026, 9, 30)
PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = PROJECT_ROOT / "data" / "synthetic_issues.csv"

BUSINESS_ROLES = {
    "Lending Operations": ("Head of Lending Operations", "Lending Controls Manager"),
    "Technology": ("Chief Technology Officer", "Technology Risk Manager"),
    "Customer Operations": ("Head of Customer Operations", "Customer Controls Manager"),
    "Savings & Deposits": ("Head of Savings Operations", "Savings Controls Manager"),
    "Financial Crime & Compliance": ("Money Laundering Reporting Officer", "Financial Crime Controls Manager"),
    "Finance": ("Finance Director", "Financial Control Manager"),
    "Third-Party Management": ("Chief Operating Officer", "Third-Party Risk Manager"),
}

ROOT_DETAILS = {
    "Manual Process Dependency": "The process relied on manually maintained data and reviewer intervention, increasing the risk of delay, omission and inconsistent execution.",
    "Inadequate Process Design": "The documented process did not contain sufficiently precise preventive and detective steps for the risk identified.",
    "System Limitation": "The current system configuration did not provide complete automated validation, exception handling or monitoring capability.",
    "Access Governance": "Access roles, approvals or periodic recertification requirements were not defined and evidenced consistently.",
    "Data Quality": "Incomplete or inaccurate source data reduced the reliability of downstream monitoring and management information.",
    "Roles and Responsibilities": "Accountability between teams was unclear, resulting in gaps in ownership, review and timely escalation.",
    "Training and Capability": "Guidance and role-based training did not equip staff to apply the control consistently in higher-risk cases.",
    "Inadequate Monitoring": "Management information and exception monitoring were not sufficiently timely or granular to identify deterioration.",
    "Third-Party Failure": "Supplier oversight and assurance did not provide sufficient evidence that the outsourced control environment remained effective.",
    "Change Management": "The change process did not consistently assess, approve, test and evidence control impacts before implementation.",
}

ROOT_ACTIONS = {
    "Manual Process Dependency": "Introduce controlled automation and an independent exception review for {process}.",
    "Inadequate Process Design": "Redesign and document the end-to-end control steps for {process}, including ownership and escalation criteria.",
    "System Limitation": "Implement a system enhancement with automated validation, alerting and retained audit evidence for {process}.",
    "Access Governance": "Define least-privilege roles and complete evidenced access approval and recertification for {process}.",
    "Data Quality": "Introduce source-data validation, exception reporting and accountable review for {process}.",
    "Roles and Responsibilities": "Assign accountable owners and introduce a documented review and escalation workflow for {process}.",
    "Training and Capability": "Deliver role-based guidance and quality assurance checks for staff performing {process}.",
    "Inadequate Monitoring": "Introduce risk-based management information, thresholds and documented exception follow-up for {process}.",
    "Third-Party Failure": "Strengthen supplier assurance, service monitoring and contingency evidence for {process}.",
    "Change Management": "Introduce control-impact assessment, approval and post-implementation validation for {process} changes.",
}


def make_issue(
    title: str,
    business: str,
    process: str,
    source: str,
    risk: str,
    theme: str,
    severity: str,
    root: str,
    status: str,
    identified: str,
    control: str,
    *,
    original_due: str = "",
    current_due: str = "",
    extensions: int = 0,
    customer: str = "None",
    regulatory: str = "None",
    financial: int | str = "",
    repeat: bool = False,
    evidence_rejections: int = 0,
) -> dict[str, object]:
    return {
        "issue_title": title,
        "business_area": business,
        "affected_process": process,
        "issue_source": source,
        "risk_category": risk,
        "risk_theme": theme,
        "severity": severity,
        "root_cause_category": root,
        "status": status,
        "date_identified": identified,
        "affected_control": control,
        "original_target_date": original_due,
        "current_target_date": current_due,
        "extension_count": extensions,
        "customer_impact": customer,
        "regulatory_impact": regulatory,
        "financial_impact_gbp": financial,
        "repeat_issue": repeat,
        "evidence_rejection_count": evidence_rejections,
    }


SPECS = [
    make_issue("Unreconciled loan settlement suspense items", "Lending Operations", "Loan Settlement Reconciliation", "Controls Testing", "Operational Risk", "Payment Processing", "High", "Manual Process Dependency", "Awaiting Closure Review", "2026-03-12", "Daily suspense reconciliation independently reviewed", original_due="2026-09-20", current_due="2026-10-10", extensions=1),
    make_issue("Affordability evidence not retained consistently", "Lending Operations", "Affordability Assessment", "Compliance Monitoring", "Conduct Risk", "Responsible Lending", "Critical", "Inadequate Process Design", "Remediation in Progress", "2026-01-20", "Completed affordability assessment and supporting evidence retained", original_due="2026-07-31", current_due="2026-10-31", extensions=1, customer="Potential", regulatory="Potential", repeat=True),
    make_issue("Post-completion quality assurance sample too narrow", "Lending Operations", "Post-Completion Quality Assurance", "RCSA", "Credit Risk", "Quality Assurance", "Medium", "Inadequate Monitoring", "Action Plan Agreed", "2026-07-08", "Monthly risk-based sample of completed lending cases", original_due="2026-11-15", current_due="2026-11-15"),
    make_issue("Collateral valuation overrides not centrally monitored", "Lending Operations", "Collateral Valuation", "Internal Audit", "Credit Risk", "Valuation Controls", "High", "Data Quality", "Under Assessment", "2026-09-02", "Valuation overrides approved and reported against thresholds"),
    make_issue("Broker commission reconciliation differences", "Lending Operations", "Broker Commission Reconciliation", "External Audit", "Financial Reporting Risk", "Reconciliations", "Medium", "Manual Process Dependency", "Closed", "2025-11-03", "Monthly broker commission reconciliation reviewed by Finance", original_due="2026-03-31", current_due="2026-04-15", extensions=1),
    make_issue("Interest adjustment approvals lack complete evidence", "Lending Operations", "Loan Interest Adjustments", "Controls Testing", "Operational Risk", "Account Adjustments", "Medium", "Inadequate Process Design", "Further Evidence Required", "2026-02-14", "Interest adjustments approved by an authorised independent reviewer", original_due="2026-08-31", current_due="2026-09-10", extensions=1),
    make_issue("Arrears status updates delayed", "Lending Operations", "Arrears Management", "Management Review", "Conduct Risk", "Collections", "High", "Manual Process Dependency", "Remediation in Progress", "2026-01-09", "Daily arrears status interface reconciled to the collections platform", original_due="2026-06-30", current_due="2026-07-31", extensions=2, customer="Potential", repeat=True),
    make_issue("Credit decision override log incomplete", "Lending Operations", "Credit Decision Overrides", "Internal Audit", "Credit Risk", "Credit Decisioning", "High", "Access Governance", "Closed", "2025-10-18", "Override access restricted and all decisions recorded with approver rationale", original_due="2026-02-28", current_due="2026-03-31", extensions=1, repeat=True),
    make_issue("Emergency production access lacks segregation", "Technology", "Emergency Production Access", "Controls Testing", "Technology & Cyber Risk", "Privileged Access", "Medium", "Access Governance", "Remediation in Progress", "2026-06-11", "Emergency access approved, time-limited and independently reviewed", original_due="2026-10-31", current_due="2026-10-31"),
    make_issue("Legacy server ownership records incomplete", "Technology", "Technology Asset Ownership", "RCSA", "Technology & Cyber Risk", "Asset Management", "Low", "Roles and Responsibilities", "Identified", "2026-09-25", "Technology assets assigned to accountable business and technical owners"),
    make_issue("Forbearance options not applied consistently to vulnerable customers", "Customer Operations", "Customer Forbearance", "Customer Complaint", "Conduct Risk", "Vulnerable Customers", "Critical", "Inadequate Process Design", "Reopened", "2025-12-06", "Forbearance decisions evidence customer circumstances, vulnerability and fair outcomes", original_due="2026-05-31", current_due="2026-10-31", extensions=2, customer="Actual", regulatory="Actual", financial=8200, repeat=True),
    make_issue("Leaver access removal not completed within policy", "Technology", "Joiner Mover Leaver", "Internal Audit", "Technology & Cyber Risk", "Identity and Access Management", "High", "Access Governance", "Under Assessment", "2026-09-04", "Leaver access automatically disabled and exceptions reviewed daily", customer="Potential", repeat=True),
    make_issue("Complaint refund approvals rely on manual evidence", "Customer Operations", "Complaint Redress", "Operational Incident", "Conduct Risk", "Customer Redress", "Medium", "Manual Process Dependency", "Remediation in Progress", "2026-05-19", "Customer refunds independently approved against redress calculations", original_due="2026-10-31", current_due="2026-10-31", customer="Actual", financial=3600),
    make_issue("Call-quality review evidence is incomplete", "Customer Operations", "Call Quality Assurance", "Compliance Monitoring", "Conduct Risk", "Customer Communications", "High", "Inadequate Monitoring", "Further Evidence Required", "2026-02-22", "Risk-based calls sampled and assessed against conduct standards", original_due="2026-08-31", current_due="2026-10-15", extensions=1, customer="Potential", evidence_rejections=2),
    make_issue("Address-change verification inconsistently recorded", "Customer Operations", "Customer Detail Amendments", "Controls Testing", "Operational Risk", "Customer Authentication", "Medium", "Manual Process Dependency", "Awaiting Closure Review", "2026-04-04", "Material customer-detail changes independently verified", original_due="2026-09-30", current_due="2026-10-20", extensions=1, customer="Potential"),
    make_issue("Bereavement cases routed inconsistently", "Customer Operations", "Bereavement Support", "Management Review", "Conduct Risk", "Customer Support", "Medium", "Training and Capability", "Closed", "2025-12-15", "Bereavement cases triaged and handled under documented specialist guidance", original_due="2026-05-31", current_due="2026-05-31", customer="Potential"),
    make_issue("Vulnerability flags missing from migrated records", "Customer Operations", "Customer Data Migration", "Operational Incident", "Conduct Risk", "Vulnerable Customers", "Medium", "Data Quality", "Further Evidence Required", "2026-03-08", "Migration completeness reconciled and vulnerability flags validated", original_due="2026-08-15", current_due="2026-10-25", extensions=1, customer="Potential", repeat=True),
    make_issue("Privileged access recertification overdue", "Technology", "Privileged Access Management", "Controls Testing", "Technology & Cyber Risk", "Privileged Access", "High", "Access Governance", "Remediation in Progress", "2026-01-18", "Quarterly privileged access recertification approved by system owners", original_due="2026-06-30", current_due="2026-08-15", extensions=2, regulatory="Potential", repeat=True),
    make_issue("Vulnerability remediation evidence incomplete", "Technology", "Vulnerability Management", "Internal Audit", "Technology & Cyber Risk", "Cyber Resilience", "High", "Inadequate Monitoring", "Awaiting Closure Review", "2026-03-25", "Critical vulnerabilities remediated within tolerance and independently evidenced", original_due="2026-09-30", current_due="2026-10-15", extensions=1, regulatory="Potential"),
    make_issue("Backup restoration testing coverage insufficient", "Technology", "Backup and Recovery", "RCSA", "Technology & Cyber Risk", "Operational Resilience", "Medium", "System Limitation", "Action Plan Agreed", "2026-07-14", "Risk-based restoration tests completed and exceptions tracked", original_due="2026-12-15", current_due="2026-12-15"),
    make_issue("Batch-job failure alerts do not cover all critical interfaces", "Technology", "Automated Batch Monitoring", "Operational Incident", "Technology & Cyber Risk", "System Monitoring", "Medium", "System Limitation", "Remediation in Progress", "2026-05-29", "Critical batch failures generate alerts with accountable response and escalation", original_due="2026-11-30", current_due="2026-11-30"),
    make_issue("Service-account ownership records not reviewed", "Technology", "Service Account Governance", "Management Review", "Technology & Cyber Risk", "Identity and Access Management", "Low", "Access Governance", "Closed", "2025-11-21", "Service accounts have named owners and periodic recertification", original_due="2026-04-30", current_due="2026-04-30"),
    make_issue("Identity-verification exceptions not consistently recorded", "Customer Operations", "Customer Identity Verification", "Compliance Monitoring", "Financial Crime", "Customer Due Diligence", "Low", "Roles and Responsibilities", "Closed", "2026-01-11", "Identity-verification exceptions documented and independently approved", original_due="2026-06-30", current_due="2026-06-30", regulatory="Potential"),
    make_issue("Duplicate customer payments detected late", "Lending Operations", "Payment Reconciliation", "Operational Incident", "Operational Risk", "Payment Processing", "High", "Manual Process Dependency", "Awaiting Closure Review", "2026-05-12", "Daily duplicate-payment exception report independently reviewed", original_due="2026-08-31", current_due="2026-09-15", extensions=1, customer="Actual", financial=24500, repeat=True),
    make_issue("Standing-order amendments lack independent verification", "Savings & Deposits", "Standing Order Amendments", "Controls Testing", "Operational Risk", "Payment Instructions", "Medium", "Manual Process Dependency", "Remediation in Progress", "2026-05-05", "Standing-order amendments independently verified before release", original_due="2026-10-31", current_due="2026-10-31", customer="Potential"),
    make_issue("Dormant-account review exceptions", "Savings & Deposits", "Dormant Account Monitoring", "Compliance Monitoring", "Financial Crime", "Dormant Accounts", "Medium", "Inadequate Monitoring", "Closed", "2025-12-02", "Dormant-account activity reviewed against defined risk thresholds", original_due="2026-05-15", current_due="2026-05-31", extensions=1, regulatory="Potential"),
    make_issue("Account-closure instructions not logged centrally", "Savings & Deposits", "Savings Account Closure", "Customer Complaint", "Operational Risk", "Account Servicing", "Low", "Manual Process Dependency", "Identified", "2026-09-27", "Closure instructions logged, authenticated and tracked to completion", customer="Potential"),
    make_issue("Maturity-instruction validation gaps", "Savings & Deposits", "Fixed-Term Maturity", "RCSA", "Operational Risk", "Maturity Processing", "Medium", "Inadequate Process Design", "Under Assessment", "2026-09-08", "Maturity instructions authenticated and independently validated", customer="Potential"),
    make_issue("FSCS disclosure review not embedded in change workflow", "Savings & Deposits", "Customer Disclosure Management", "Compliance Monitoring", "Regulatory Compliance", "Customer Disclosures", "Medium", "Inadequate Process Design", "Action Plan Agreed", "2026-07-21", "Disclosure changes receive Compliance approval before release", original_due="2026-11-30", current_due="2026-11-30", regulatory="Potential"),
    make_issue("Savings interest-rate change verification incomplete", "Savings & Deposits", "Interest Rate Changes", "Controls Testing", "Conduct Risk", "Pricing and Interest", "High", "Change Management", "Awaiting Closure Review", "2026-04-18", "Rate changes independently verified across systems and customer communications", original_due="2026-09-30", current_due="2026-10-15", extensions=1, customer="Potential", regulatory="Potential"),
    make_issue("AML screening-list update deployed late", "Financial Crime & Compliance", "Sanctions and AML Screening", "Operational Incident", "Financial Crime", "Screening Controls", "Critical", "Change Management", "Remediation in Progress", "2026-01-29", "Screening lists updated, reconciled and independently confirmed within tolerance", original_due="2026-06-30", current_due="2026-08-15", extensions=2, regulatory="Potential", repeat=True),
    make_issue("SAR case-ageing report omitted reassigned cases", "Financial Crime & Compliance", "Suspicious Activity Reporting", "Management Review", "Financial Crime", "Case Management", "Medium", "Data Quality", "Closed", "2025-11-29", "Complete SAR population reconciled to case-ageing management information", original_due="2026-04-30", current_due="2026-05-15", extensions=1, regulatory="Potential"),
    make_issue("PEP review documentation inconsistent", "Financial Crime & Compliance", "Politically Exposed Person Reviews", "Compliance Monitoring", "Financial Crime", "Enhanced Due Diligence", "Medium", "Training and Capability", "Action Plan Agreed", "2026-07-10", "PEP reviews evidence risk assessment, approval and review rationale", original_due="2026-12-15", current_due="2026-12-15", regulatory="Potential"),
    make_issue("Transaction-monitoring threshold ownership unclear", "Financial Crime & Compliance", "Transaction Monitoring", "Internal Audit", "Financial Crime", "Monitoring Governance", "Medium", "Roles and Responsibilities", "Remediation in Progress", "2026-05-16", "Threshold changes assigned, approved, tested and periodically reviewed", original_due="2026-11-15", current_due="2026-11-15", regulatory="Potential"),
    make_issue("Sanctions-alert dispositions lack sufficient rationale", "Financial Crime & Compliance", "Sanctions Alert Review", "Controls Testing", "Financial Crime", "Sanctions Screening", "High", "Training and Capability", "Further Evidence Required", "2026-02-19", "Alert dispositions document evidence, rationale and independent quality review", original_due="2026-08-31", current_due="2026-10-15", extensions=1, regulatory="Potential", evidence_rejections=2),
    make_issue("Screening-administrator rights not segregated", "Financial Crime & Compliance", "Screening System Access", "Internal Audit", "Technology & Cyber Risk", "Access Management", "Low", "Access Governance", "Closed", "2025-12-20", "Screening administration separated from alert disposition and recertified", original_due="2026-05-31", current_due="2026-05-31", regulatory="Potential"),
    make_issue("Aged suspense items not escalated", "Finance", "Suspense Account Reconciliation", "External Audit", "Financial Reporting Risk", "Reconciliations", "Medium", "Manual Process Dependency", "Remediation in Progress", "2026-04-02", "Aged suspense items reviewed against thresholds and escalated", original_due="2026-10-31", current_due="2026-10-31", financial=68000, repeat=True),
    make_issue("Manual-journal support not retained consistently", "Finance", "Manual Journal Review", "Controls Testing", "Financial Reporting Risk", "Journal Controls", "Medium", "Manual Process Dependency", "Awaiting Closure Review", "2026-04-27", "Manual journals independently approved with complete supporting evidence", original_due="2026-09-30", current_due="2026-10-20", extensions=1),
    make_issue("Regulatory-return variance review", "Finance", "Regulatory Reporting", "External Audit", "Regulatory Compliance", "Regulatory Reporting", "Low", "Data Quality", "Closed", "2025-10-27", "Material return variances investigated and independently approved", original_due="2026-03-31", current_due="2026-03-31", regulatory="Potential"),
    make_issue("Critical supplier outage exposed untested recovery dependency", "Third-Party Management", "Supplier Continuity and Recovery", "Operational Incident", "Third-Party Risk", "Operational Resilience", "High", "Third-Party Failure", "Remediation in Progress", "2026-01-05", "Critical supplier recovery capability tested against contractual tolerances", original_due="2026-05-31", current_due="2026-07-15", extensions=2, customer="Actual", regulatory="Potential", financial=112000, repeat=True),
    make_issue("Savings account-closure fee review", "Savings & Deposits", "Savings Account Closure", "Management Review", "Conduct Risk", "Fees and Charges", "Low", "Inadequate Process Design", "Closed", "2026-01-26", "Closure fees independently reviewed against product terms and customer outcome standards", original_due="2026-06-30", current_due="2026-06-30", customer="Potential"),
    make_issue("Credit override permissions reappeared after remediation", "Lending Operations", "Credit Decision Overrides", "Controls Testing", "Credit Risk", "Credit Decisioning", "High", "Access Governance", "Reopened", "2026-06-03", "Override access restricted and periodically reconciled to approved roles", original_due="2026-07-31", current_due="2026-08-20", extensions=2, repeat=True),
    make_issue("Month-end reconciliation sign-off delayed", "Finance", "Month-End Reconciliations", "Controls Testing", "Financial Reporting Risk", "Reconciliations", "Medium", "Manual Process Dependency", "Awaiting Closure Review", "2026-05-08", "Month-end reconciliations completed and independently signed off to timetable", original_due="2026-09-30", current_due="2026-10-15", extensions=1),
    make_issue("Finance-system access recertification population incomplete", "Finance", "Finance System Access", "Internal Audit", "Technology & Cyber Risk", "Access Management", "Medium", "Access Governance", "Under Assessment", "2026-09-06", "Complete finance-system access population periodically recertified"),
    make_issue("Supplier bank-detail changes", "Finance", "Supplier Master Data", "External Audit", "Financial Crime", "Payment Fraud", "Low", "Inadequate Process Design", "Closed", "2025-12-12", "Supplier bank-detail changes independently authenticated and approved", original_due="2026-05-31", current_due="2026-05-31", financial=12500),
    make_issue("Supplier exit plans not tested", "Third-Party Management", "Supplier Exit Planning", "RCSA", "Third-Party Risk", "Operational Resilience", "Low", "Third-Party Failure", "Identified", "2026-09-24", "Critical supplier exit plans periodically exercised and evidenced"),
    make_issue("Critical supplier assurance reports not reviewed promptly", "Third-Party Management", "Supplier Assurance", "Internal Audit", "Third-Party Risk", "Supplier Oversight", "High", "Third-Party Failure", "Remediation in Progress", "2026-04-15", "Supplier assurance reports risk-assessed and exceptions tracked to resolution", original_due="2026-10-31", current_due="2026-10-31", regulatory="Potential"),
    make_issue("Outsourcing inventory evidence incomplete", "Third-Party Management", "Outsourcing Inventory", "Compliance Monitoring", "Regulatory Compliance", "Outsourcing Governance", "Low", "Roles and Responsibilities", "Further Evidence Required", "2026-03-17", "Complete outsourcing inventory reconciled and approved by accountable owners", original_due="2026-08-31", current_due="2026-10-31", extensions=1, regulatory="Potential"),
]


ANCHOR_DESCRIPTIONS = {
    11: "Quality review and complaint evidence showed that customer vulnerability and affordability circumstances were not consistently considered when selecting forbearance options. The issue recurred after an earlier closure decision.",
    18: "Quarterly recertification was not completed for all privileged accounts, leaving elevated access without current system-owner confirmation and creating an overdue high-risk remediation action.",
    24: "A manual reconciliation did not identify duplicate customer payments promptly. Customers were refunded, but the submitted closure pack contains only one month of the new exception report and does not yet demonstrate sustained operating effectiveness.",
    31: "An approved AML screening-list update was deployed after the required implementation window because change ownership and post-deployment reconciliation were not completed on time.",
    40: "A critical outsourced service outage interrupted customer operations and demonstrated that recovery dependencies had not been tested end to end against agreed impact tolerances.",
}


def parse_date(value: str) -> date | None:
    return datetime.strptime(value, "%Y-%m-%d").date() if value else None


def lifecycle_fields(status: str, severity: str, current_due: str) -> dict[str, object]:
    if status == "Closed":
        closed_date = parse_date(current_due) - timedelta(days=5)
        return {
            "control_design_rating": "Effective",
            "operating_effectiveness_rating": "Effective",
            "evidence_status": "Validated",
            "validation_method": "Document inspection and post-implementation sample testing",
            "closure_review_date": closed_date.isoformat(),
            "reviewer_decision": "Approve Closure",
            "reviewer_rationale": "Remediation evidence was complete and sample testing demonstrated that the redesigned control operated effectively.",
            "date_closed": closed_date.isoformat(),
            "residual_risk": "Medium" if severity in {"Critical", "High"} else "Low",
            "closure_evidence_summary": "Updated procedure, implementation evidence and post-implementation sample testing.",
        }
    if status == "Awaiting Closure Review":
        return {
            "control_design_rating": "Effective",
            "operating_effectiveness_rating": "Partially Effective",
            "evidence_status": "Submitted",
            "validation_method": "Document inspection and sample testing",
            "closure_review_date": "",
            "reviewer_decision": "Pending Review",
            "reviewer_rationale": "",
            "date_closed": "",
            "residual_risk": "",
            "closure_evidence_summary": "Updated procedure and initial implementation evidence submitted for independent review.",
        }
    if status == "Further Evidence Required":
        return {
            "control_design_rating": "Effective",
            "operating_effectiveness_rating": "Partially Effective",
            "evidence_status": "Further Evidence Required",
            "validation_method": "Document inspection and targeted sample testing",
            "closure_review_date": "2026-09-22",
            "reviewer_decision": "Request Further Evidence",
            "reviewer_rationale": "The evidence supports the revised design but does not yet demonstrate complete and sustained operating effectiveness.",
            "date_closed": "",
            "residual_risk": "",
            "closure_evidence_summary": "Procedure and selected implementation evidence submitted; reviewer identified gaps in the testing period or population.",
        }
    if status == "Reopened":
        return {
            "control_design_rating": "Partially Effective",
            "operating_effectiveness_rating": "Ineffective",
            "evidence_status": "Not Submitted",
            "validation_method": "Recurrence analysis and control retesting",
            "closure_review_date": "2026-09-18",
            "reviewer_decision": "Reopen",
            "reviewer_rationale": "Subsequent testing identified recurrence and showed that the previous remediation did not address the underlying cause.",
            "date_closed": "",
            "residual_risk": "",
            "closure_evidence_summary": "Previous closure pack retained; recurrence evidence recorded for reassessment.",
        }
    if status in {"Identified", "Under Assessment"}:
        return {
            "control_design_rating": "Not Yet Tested",
            "operating_effectiveness_rating": "Not Yet Tested",
            "evidence_status": "Not Submitted",
            "validation_method": "",
            "closure_review_date": "",
            "reviewer_decision": "Pending Review",
            "reviewer_rationale": "",
            "date_closed": "",
            "residual_risk": "",
            "closure_evidence_summary": "",
        }
    return {
        "control_design_rating": "Partially Effective" if status == "Remediation in Progress" else "Ineffective",
        "operating_effectiveness_rating": "Ineffective",
        "evidence_status": "Not Submitted",
        "validation_method": "",
        "closure_review_date": "",
        "reviewer_decision": "Pending Review",
        "reviewer_rationale": "",
        "date_closed": "",
        "residual_risk": "",
        "closure_evidence_summary": "",
    }


def enrich(index: int, spec: dict[str, object]) -> dict[str, object]:
    issue_id = f"ISS-{index:03d}"
    owner, action_owner = BUSINESS_ROLES[str(spec["business_area"])]
    root = str(spec["root_cause_category"])
    status = str(spec["status"])
    process = str(spec["affected_process"])
    action = "" if status in {"Identified", "Under Assessment"} else ROOT_ACTIONS[root].format(process=process.lower())
    description = ANCHOR_DESCRIPTIONS.get(
        index,
        f"Review of {process.lower()} identified that the control '{spec['affected_control']}' did not consistently prevent or detect the stated risk. The weakness could lead to delayed identification, inconsistent outcomes or incomplete management information.",
    )
    lifecycle = lifecycle_fields(status, str(spec["severity"]), str(spec["current_target_date"]))
    last_update = lifecycle["date_closed"] or ("2026-09-25" if status in {"Identified", "Under Assessment"} else "2026-09-20")
    commentary = "" if status == "Identified" else (
        "The issue is being assessed and accountable actions will be agreed following completion of evidence review."
        if status == "Under Assessment"
        else "The accountable owner confirmed that remediation remains in progress and supporting evidence will be retained for independent validation."
    )
    return {
        "issue_id": issue_id,
        "issue_title": spec["issue_title"],
        "business_area": spec["business_area"],
        "affected_process": process,
        "issue_source": spec["issue_source"],
        "date_identified": spec["date_identified"],
        "issue_description": description,
        "affected_control": spec["affected_control"],
        "risk_category": spec["risk_category"],
        "risk_theme": spec["risk_theme"],
        "severity": spec["severity"],
        "customer_impact": spec["customer_impact"],
        "regulatory_impact": spec["regulatory_impact"],
        "financial_impact_gbp": spec["financial_impact_gbp"],
        "root_cause_category": root,
        "root_cause_detail": ROOT_DETAILS[root],
        "repeat_issue": str(spec["repeat_issue"]).lower(),
        "control_design_rating": lifecycle["control_design_rating"],
        "operating_effectiveness_rating": lifecycle["operating_effectiveness_rating"],
        "issue_owner": owner,
        "action_owner": action_owner,
        "remediation_action": action,
        "original_target_date": spec["original_target_date"],
        "current_target_date": spec["current_target_date"],
        "extension_count": spec["extension_count"],
        "status": status,
        "last_update_date": last_update,
        "management_commentary": commentary,
        "closure_evidence_summary": lifecycle["closure_evidence_summary"],
        "evidence_status": lifecycle["evidence_status"],
        "evidence_rejection_count": spec["evidence_rejection_count"],
        "validation_method": lifecycle["validation_method"],
        "closure_review_date": lifecycle["closure_review_date"],
        "reviewer_decision": lifecycle["reviewer_decision"],
        "reviewer_rationale": lifecycle["reviewer_rationale"],
        "date_closed": lifecycle["date_closed"],
        "residual_risk": lifecycle["residual_risk"],
    }


def validate_distribution(rows: list[dict[str, object]]) -> None:
    expected = {
        "status": {"Identified": 3, "Under Assessment": 4, "Action Plan Agreed": 4, "Remediation in Progress": 12, "Awaiting Closure Review": 7, "Further Evidence Required": 5, "Closed": 11, "Reopened": 2},
        "severity": {"Critical": 3, "High": 14, "Medium": 21, "Low": 10},
        "business_area": {"Lending Operations": 10, "Technology": 8, "Customer Operations": 7, "Savings & Deposits": 7, "Financial Crime & Compliance": 6, "Finance": 6, "Third-Party Management": 4},
    }
    for field, expected_counts in expected.items():
        actual = Counter(str(row[field]) for row in rows)
        if actual != Counter(expected_counts):
            raise ValueError(f"Unexpected {field} distribution: {dict(actual)}")


def main() -> None:
    rows = [enrich(index, spec) for index, spec in enumerate(SPECS, start=1)]
    if len(rows) != 48:
        raise ValueError(f"Expected 48 issues, found {len(rows)}")
    validate_distribution(rows)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} synthetic issues to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
