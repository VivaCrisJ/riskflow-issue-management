# RiskFlow — Data Dictionary

## Dataset conventions

- All records are synthetic and created solely for demonstration.
- Dates use ISO 8601 format: `YYYY-MM-DD`.
- Currency fields use GBP and contain numeric values only.
- Blank values are permitted where an impact is potential or a lifecycle stage
  has not yet been reached.
- Owners are represented by role title rather than personal name.

## Source fields

| Field | Type | Required | Example | Definition |
|---|---|---:|---|---|
| `issue_id` | string | Yes | `ISS-024` | Unique issue identifier. |
| `issue_title` | string | Yes | `Delayed detection of duplicate payments` | Concise issue title. |
| `business_area` | category | Yes | `Lending Operations` | Business function accountable for the issue. |
| `affected_process` | string | Yes | `Payment Reconciliation` | Process affected by the control weakness. |
| `issue_source` | category | Yes | `Controls Testing` | Channel through which the issue was identified. |
| `date_identified` | date | Yes | `2026-05-12` | Date on which the issue was formally recorded. |
| `issue_description` | text | Yes | `Manual reconciliation did not...` | Evidence-based description of condition, cause and impact. |
| `affected_control` | text | Yes | `Monthly duplicate-payment exception review` | Control that is absent, poorly designed or ineffective. |
| `risk_category` | category | Yes | `Operational Risk` | Primary risk taxonomy classification. |
| `risk_theme` | category | Yes | `Payment Processing` | More specific thematic classification. |
| `severity` | category | Yes | `High` | Initial assessment of issue significance. |
| `customer_impact` | category | Yes | `Potential` | Whether customer harm is absent, potential or actual. |
| `regulatory_impact` | category | Yes | `Potential` | Whether regulatory impact is absent, potential or actual. |
| `financial_impact_gbp` | number | No | `24500` | Known or reasonably estimated financial impact; blank if not measurable. |
| `root_cause_category` | category | Yes | `Manual Process Dependency` | Standardised root-cause classification. |
| `root_cause_detail` | text | Yes | `The reconciliation relied on...` | Analysis of the underlying driver beyond the immediate symptom. |
| `repeat_issue` | boolean | Yes | `True` | Whether a sufficiently similar issue has occurred previously. |
| `control_design_rating` | category | Yes | `Effective` | Whether the control is suitably designed to address the risk. |
| `operating_effectiveness_rating` | category | Yes | `Ineffective` | Whether the control operated consistently as designed. |
| `issue_owner` | string | Yes | `Head of Lending Operations` | Senior role accountable for issue resolution. |
| `action_owner` | string | Yes | `Payments Operations Manager` | Role responsible for completing remediation. |
| `remediation_action` | text | No | `Implement automated duplicate-payment monitoring...` | Agreed corrective action; blank until an action plan exists. |
| `original_target_date` | date | No | `2026-08-31` | Original remediation deadline; blank before an action plan is agreed. |
| `current_target_date` | date | No | `2026-09-15` | Current approved remediation deadline; blank before an action plan is agreed. |
| `extension_count` | integer | Yes | `1` | Number of approved target-date extensions. |
| `status` | category | Yes | `Awaiting Closure Review` | Current issue lifecycle stage. |
| `last_update_date` | date | Yes | `2026-09-20` | Date of the most recent recorded update. |
| `management_commentary` | text | No | `Automated report introduced in August...` | Latest update from the accountable business area. |
| `closure_evidence_summary` | text | No | `Updated procedure and August exception report` | Summary of evidence submitted to support closure. |
| `evidence_status` | category | Yes | `Further Evidence Required` | Current completeness and review state of closure evidence. |
| `evidence_rejection_count` | integer | Yes | `2` | Number of times a closure submission has been returned for further evidence. |
| `validation_method` | text | No | `Sample testing and document inspection` | Method used by the independent reviewer. |
| `closure_review_date` | date | No | `2026-09-22` | Date of the latest closure review. |
| `reviewer_decision` | category | Yes | `Request Further Evidence` | Latest independent review decision. |
| `reviewer_rationale` | text | No | `Evidence demonstrates design but not...` | Evidence-based justification for the decision. |
| `date_closed` | date | No | `2026-09-25` | Date closure was independently approved. |
| `residual_risk` | category | No | `Medium` | Remaining risk after remediation and validation. |

## Allowed values

### `issue_source`

- Controls Testing
- Internal Audit
- RCSA
- Compliance Monitoring
- Operational Incident
- Customer Complaint
- Management Review
- External Audit

### `risk_category`

- Operational Risk
- Credit Risk
- Conduct Risk
- Regulatory Compliance
- Financial Crime
- Technology & Cyber Risk
- Financial Reporting Risk
- Third-Party Risk

### `severity` and `residual_risk`

- Critical
- High
- Medium
- Low

### Impact fields

- None
- Potential
- Actual

### `root_cause_category`

- Manual Process Dependency
- Inadequate Process Design
- System Limitation
- Access Governance
- Data Quality
- Roles and Responsibilities
- Training and Capability
- Inadequate Monitoring
- Third-Party Failure
- Change Management

### Control ratings

- Effective
- Partially Effective
- Ineffective
- Not Yet Tested

### `status`

- Identified
- Under Assessment
- Action Plan Agreed
- Remediation in Progress
- Awaiting Closure Review
- Further Evidence Required
- Closed
- Reopened

### `evidence_status`

- Not Submitted
- Submitted
- Under Review
- Further Evidence Required
- Validated

### `reviewer_decision`

- Pending Review
- Approve Closure
- Request Further Evidence
- Escalate
- Reopen

## Derived fields

These fields are calculated from the reporting date and source data rather than
entered manually.

| Field | Type | Initial rule |
|---|---|---|
| `days_open` | integer | Reporting date minus `date_identified`; frozen at `date_closed` for closed issues. |
| `days_overdue` | integer | Maximum of zero and reporting date minus `current_target_date`; zero where no target is yet agreed or the issue is closed. |
| `overdue_flag` | boolean | A target date exists, is before the reporting date and status is not `Closed`. |
| `escalation_required` | boolean | Triggered by defined severity, delay, extension, impact or failed-evidence conditions. |
| `priority_score` | integer | Transparent 0–100 score based on severity, timeliness, impact and governance factors. |
| `priority_band` | category | `Immediate`, `High`, `Standard` or `Monitor`, derived from priority score. |
| `evidence_completion` | percentage | Completion of required closure-evidence components. |
| `issue_age_band` | category | `0–30`, `31–60`, `61–90` or `90+ days`. |

## Initial closure rule

Closure may be approved only where:

1. remediation is complete;
2. required evidence has been submitted;
3. evidence has passed independent validation;
4. control design is effective;
5. operating effectiveness is effective, or a documented risk-based exception
   has been approved;
6. no material testing exceptions remain unresolved; and
7. reviewer decision and rationale are recorded.

## Initial escalation triggers

Escalation is required when at least one of the following applies:

- severity is Critical;
- a High-severity issue is more than 30 days overdue;
- the target date has been extended two or more times;
- actual customer or regulatory impact is recorded;
- a business owner has not provided a timely update;
- closure evidence has been rejected twice; or
- a common root cause is recurring across multiple business areas.
