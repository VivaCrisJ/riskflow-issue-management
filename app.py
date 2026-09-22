"""RiskFlow interactive portfolio application."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.analytics import (
    REPORTING_DATE,
    closure_approval_blockers,
    closure_decision_outcome,
    closure_readiness,
    classify_issue_text,
    enrich_issues,
    filter_issues,
    load_issues,
    overview_segment,
    priority_factors,
    priority_queue,
    summary_metrics,
    thematic_summary,
)


ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data" / "synthetic_issues.csv"

PALETTE = {
    "navy": "#263946",
    "ink": "#29383F",
    "muted": "#708087",
    "teal": "#6F918F",
    "blue": "#8398A8",
    "slate": "#A8B3B8",
    "sand": "#C6AA7B",
    "rust": "#B77568",
    "red": "#A45F5F",
    "surface": "#FFFFFF",
    "background": "#F4F6F6",
    "line": "#DDE3E4",
}

SEVERITY_COLORS = {
    "Critical": PALETTE["red"],
    "High": PALETTE["rust"],
    "Medium": PALETTE["sand"],
    "Low": PALETTE["blue"],
}


st.set_page_config(
    page_title="RiskFlow",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)


def apply_theme() -> None:
    st.markdown(
        """
        <style>
        :root {
            --rf-navy: #263946;
            --rf-ink: #29383F;
            --rf-muted: #708087;
            --rf-teal: #6F918F;
            --rf-bg: #F4F6F6;
            --rf-line: #DDE3E4;
        }
        .stApp { background: var(--rf-bg); color: var(--rf-ink); }
        [data-testid="stSidebar"] { background: #263946; }
        [data-testid="stSidebar"] * { color: #F4F6F6; }
        [data-testid="stSidebar"] [data-baseweb="radio"] label {
            padding: .52rem .7rem; border-radius: .45rem; margin: .1rem 0;
        }
        [data-testid="stSidebar"] [data-baseweb="radio"] label:hover {
            background: rgba(255,255,255,.07);
        }
        .block-container { max-width: 1460px; padding-top: 4rem; padding-bottom: 3rem; }
        h1, h2, h3 { color: var(--rf-ink); letter-spacing: -.02em; }
        h1 { font-size: 2rem !important; font-weight: 650 !important; }
        h2 { font-size: 1.28rem !important; font-weight: 620 !important; }
        .rf-brand { font-size: 1.35rem; font-weight: 700; letter-spacing: -.02em; margin: .15rem 0 0; }
        .rf-brand-sub { color: #BFCBCD !important; font-size: .78rem; line-height: 1.4; margin-bottom: 1.4rem; }
        .rf-eyebrow { color: var(--rf-teal); text-transform: uppercase; letter-spacing: .12em; font-size: .72rem; font-weight: 700; }
        .rf-subtitle { color: var(--rf-muted); font-size: .96rem; margin-top: -.55rem; }
        .rf-meta { display: flex; gap: .55rem; flex-wrap: wrap; margin: .9rem 0 1.5rem; }
        .rf-pill { border: 1px solid var(--rf-line); background: rgba(255,255,255,.72); color: var(--rf-muted); border-radius: 999px; padding: .3rem .65rem; font-size: .77rem; }
        .rf-metric { background: #FFFFFF; border: 1px solid var(--rf-line); border-radius: .7rem; padding: 1rem 1.05rem; min-height: 106px; box-shadow: 0 1px 2px rgba(38,57,70,.025); }
        .rf-metric-label { color: var(--rf-muted); font-size: .78rem; font-weight: 600; line-height: 1.25; min-height: 2rem; }
        .rf-metric-value { color: var(--rf-ink); font-size: 1.85rem; font-weight: 680; margin-top: .22rem; }
        .rf-metric-link { display:block; color:inherit !important; text-decoration:none !important; border-radius:.7rem; }
        .rf-metric-link .rf-metric { transition: transform .14s ease, border-color .14s ease, box-shadow .14s ease; }
        .rf-metric-link:hover .rf-metric { transform:translateY(-2px); border-color:#9BAFAE; box-shadow:0 6px 18px rgba(38,57,70,.08); }
        .rf-metric-action { color:var(--rf-teal); font-size:.7rem; font-weight:700; margin-top:.12rem; }
        .rf-section-copy { color: var(--rf-muted); font-size: .88rem; margin-top: -.55rem; margin-bottom: .9rem; }
        .rf-card { background: #FFFFFF; border: 1px solid var(--rf-line); border-radius: .7rem; padding: 1rem 1.05rem; }
        .rf-factor { display:flex; justify-content:space-between; gap:1rem; padding:.48rem 0; border-bottom:1px solid #E8EDEE; font-size:.86rem; }
        .rf-factor:last-child { border-bottom:0; }
        .rf-factor-points { color: var(--rf-teal); font-weight: 700; }
        .rf-issue-title { color: var(--rf-ink); font-weight: 650; font-size: 1.02rem; margin-bottom: .25rem; }
        .rf-note { color: var(--rf-muted); font-size: .78rem; line-height: 1.45; }
        div[data-testid="stDataFrame"] { border: 1px solid var(--rf-line); border-radius: .65rem; overflow: hidden; }
        div[data-testid="stSelectbox"] label { color: var(--rf-muted); font-size: .8rem; }
        .stAlert { border-radius: .65rem; }
        footer { visibility: hidden; }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data
def get_data() -> pd.DataFrame:
    return enrich_issues(load_issues(DATA_PATH))


def header(title: str, copy: str) -> None:
    st.markdown('<div class="rf-eyebrow">Risk &amp; Controls</div>', unsafe_allow_html=True)
    st.title(title)
    st.markdown(f'<div class="rf-subtitle">{copy}</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="rf-meta">'
        '<span class="rf-pill">Reporting date · 30 Sep 2026</span>'
        '<span class="rf-pill">Synthetic demonstration data</span>'
        '<span class="rf-pill">48 issues</span>'
        '</div>',
        unsafe_allow_html=True,
    )


def metric_cards(metrics: dict[str, int]) -> None:
    columns = st.columns(len(metrics), gap="small")
    for column, (label, value) in zip(columns, metrics.items()):
        with column:
            st.markdown(
                f'<div class="rf-metric"><div class="rf-metric-label">{label}</div>'
                f'<div class="rf-metric-value">{value}</div></div>',
                unsafe_allow_html=True,
            )


OVERVIEW_METRIC_SEGMENTS = {
    "Open issues": "open",
    "Open high & critical": "high_critical",
    "Overdue": "overdue",
    "Awaiting closure": "awaiting_closure",
    "Escalation required": "escalation",
}


def overview_metric_cards(metrics: dict[str, int]) -> None:
    columns = st.columns(len(metrics), gap="small")
    for column, (label, value) in zip(columns, metrics.items()):
        segment = OVERVIEW_METRIC_SEGMENTS[label]
        with column:
            st.markdown(
                f'<a class="rf-metric-link" href="?overview_filter={segment}#overview-drilldown" target="_self" '
                f'aria-label="View issues for {label}">'
                f'<div class="rf-metric"><div class="rf-metric-label">{label}</div>'
                f'<div class="rf-metric-value">{value}</div>'
                '<div class="rf-metric-action">View issues →</div></div></a>',
                unsafe_allow_html=True,
            )


def _selection_points(state: object) -> list[dict[str, object]]:
    if state is None:
        return []
    selection = state.get("selection", {}) if hasattr(state, "get") else {}
    points = selection.get("points", []) if hasattr(selection, "get") else []
    return list(points)


def _set_overview_chart_focus(chart_key: str, dimension: str, point_field: str) -> None:
    points = _selection_points(st.session_state.get(chart_key))
    if not points:
        return
    value = points[-1].get(point_field)
    if value is None:
        return
    st.session_state["overview_chart_focus"] = {
        "dimension": dimension,
        "value": str(value),
    }
    st.query_params.pop("overview_filter", None)


def _overview_issue_drilldown(
    issues: pd.DataFrame,
    title: str,
    description: str,
    key_suffix: str,
) -> None:
    st.markdown('<div id="overview-drilldown"></div>', unsafe_allow_html=True)
    st.markdown(f"## {title}")
    st.markdown(f'<div class="rf-section-copy">{description}</div>', unsafe_allow_html=True)
    if issues.empty:
        st.info("No issues are currently represented by this selection.")
        return

    ordered = issues.sort_values(["priority_score", "issue_id"], ascending=[False, True]).copy()
    ordered["Issue"] = ordered["issue_id"] + "  ·  " + ordered["issue_title"]
    ordered["Target date"] = ordered["current_target_date"].dt.strftime("%d %b %Y").fillna("Not yet agreed")
    ordered["Overdue"] = ordered["days_overdue"].apply(lambda value: f"{int(value)} days" if value else "—")
    display = ordered[["Issue", "business_area", "severity", "status", "Target date", "Overdue", "priority_score"]]
    display.columns = ["Issue", "Business area", "Severity", "Status", "Target date", "Overdue", "Score"]
    table_state = st.dataframe(
        display,
        hide_index=True,
        width="stretch",
        height=min(430, 38 + 36 * len(display)),
        key=f"overview_drilldown_{key_suffix}",
        on_select="rerun",
        selection_mode="single-row",
        column_config={
            "Issue": st.column_config.TextColumn(width="large"),
            "Business area": st.column_config.TextColumn(width="medium"),
            "Score": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%d"),
        },
    )
    st.caption("Select a row to open its complete issue record.")
    selected_rows = table_state.selection.rows
    if selected_rows:
        selected_issue = ordered.iloc[selected_rows[0]]
        with st.expander(f'{selected_issue["issue_id"]} · Issue detail', expanded=True):
            issue_detail(selected_issue)


def chart_layout(fig: go.Figure, height: int = 310) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=dict(l=18, r=18, t=45, b=18),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(color=PALETTE["ink"], size=12),
        title_font=dict(size=15, color=PALETTE["ink"]),
        legend_title_text="",
        hoverlabel=dict(bgcolor="#FFFFFF", font_color=PALETTE["ink"]),
    )
    return fig


def overview_page(data: pd.DataFrame) -> None:
    header(
        "Executive Overview",
        "A focused view of current exposure, ageing and the issues requiring attention now.",
    )
    overview_metric_cards(summary_metrics(data))

    st.markdown("## Priority Review Queue")
    st.markdown(
        '<div class="rf-section-copy">Ranked using transparent severity, timeliness, impact and governance factors.</div>',
        unsafe_allow_html=True,
    )
    queue = priority_queue(data, limit=6).copy()
    queue["Issue"] = queue["issue_id"] + "  ·  " + queue["issue_title"]
    queue["Target date"] = queue["current_target_date"].dt.strftime("%d %b %Y").fillna("Not yet agreed")
    queue["Days overdue"] = queue["days_overdue"].apply(
        lambda value: f"{int(value)}" if value else "—"
    )
    display = queue[["Issue", "business_area", "severity", "status", "Target date", "Days overdue", "priority_score", "priority_band"]]
    display.columns = ["Issue", "Business area", "Severity", "Status", "Target date", "Days overdue", "Score", "Priority"]
    queue_state = st.dataframe(
        display,
        hide_index=True,
        width="stretch",
        height=276,
        key="overview_priority_queue",
        on_select="rerun",
        selection_mode="single-row",
        column_config={
            "Issue": st.column_config.TextColumn(width="large"),
            "Business area": st.column_config.TextColumn(width="medium"),
            "Score": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%d"),
        },
    )
    st.caption("Select any row to open the complete issue record.")
    selected_queue_rows = queue_state.selection.rows
    if selected_queue_rows:
        selected_issue = queue.iloc[selected_queue_rows[0]]
        with st.expander(f'{selected_issue["issue_id"]} · Issue detail', expanded=True):
            issue_detail(selected_issue)

    st.markdown("## Portfolio profile")
    st.markdown(
        '<div class="rf-section-copy">Select a bar or donut segment to see the underlying issues.</div>',
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.05, 0.95], gap="medium")
    with left:
        status_counts = data["status"].value_counts().sort_values().reset_index()
        status_counts.columns = ["Status", "Issues"]
        fig = px.bar(
            status_counts,
            x="Issues",
            y="Status",
            orientation="h",
            title="Issues by lifecycle status",
            color_discrete_sequence=[PALETTE["teal"]],
        )
        fig.update_traces(marker_line_width=0, hovertemplate="%{y}: %{x}<extra></extra>")
        fig.update_xaxes(showgrid=False, title=None, dtick=2)
        fig.update_yaxes(title=None)
        st.plotly_chart(
            chart_layout(fig, 335),
            width="stretch",
            config={"displayModeBar": False},
            key="overview_status_chart",
            on_select=lambda: _set_overview_chart_focus("overview_status_chart", "status", "y"),
            selection_mode="points",
        )

    with right:
        severity_order = ["Critical", "High", "Medium", "Low"]
        severity_counts = data["severity"].value_counts().reindex(severity_order).fillna(0)
        fig = go.Figure(
            go.Pie(
                labels=severity_counts.index,
                values=severity_counts.values,
                hole=.66,
                marker_colors=[SEVERITY_COLORS[item] for item in severity_counts.index],
                textinfo="label+value",
                textposition="outside",
                hovertemplate="%{label}: %{value} issues<extra></extra>",
            )
        )
        fig.update_layout(title="Issue severity profile", showlegend=False)
        st.plotly_chart(
            chart_layout(fig, 335),
            width="stretch",
            config={"displayModeBar": False},
            key="overview_severity_chart",
            on_select=lambda: _set_overview_chart_focus("overview_severity_chart", "severity", "label"),
            selection_mode="points",
        )

    left, right = st.columns(2, gap="medium")
    with left:
        area_counts = data["business_area"].value_counts().sort_values().reset_index()
        area_counts.columns = ["Business area", "Issues"]
        fig = px.bar(
            area_counts,
            x="Issues",
            y="Business area",
            orientation="h",
            title="Issues by business area",
            color_discrete_sequence=[PALETTE["blue"]],
        )
        fig.update_xaxes(showgrid=False, title=None)
        fig.update_yaxes(title=None)
        st.plotly_chart(
            chart_layout(fig, 330),
            width="stretch",
            config={"displayModeBar": False},
            key="overview_area_chart",
            on_select=lambda: _set_overview_chart_focus("overview_area_chart", "business_area", "y"),
            selection_mode="points",
        )

    with right:
        root_counts = data["root_cause_category"].value_counts().head(6).sort_values().reset_index()
        root_counts.columns = ["Root cause", "Issues"]
        fig = px.bar(
            root_counts,
            x="Issues",
            y="Root cause",
            orientation="h",
            title="Leading root-cause themes",
            color_discrete_sequence=[PALETTE["sand"]],
        )
        fig.update_xaxes(showgrid=False, title=None)
        fig.update_yaxes(title=None)
        st.plotly_chart(
            chart_layout(fig, 330),
            width="stretch",
            config={"displayModeBar": False},
            key="overview_root_chart",
            on_select=lambda: _set_overview_chart_focus("overview_root_chart", "root_cause_category", "y"),
            selection_mode="points",
        )

    metric_segment = st.query_params.get("overview_filter")
    chart_focus = st.session_state.get("overview_chart_focus")
    focused_issues: pd.DataFrame | None = None
    focus_title = ""
    focus_description = ""
    focus_key = ""

    if metric_segment in OVERVIEW_METRIC_SEGMENTS.values():
        label = next(label for label, segment in OVERVIEW_METRIC_SEGMENTS.items() if segment == metric_segment)
        focused_issues = overview_segment(data, metric_segment)
        focus_title = f"{label} · {len(focused_issues)} issues"
        focus_description = "This is the complete issue population represented by the selected executive KPI."
        focus_key = f"metric_{metric_segment}"
    elif chart_focus:
        dimension = chart_focus["dimension"]
        value = chart_focus["value"]
        focused_issues = data.loc[data[dimension].astype(str).eq(value)].copy()
        dimension_label = {
            "status": "Lifecycle status",
            "severity": "Severity",
            "business_area": "Business area",
            "root_cause_category": "Root cause",
        }[dimension]
        focus_title = f"{value} · {len(focused_issues)} issues"
        focus_description = f"Underlying issues for the selected {dimension_label.lower()} category."
        safe_value = "".join(character if character.isalnum() else "_" for character in value)
        focus_key = f"chart_{dimension}_{safe_value}"

    if focused_issues is not None:
        _overview_issue_drilldown(
            focused_issues,
            focus_title,
            focus_description,
            focus_key,
        )
        if st.button("Clear focused view", key="clear_overview_focus"):
            st.session_state.pop("overview_chart_focus", None)
            st.query_params.pop("overview_filter", None)
            st.rerun()


def priority_page(data: pd.DataFrame) -> None:
    header(
        "Priority Review",
        "Understand which issues need action first and why each priority score was assigned.",
    )
    queue = priority_queue(data, limit=len(data))
    labels = {
        row.issue_id: f"{row.issue_id} · {row.issue_title}"
        for row in queue.itertuples()
    }
    default_id = "ISS-024" if "ISS-024" in labels else queue.iloc[0]["issue_id"]
    selected_id = st.selectbox(
        "Select an issue to review",
        options=list(labels),
        index=list(labels).index(default_id),
        format_func=labels.get,
    )
    issue = data.loc[data["issue_id"].eq(selected_id)].iloc[0]

    left, right = st.columns([1.45, .85], gap="medium")
    with left:
        st.markdown(
            f'<div class="rf-card"><div class="rf-issue-title">{issue["issue_id"]} · {issue["issue_title"]}</div>'
            f'<div class="rf-note">{issue["business_area"]} · {issue["risk_category"]} · {issue["status"]}</div>'
            f'<p style="margin-top:1rem;line-height:1.58;font-size:.91rem;">{issue["issue_description"]}</p></div>',
            unsafe_allow_html=True,
        )
        st.markdown("### Current assessment")
        assessment = pd.DataFrame(
            {
                "Field": ["Severity", "Root cause", "Control design", "Operating effectiveness", "Target date", "Days overdue", "Issue owner"],
                "Assessment": [
                    issue["severity"],
                    issue["root_cause_category"],
                    issue["control_design_rating"],
                    issue["operating_effectiveness_rating"],
                    issue["current_target_date"].strftime("%d %b %Y") if pd.notna(issue["current_target_date"]) else "Not yet agreed",
                    str(int(issue["days_overdue"])) if issue["days_overdue"] else "Not overdue",
                    issue["issue_owner"],
                ],
            }
        )
        st.dataframe(assessment, hide_index=True, width="stretch")

    with right:
        factor_rows = "".join(
            f'<div class="rf-factor"><span>{label}</span><span class="rf-factor-points">+{points}</span></div>'
            for label, points in priority_factors(issue)
        )
        st.markdown(
            f'<div class="rf-card"><div class="rf-note">Priority score</div>'
            f'<div style="font-size:2.35rem;font-weight:700;color:{PALETTE["ink"]};">{int(issue["priority_score"])}</div>'
            f'<div class="rf-pill" style="display:inline-block;margin:.15rem 0 .75rem;">{issue["priority_band"]}</div>'
            f'{factor_rows}</div>',
            unsafe_allow_html=True,
        )

    st.markdown("### Priority queue")
    full_queue = queue.copy()
    full_queue["Issue"] = full_queue["issue_id"] + "  ·  " + full_queue["issue_title"]
    full_queue["Overdue"] = full_queue["days_overdue"].apply(lambda value: f"{int(value)} days" if value else "No")
    full_queue["Escalate"] = full_queue["escalation_required"].map({True: "Required", False: "—"})
    st.dataframe(
        full_queue[["Issue", "severity", "priority_score", "priority_band", "Overdue", "Escalate"]].rename(
            columns={"severity": "Severity", "priority_score": "Score", "priority_band": "Priority"}
        ),
        hide_index=True,
        width="stretch",
        height=430,
        column_config={"Score": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%d")},
    )


def _display_date(value: object) -> str:
    return value.strftime("%d %b %Y") if pd.notna(value) else "Not recorded"


def _detail_pair(label: str, value: object) -> str:
    display_value = "Not recorded" if value is None or pd.isna(value) or str(value).strip() == "" else str(value)
    return (
        '<div style="padding:.68rem 0;border-bottom:1px solid #E8EDEE;">'
        f'<div class="rf-note">{label}</div>'
        f'<div style="font-size:.9rem;margin-top:.2rem;line-height:1.45;">{display_value}</div>'
        '</div>'
    )


def issue_detail(issue: pd.Series) -> None:
    st.markdown(
        f'<div class="rf-card"><div class="rf-issue-title">{issue["issue_id"]} · {issue["issue_title"]}</div>'
        f'<div class="rf-note">{issue["business_area"]} · {issue["severity"]} · {issue["status"]}</div>'
        f'<p style="margin-top:1rem;line-height:1.58;font-size:.91rem;">{issue["issue_description"]}</p></div>',
        unsafe_allow_html=True,
    )
    overview, controls, remediation = st.tabs(["Issue overview", "Risk & controls", "Remediation & closure"])
    with overview:
        left, right = st.columns(2, gap="large")
        with left:
            st.markdown(
                _detail_pair("Business area", issue["business_area"])
                + _detail_pair("Affected process", issue["affected_process"])
                + _detail_pair("Issue source", issue["issue_source"])
                + _detail_pair("Date identified", _display_date(issue["date_identified"])),
                unsafe_allow_html=True,
            )
        with right:
            st.markdown(
                _detail_pair("Issue owner", issue["issue_owner"])
                + _detail_pair("Priority", f'{issue["priority_band"]} · {int(issue["priority_score"])} points')
                + _detail_pair("Days open", f'{int(issue["days_open"])} days')
                + _detail_pair("Escalation", "Required" if issue["escalation_required"] else "Not currently required"),
                unsafe_allow_html=True,
            )
    with controls:
        left, right = st.columns(2, gap="large")
        with left:
            st.markdown(
                _detail_pair("Risk category", issue["risk_category"])
                + _detail_pair("Risk theme", issue["risk_theme"])
                + _detail_pair("Root cause", issue["root_cause_category"])
                + _detail_pair("Root-cause analysis", issue["root_cause_detail"]),
                unsafe_allow_html=True,
            )
        with right:
            st.markdown(
                _detail_pair("Affected control", issue["affected_control"])
                + _detail_pair("Control design", issue["control_design_rating"])
                + _detail_pair("Operating effectiveness", issue["operating_effectiveness_rating"])
                + _detail_pair("Customer / regulatory impact", f'{issue["customer_impact"]} / {issue["regulatory_impact"]}'),
                unsafe_allow_html=True,
            )
    with remediation:
        left, right = st.columns(2, gap="large")
        with left:
            st.markdown(
                _detail_pair("Remediation action", issue["remediation_action"])
                + _detail_pair("Action owner", issue["action_owner"])
                + _detail_pair("Original target date", _display_date(issue["original_target_date"]))
                + _detail_pair("Current target date", _display_date(issue["current_target_date"]))
                + _detail_pair("Target extensions", int(issue["extension_count"])),
                unsafe_allow_html=True,
            )
        with right:
            st.markdown(
                _detail_pair("Evidence status", issue["evidence_status"])
                + _detail_pair("Closure evidence", issue["closure_evidence_summary"])
                + _detail_pair("Reviewer decision", issue["reviewer_decision"])
                + _detail_pair("Reviewer rationale", issue["reviewer_rationale"])
                + _detail_pair("Residual risk", issue["residual_risk"]),
                unsafe_allow_html=True,
            )


def issue_register_page(data: pd.DataFrame) -> None:
    header(
        "Issue Register",
        "Search, filter and inspect the complete population of risk and control issues.",
    )
    search = st.text_input(
        "Search issues",
        placeholder="Search by issue ID, title, process or description",
    )
    first, second, third = st.columns(3, gap="small")
    with first:
        business_areas = st.multiselect("Business area", sorted(data["business_area"].unique()))
        risk_categories = st.multiselect("Risk category", sorted(data["risk_category"].unique()))
    with second:
        severities = st.multiselect("Severity", ["Critical", "High", "Medium", "Low"])
        root_causes = st.multiselect("Root cause", sorted(data["root_cause_category"].unique()))
    with third:
        statuses = st.multiselect("Lifecycle status", sorted(data["status"].unique()))
        overdue_only = st.checkbox("Overdue issues only")
        escalation_only = st.checkbox("Escalation required")
        repeat_only = st.checkbox("Repeat issues only")

    filtered = filter_issues(
        data,
        search=search,
        business_areas=business_areas,
        severities=severities,
        statuses=statuses,
        risk_categories=risk_categories,
        root_causes=root_causes,
        overdue_only=overdue_only,
        escalation_only=escalation_only,
        repeat_only=repeat_only,
    ).sort_values(["priority_score", "issue_id"], ascending=[False, True])

    result_left, result_right = st.columns([3, 1])
    with result_left:
        st.markdown(f"### {len(filtered)} issues")
    with result_right:
        export = filtered.copy()
        for column in [name for name in export.columns if "date" in name]:
            export[column] = export[column].dt.strftime("%Y-%m-%d")
        st.download_button(
            "Download filtered CSV",
            data=export.to_csv(index=False).encode("utf-8"),
            file_name="riskflow_filtered_issues.csv",
            mime="text/csv",
            width="stretch",
            disabled=filtered.empty,
        )

    if filtered.empty:
        st.warning("No issues match the selected filters. Adjust one or more criteria to continue.")
        return

    table = filtered.copy()
    table["Issue"] = table["issue_id"] + "  ·  " + table["issue_title"]
    table["Target date"] = table["current_target_date"].dt.strftime("%d %b %Y").fillna("Not yet agreed")
    table["Overdue"] = table["days_overdue"].apply(lambda value: f"{int(value)} days" if value else "—")
    table["Escalation"] = table["escalation_required"].map({True: "Required", False: "—"})
    display = table[["Issue", "business_area", "severity", "status", "issue_owner", "Target date", "Overdue", "priority_score", "Escalation"]]
    display.columns = ["Issue", "Business area", "Severity", "Status", "Issue owner", "Target date", "Overdue", "Score", "Escalation"]
    st.dataframe(
        display,
        hide_index=True,
        width="stretch",
        height=410,
        column_config={
            "Issue": st.column_config.TextColumn(width="large"),
            "Business area": st.column_config.TextColumn(width="medium"),
            "Issue owner": st.column_config.TextColumn(width="medium"),
            "Score": st.column_config.ProgressColumn(min_value=0, max_value=100, format="%d"),
        },
    )

    st.markdown("## Issue Detail")
    labels = {
        row.issue_id: f"{row.issue_id} · {row.issue_title}"
        for row in filtered.itertuples()
    }
    default_id = "ISS-024" if "ISS-024" in labels else next(iter(labels))
    selected_id = st.selectbox(
        "Open issue",
        options=list(labels),
        index=list(labels).index(default_id),
        format_func=labels.get,
        key="register_issue_selector",
    )
    issue_detail(filtered.loc[filtered["issue_id"].eq(selected_id)].iloc[0])


def _readiness_panel(issue: pd.Series) -> None:
    st.markdown("### Closure readiness")
    for item in closure_readiness(issue):
        tone = PALETTE["teal"] if item["passed"] else PALETTE["rust"]
        state = "Ready" if item["passed"] else "Evidence gap"
        st.markdown(
            '<div class="rf-card" style="padding:.72rem .85rem;margin-bottom:.48rem;">'
            f'<div style="display:flex;justify-content:space-between;gap:1rem;align-items:center;">'
            f'<span style="font-size:.87rem;font-weight:620;">{item["check"]}</span>'
            f'<span style="font-size:.72rem;font-weight:700;color:{tone};">{state}</span></div>'
            f'<div class="rf-note" style="margin-top:.22rem;">{item["detail"]}</div></div>',
            unsafe_allow_html=True,
        )


def closure_review_page(data: pd.DataFrame) -> None:
    header(
        "Closure Review",
        "Assess remediation evidence, challenge premature closure and record an independent decision.",
    )
    review_queue = data.loc[
        data["status"].isin(["Awaiting Closure Review", "Further Evidence Required"])
    ].sort_values(["priority_score", "days_overdue"], ascending=[False, False])

    metrics = {
        "Closure review queue": int(len(review_queue)),
        "Awaiting first review": int(review_queue["status"].eq("Awaiting Closure Review").sum()),
        "Further evidence required": int(review_queue["status"].eq("Further Evidence Required").sum()),
        "High-risk reviews": int(review_queue["severity"].isin(["Critical", "High"]).sum()),
    }
    metric_cards(metrics)

    labels = {
        row.issue_id: f"{row.issue_id} · {row.issue_title}"
        for row in review_queue.itertuples()
    }
    default_id = "ISS-024" if "ISS-024" in labels else next(iter(labels))
    selected_id = st.selectbox(
        "Select an issue for closure review",
        options=list(labels),
        index=list(labels).index(default_id),
        format_func=labels.get,
        key="closure_issue_selector",
    )
    issue = data.loc[data["issue_id"].eq(selected_id)].iloc[0]

    st.markdown(
        f'<div class="rf-card"><div class="rf-issue-title">{issue["issue_id"]} · {issue["issue_title"]}</div>'
        f'<div class="rf-note">{issue["business_area"]} · {issue["severity"]} · {issue["status"]}</div>'
        f'<p style="margin-top:1rem;line-height:1.58;font-size:.91rem;">{issue["issue_description"]}</p></div>',
        unsafe_allow_html=True,
    )

    evidence_col, readiness_col = st.columns([1.08, .92], gap="medium")
    with evidence_col:
        st.markdown("### Evidence submitted")
        st.markdown(
            '<div class="rf-card">'
            + _detail_pair("Remediation action", issue["remediation_action"])
            + _detail_pair("Management commentary", issue["management_commentary"])
            + _detail_pair("Closure evidence", issue["closure_evidence_summary"])
            + _detail_pair("Validation method", issue["validation_method"])
            + _detail_pair("Control design", issue["control_design_rating"])
            + _detail_pair("Operating effectiveness", issue["operating_effectiveness_rating"])
            + "</div>",
            unsafe_allow_html=True,
        )
    with readiness_col:
        _readiness_panel(issue)

    st.markdown("## Independent reviewer decision")
    decision = st.radio(
        "Decision",
        ["Request Further Evidence", "Approve Closure", "Escalate Issue"],
        horizontal=True,
        key=f"closure_decision_{selected_id}",
    )
    templates = {
        "Request Further Evidence": "Closure cannot yet be supported. The evidence demonstrates implementation of the redesigned control, but sustained operating effectiveness has not been established across a sufficient period and population.",
        "Approve Closure": "The remediation evidence is complete and independent validation demonstrates that the redesigned control is appropriately designed and operating effectively.",
        "Escalate Issue": "The issue should remain open and be escalated for governance review due to the level of risk, unresolved evidence gaps and potential impact.",
    }
    rationale = st.text_area(
        "Reviewer rationale",
        value=templates[decision],
        height=125,
        key=f"closure_rationale_{selected_id}_{decision}",
    )
    evidence_requests: list[str] = []
    if decision == "Request Further Evidence":
        evidence_requests = st.multiselect(
            "Additional evidence required",
            [
                "Three months of operating evidence",
                "Complete exception population",
                "Independent reviewer sign-off",
                "Post-implementation sample testing",
                "Evidence of exception follow-up",
            ],
            default=["Three months of operating evidence", "Post-implementation sample testing"],
        )

    blockers = closure_approval_blockers(issue) if decision == "Approve Closure" else []
    if blockers:
        st.warning("Closure approval is blocked: " + "; ".join(blockers) + ".")

    action_col, reset_col = st.columns([3, 1])
    with action_col:
        submit = st.button(
            "Record review decision",
            type="primary",
            disabled=bool(blockers),
            width="stretch",
        )
    with reset_col:
        reset = st.button("Reset demonstration", width="stretch")

    reviews = st.session_state.setdefault("closure_reviews", {})
    if reset:
        reviews.pop(selected_id, None)
        st.rerun()
    if submit:
        if len(rationale.strip()) < 30:
            st.error("Add a clear evidence-based rationale of at least 30 characters.")
        elif decision == "Request Further Evidence" and not evidence_requests:
            st.error("Select at least one additional evidence requirement.")
        else:
            outcome = closure_decision_outcome(decision)
            reviews[selected_id] = {
                "decision": decision,
                "rationale": rationale.strip(),
                "evidence_requests": evidence_requests,
                "status": outcome["status"],
                "evidence_status": outcome["evidence_status"],
                "governance_action": outcome["governance_action"],
                "review_date": "30 Sep 2026",
                "reviewer": "Independent Controls Reviewer",
            }

    if selected_id in reviews:
        review = reviews[selected_id]
        st.success(f'Review recorded for this demonstration: {review["decision"]}.')
        st.markdown("### Demonstration outcome")
        before, after = st.columns(2, gap="medium")
        with before:
            st.markdown(
                '<div class="rf-card"><div class="rf-note">Before review</div>'
                + _detail_pair("Status", issue["status"])
                + _detail_pair("Evidence status", issue["evidence_status"])
                + "</div>",
                unsafe_allow_html=True,
            )
        with after:
            st.markdown(
                '<div class="rf-card"><div class="rf-note">After review</div>'
                + _detail_pair("Status", review["status"])
                + _detail_pair("Evidence status", review["evidence_status"])
                + _detail_pair("Governance action", review["governance_action"])
                + "</div>",
                unsafe_allow_html=True,
            )
        with st.expander("View review audit trail"):
            st.write(f'**Reviewer:** {review["reviewer"]}')
            st.write(f'**Review date:** {review["review_date"]}')
            st.write(f'**Decision:** {review["decision"]}')
            st.write(f'**Rationale:** {review["rationale"]}')
            if review["evidence_requests"]:
                st.write("**Additional evidence required:**")
                for item in review["evidence_requests"]:
                    st.write(f"- {item}")


def thematic_analysis_page(data: pd.DataFrame) -> None:
    header(
        "Thematic Analysis",
        "Identify recurring control weaknesses across the organisation and support consistent issue classification.",
    )
    themes = thematic_summary(data)
    systemic = themes.loc[themes["systemic_theme"]]
    manual_dependency = themes.loc[
        themes["root_cause_category"].eq("Manual Process Dependency")
    ].iloc[0]
    access_governance = themes.loc[
        themes["root_cause_category"].eq("Access Governance")
    ].iloc[0]
    metrics = {
        "Cross-business themes": int(len(systemic)),
        "Manual-dependency issues": int(manual_dependency["issue_count"]),
        "Access-governance issues": int(access_governance["issue_count"]),
        "Repeat issues": int(data["repeat_issue"].sum()),
    }
    metric_cards(metrics)

    st.markdown("## Emerging themes")
    st.markdown(
        '<div class="rf-section-copy">Themes are marked systemic when they appear frequently across at least three business areas.</div>',
        unsafe_allow_html=True,
    )
    theme_columns = st.columns(min(3, len(systemic)), gap="small")
    for column, (_, theme) in zip(theme_columns, systemic.head(3).iterrows()):
        with column:
            st.markdown(
                '<div class="rf-card" style="min-height:190px;">'
                f'<div class="rf-note">Systemic theme</div>'
                f'<div class="rf-issue-title" style="margin-top:.35rem;">{theme["root_cause_category"]}</div>'
                f'<p style="font-size:.86rem;line-height:1.5;color:{PALETTE["muted"]};">'
                f'{int(theme["issue_count"])} issues across {int(theme["business_area_count"])} business areas. '
                f'{int(theme["open_issues"])} remain open and {int(theme["repeat_issues"])} are repeat issues.</p>'
                f'<div class="rf-note">{theme["business_areas"]}</div></div>',
                unsafe_allow_html=True,
            )

    heatmap = pd.crosstab(data["root_cause_category"], data["business_area"])
    heatmap = heatmap.loc[heatmap.sum(axis=1).sort_values(ascending=False).index]
    fig = px.imshow(
        heatmap,
        labels=dict(x="Business area", y="Root cause", color="Issues"),
        color_continuous_scale=[[0, "#F1F4F4"], [.45, "#AFC1C0"], [1, PALETTE["teal"]]],
        aspect="auto",
        text_auto=True,
        title="Root causes across business areas",
    )
    fig.update_xaxes(side="bottom", tickangle=-28)
    fig.update_layout(coloraxis_showscale=False)
    st.plotly_chart(chart_layout(fig, 460), width="stretch", config={"displayModeBar": False})

    display_themes = themes.copy()
    display_themes["Systemic"] = display_themes["systemic_theme"].map({True: "Yes", False: "—"})
    display_themes = display_themes[["root_cause_category", "issue_count", "business_area_count", "open_issues", "high_critical", "overdue", "repeat_issues", "Systemic"]]
    display_themes.columns = ["Root cause", "Issues", "Business areas", "Open", "High / critical", "Overdue", "Repeat", "Systemic"]
    with st.expander("View full thematic summary"):
        st.dataframe(display_themes, hide_index=True, width="stretch")

    st.markdown("## Assisted issue classification")
    st.markdown(
        '<div class="rf-section-copy">A transparent rule-based prototype showing how AI-assisted classification could support consistent triage. Human review remains required.</div>',
        unsafe_allow_html=True,
    )
    description = st.text_area(
        "Issue description",
        value="Manual reconciliation resulted in delayed detection of duplicate customer payments.",
        height=110,
        key="classification_input",
    )
    analyse = st.button("Analyse issue description", type="primary", width="stretch")
    if analyse:
        if len(description.strip()) < 15:
            st.error("Enter a sufficiently detailed issue description before running the analysis.")
        else:
            result = classify_issue_text(description)
            st.session_state["classification_result"] = result

    if "classification_result" in st.session_state:
        result = st.session_state["classification_result"]
        first, second, third = st.columns(3, gap="small")
        classifications = [
            (first, "Suggested risk category", result["risk_category"]),
            (second, "Suggested root cause", result["root_cause_category"]),
            (third, "Suggested risk theme", result["risk_theme"]),
        ]
        for column, label, value in classifications:
            with column:
                st.markdown(
                    f'<div class="rf-card" style="min-height:118px;"><div class="rf-note">{label}</div>'
                    f'<div class="rf-issue-title" style="margin-top:.55rem;">{value}</div></div>',
                    unsafe_allow_html=True,
                )
        detail_left, detail_right = st.columns([1, 1], gap="medium")
        with detail_left:
            st.markdown("### Suggested investigation areas")
            for item in result["suggested_investigation_areas"]:
                st.write(f"- {item}")
        with detail_right:
            st.markdown("### Explainability")
            st.write(f'**Match strength:** {result["match_strength"]}')
            matched = ", ".join(result["matched_terms"]) or "No direct keyword matches"
            st.write(f"**Matched terms:** {matched}")
            st.write(f'**Method:** {result["method"]}')
        st.info("Suggested classification only. Final assessment, challenge and accountability remain with the risk professional.")


def placeholder_page(title: str, copy: str) -> None:
    header(title, copy)
    st.info("This module is included in the approved product design and will be implemented in the next build slice.")


apply_theme()
data = get_data()

with st.sidebar:
    st.markdown('<div class="rf-brand">◈ RiskFlow</div>', unsafe_allow_html=True)
    st.markdown('<div class="rf-brand-sub">Risk &amp; Controls<br>Issue Management</div>', unsafe_allow_html=True)
    page = st.radio(
        "Navigation",
        ["Executive Overview", "Priority Review", "Issue Register", "Closure Review", "Thematic Analysis"],
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.markdown('<div class="rf-brand-sub">Portfolio prototype<br>Human-reviewed decision support</div>', unsafe_allow_html=True)

if page == "Executive Overview":
    overview_page(data)
elif page == "Priority Review":
    priority_page(data)
elif page == "Issue Register":
    issue_register_page(data)
elif page == "Closure Review":
    closure_review_page(data)
else:
    thematic_analysis_page(data)
