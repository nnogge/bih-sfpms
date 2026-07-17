import sqlite3
import hashlib
import json
import re
from io import BytesIO, StringIO
from datetime import datetime
from datetime import date
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

APP_TITLE = "Strategic Financial Planning Management System (SFPMS)"
ORG_NAME = "BIH SOLUTIONS"
ORG_TAGLINE = "Governance-Grade Strategic Execution Platform"
DB_PATH = Path(__file__).parent / "sfpms.db"

# ---------------------------------------------------------------------------
# Corporate design system
# Palette: Ink Navy (authority) + Burnished Gold (governance/approval signal)
# on a cool paper background. Typography: Fraunces (institutional serif for
# headings/masthead) paired with IBM Plex Sans (data-grade sans for body,
# tables and controls).
# ---------------------------------------------------------------------------
NAVY_900 = "#0B1F3A"
NAVY_800 = "#12294B"
NAVY_700 = "#1C3A63"
GOLD_600 = "#AD8A4D"
GOLD_500 = "#C7A45F"
SLATE_700 = "#2B3B52"
SLATE_500 = "#5B6B82"
PAPER = "#F3F5F9"
HAIRLINE = "#DCE2EB"
STATUS_GREEN = "#157347"
STATUS_ORANGE = "#B7791F"
STATUS_RED = "#B3261E"

CORPORATE_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500&display=swap');

html, body, [class*="css"] {{
    font-family: 'IBM Plex Sans', -apple-system, sans-serif;
}}

.stApp {{
    background: {PAPER};
}}

h1, h2, h3, h4 {{
    font-family: 'Fraunces', Georgia, serif !important;
    color: {NAVY_900} !important;
    letter-spacing: -0.01em;
}}

h1 {{ font-weight: 600 !important; }}
h2, h3 {{ font-weight: 600 !important; }}

p, span, div, label, li {{
    color: {SLATE_700};
}}

/* ---- Masthead ---- */
.sfpms-masthead {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: clamp(10px, 2vw, 24px);
    background: linear-gradient(135deg, {NAVY_900} 0%, {NAVY_800} 100%);
    border-radius: 16px;
    padding: clamp(14px, 3vw, 22px) clamp(16px, 4vw, 30px);
    margin-bottom: 20px;
    box-shadow: 0 10px 30px rgba(11,31,58,.18);
    border-bottom: 3px solid {GOLD_600};
    width: 100%;
    box-sizing: border-box;
    overflow-wrap: anywhere;
}}
.sfpms-masthead .crest-block {{
    display:flex; align-items:center; gap: clamp(10px, 2vw, 16px);
    min-width: 0;
    flex: 1 1 260px;
}}
.sfpms-masthead .org-text {{ min-width: 0; }}
.sfpms-masthead .org-text .org-name {{
    font-family: 'IBM Plex Sans', sans-serif;
    color: {GOLD_500};
    font-size: clamp(.62rem, 1.6vw, .74rem);
    font-weight: 700;
    letter-spacing: .2em;
    text-transform: uppercase;
    margin-bottom: 2px;
}}
.sfpms-masthead .org-text .system-name {{
    font-family: 'Fraunces', serif;
    color: #FFFFFF;
    font-size: clamp(1.05rem, 3.4vw, 1.5rem);
    font-weight: 600;
    line-height: 1.18;
}}
.sfpms-masthead .org-text .tagline {{
    color: #A9B7CC;
    font-size: clamp(.68rem, 1.6vw, .78rem);
    font-weight: 400;
    margin-top: 2px;
}}
.sfpms-masthead .badges {{
    display:flex; gap:8px; flex-wrap:wrap; justify-content:flex-end;
    flex: 1 1 auto;
    min-width: 0;
}}
.sfpms-crest {{
    flex: 0 0 auto;
    width: clamp(32px, 7vw, 46px);
    height: clamp(32px, 7vw, 46px);
}}
.sfpms-crest svg {{ width: 100%; height: 100%; display: block; }}
.sfpms-badge {{
    background: rgba(255,255,255,.08);
    border: 1px solid rgba(199,164,95,.45);
    color: #EDE6D8;
    font-size: clamp(.62rem, 1.5vw, .72rem);
    font-weight: 600;
    padding: clamp(4px, 1vw, 6px) clamp(8px, 2vw, 12px);
    border-radius: 999px;
    letter-spacing: .03em;
    white-space: nowrap;
    max-width: 100%;
}}
.sfpms-badge .lbl {{ color: {GOLD_500}; text-transform: uppercase; font-size: .62rem; letter-spacing: .1em; margin-right: 6px; }}

/* ---- Sidebar ---- */
section[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, {NAVY_900} 0%, {NAVY_800} 100%);
    border-right: 1px solid {GOLD_600};
}}
section[data-testid="stSidebar"] * {{ color: #E7ECF5 !important; }}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {{ color: #FFFFFF !important; font-family:'Fraunces',serif !important; }}
.sfpms-sidebar-brand {{
    display:flex; align-items:center; gap:10px;
    padding: 4px 0 16px 0; margin-bottom: 12px;
    border-bottom: 1px solid rgba(199,164,95,.35);
    flex-wrap: wrap;
}}
.sfpms-sidebar-brand .name {{
    font-family:'Fraunces',serif; font-weight:600; color:#FFFFFF; font-size: clamp(.92rem, 2.4vw, 1.02rem); line-height:1.1;
}}
.sfpms-sidebar-brand .sub {{
    font-size:.66rem; letter-spacing:.14em; text-transform:uppercase; color:{GOLD_500}; font-weight:600;
}}
section[data-testid="stSidebar"] .stCaption, section[data-testid="stSidebar"] small {{ color:#9FB0C7 !important; }}

/* ---- Buttons ---- */
.stButton>button, .stDownloadButton>button {{
    background: {NAVY_900};
    color: #FFFFFF;
    border: 1px solid {NAVY_900};
    border-radius: 8px;
    font-weight: 600;
    letter-spacing: .01em;
    max-width: 100%;
}}
.stButton>button:hover, .stDownloadButton>button:hover {{
    background: {GOLD_600};
    border-color: {GOLD_600};
    color: {NAVY_900};
}}
button[kind="primary"] {{
    background: {GOLD_600} !important;
    border-color: {GOLD_600} !important;
    color: {NAVY_900} !important;
}}
button[kind="primary"]:hover {{
    background: {GOLD_500} !important;
    border-color: {GOLD_500} !important;
}}

/* ---- Tabs ---- */
.stTabs [data-baseweb="tab-list"] {{ gap: 4px; border-bottom: 1px solid {HAIRLINE}; overflow-x: auto; flex-wrap: nowrap; }}
.stTabs [data-baseweb="tab"] {{
    font-weight: 600; color: {SLATE_500}; font-size: clamp(.78rem, 1.6vw, .95rem); white-space: nowrap;
}}
.stTabs [aria-selected="true"] {{
    color: {NAVY_900} !important;
    border-bottom: 3px solid {GOLD_600} !important;
}}

/* ---- Dataframes / tables ---- */
[data-testid="stDataFrame"] {{
    border: 1px solid {HAIRLINE};
    border-radius: 10px;
    overflow-x: auto;
    max-width: 100%;
}}

/* ---- Dividers & panel cards ---- */
hr {{ border-top: 1px solid {HAIRLINE}; }}
.panel-card {{
    background:#FFFFFF;
    border:1px solid {HAIRLINE};
    border-left:5px solid {GOLD_600};
    border-radius:14px;
    padding: clamp(12px, 3vw, 16px) clamp(14px, 4vw, 20px);
    margin: 6px 0 18px 0;
    box-shadow:0 4px 14px rgba(15,35,68,.06);
    max-width: 100%;
    box-sizing: border-box;
    overflow-wrap: anywhere;
}}
.panel-card .section-title {{
    font-family:'Fraunces',serif;
    font-weight:600;
    font-size: clamp(.94rem, 2.6vw, 1.05rem);
    color:{NAVY_900};
    margin-bottom:6px;
}}
.panel-card p {{ color:{SLATE_700}; margin:.2rem 0; font-size: clamp(.82rem, 2vw, .95rem); }}

/* ---- Footer ---- */
.sfpms-footer {{
    margin-top: 34px;
    padding-top: 14px;
    border-top: 1px solid {HAIRLINE};
    display:flex; justify-content:space-between; flex-wrap:wrap; gap:8px;
    font-size: clamp(.64rem, 1.6vw, .72rem); color:{SLATE_500};
}}
.sfpms-footer .tag {{
    font-weight:700; letter-spacing:.08em; color:{NAVY_800}; text-transform:uppercase; font-size:.66rem;
}}

/* Streamlit metric widget (st.metric) restyle to match the design system */
[data-testid="stMetric"] {{
    background:#FFFFFF; border:1px solid {HAIRLINE}; border-left:5px solid {NAVY_800};
    border-radius:14px; padding: clamp(10px, 2.5vw, 12px) clamp(12px, 3vw, 16px); box-shadow:0 4px 14px rgba(15,35,68,.05);
    max-width: 100%; box-sizing: border-box;
}}
[data-testid="stMetricLabel"] {{ color:{SLATE_500} !important; font-weight:700; text-transform:uppercase; font-size: clamp(.64rem, 1.6vw, .72rem) !important; }}
[data-testid="stMetricValue"] {{ color:{NAVY_900} !important; font-family:'Fraunces',serif !important; font-size: clamp(1.1rem, 4vw, 1.6rem) !important; }}

/* ---- Global responsive scaffolding ---- */
.stApp, .main, .block-container {{
    max-width: 100%;
    overflow-x: hidden;
}}
.block-container {{
    padding-left: clamp(.75rem, 3vw, 3rem);
    padding-right: clamp(.75rem, 3vw, 3rem);
    padding-top: clamp(1rem, 3vw, 2rem);
}}
img, svg, iframe, [data-testid="stPlotlyChart"], [data-testid="stDataFrame"] {{
    max-width: 100%;
}}

@media (max-width: 640px) {{
    .sfpms-masthead {{ flex-direction: column; align-items: flex-start; }}
    .sfpms-masthead .badges {{ justify-content: flex-start; width: 100%; }}
    .sfpms-badge {{ flex: 1 1 auto; text-align: center; }}
    div[data-testid="column"] {{ width: 100% !important; flex: 1 1 100% !important; min-width: 100% !important; }}
    .stButton>button, .stDownloadButton>button {{ width: 100%; }}
}}

@media (max-width: 420px) {{
    .sfpms-masthead .org-text .tagline {{ display: none; }}
}}
</style>
"""


def inject_corporate_theme():
    st.markdown(CORPORATE_CSS, unsafe_allow_html=True)


CREST_SVG = """
<svg viewBox="0 0 46 46" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid meet">
  <polygon points="23,2 43,12 43,27 23,44 3,27 3,12" fill="#0B1F3A" stroke="#C7A45F" stroke-width="1.5"/>
  <polygon points="23,7 38,15 38,25 23,38 8,25 8,15" fill="none" stroke="#C7A45F" stroke-width="1"/>
  <text x="23" y="27" font-family="Fraunces, serif" font-size="13" font-weight="700" fill="#EDE6D8" text-anchor="middle">BIH</text>
</svg>
"""


def render_masthead(role, scenario_name):
    st.markdown(
        f"""
        <div class="sfpms-masthead">
            <div class="crest-block">
                <div class="sfpms-crest">{CREST_SVG}</div>
                <div class="org-text">
                    <div class="org-name">{ORG_NAME}</div>
                    <div class="system-name">{APP_TITLE}</div>
                    <div class="tagline">{ORG_TAGLINE}</div>
                </div>
            </div>
            <div class="badges">
                <span class="sfpms-badge"><span class="lbl">Role</span>{role}</span>
                <span class="sfpms-badge"><span class="lbl">Scenario</span>{scenario_name}</span>
                <span class="sfpms-badge"><span class="lbl">Cycle</span>2026 SFP Cycle</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_brand():
    st.markdown(
        f"""
        <div class="sfpms-sidebar-brand">
            <div class="sfpms-crest">{CREST_SVG}</div>
            <div>
                <div class="name">{ORG_NAME}</div>
                <div class="sub">SFPMS Console</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_footer(role):
    st.markdown(
        f"""
        <div class="sfpms-footer">
            <div><span class="tag">Classification:</span> Internal — Pilot / Research Use Only</div>
            <div><span class="tag">Signed in as:</span> {role}</div>
            <div><span class="tag">SFPMS</span> · BIH Solutions · Action Research Pilot Build</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

BASELINES = {
    "SFPE": 2.781,
    "FLQ": 2.700,
    "FIQ-Core": 2.705,
    "FRM": 2.733,
    "SM": 2.670,
    "RMC": 2.742,
}

CONSTRUCT_LABELS = {
    "SFPE": "Strategic Financial Planning Effectiveness (SFPE)",
    "FLQ": "Financial Leadership Quality (FLQ)",
    "FIQ-Core": "Financial Information Quality—Core (FIQ-Core)",
    "FRM": "Financial Risk Management (FRM)",
    "SM": "Stakeholder Management (SM)",
    "RMC": "Resource Management Capability (RMC)",
}

SCENARIOS = {
    "Main Scenario": {
        "revenue": 4200000,
        "operating_cost": 2600000,
        "net_cash_flow": 650000,
        "financing_need": 300000,
        "closing_cash": 1200000,
        "risk_exposure": 11,
        "resource_pressure": "Moderate",
        "forecast_accuracy": 78,
        "budget_variance": -6.42,
        "completion": 62,
        "critical_risks": 5,
        "pending_approvals": 8,
        "recommendation": "Proceed with the approved baseline plan while monitoring cash flow, data quality and resource readiness.",
    },
    "Optimistic Scenario": {
        "revenue": 4800000,
        "operating_cost": 2450000,
        "net_cash_flow": 1100000,
        "financing_need": 0,
        "closing_cash": 1700000,
        "risk_exposure": 7,
        "resource_pressure": "Low",
        "forecast_accuracy": 86,
        "budget_variance": -2.10,
        "completion": 68,
        "critical_risks": 3,
        "pending_approvals": 6,
        "recommendation": "Accelerate priority investments and preserve contingency reserves while validating the stronger revenue assumptions.",
    },
    "Pessimistic Scenario": {
        "revenue": 3400000,
        "operating_cost": 2850000,
        "net_cash_flow": -250000,
        "financing_need": 1200000,
        "closing_cash": 500000,
        "risk_exposure": 17,
        "resource_pressure": "High",
        "forecast_accuracy": 64,
        "budget_variance": 8.75,
        "completion": 54,
        "critical_risks": 8,
        "pending_approvals": 11,
        "recommendation": "Activate contingency funding, defer non-critical expenditure, reassess resource allocations and escalate liquidity risks.",
    },
}

SCENARIO_ALLOWED_ROLES = {
    "CEO/Managing Director": "authorize",
    "SFPMS Process Owner": "coordinate",
    "SFP Committee Member": "recommend",
    "Finance Manager": "edit",
    "Department Manager": "view",
    "Budget Owner": "view",
    "Risk/Internal Control Officer": "assess",
    "Internal Auditor/Reviewer": "read_only",
    "Key Stakeholder": "summary",
    "System Administrator": "technical_only",
}

def init_scenario_state():
    if "selected_scenario" not in st.session_state:
        st.session_state.selected_scenario = "Main Scenario"

def scenario_selector(role, compact=False):
    init_scenario_state()
    access = SCENARIO_ALLOWED_ROLES.get(role, "view")
    label = "Planning Scenario"
    selected = st.selectbox(
        label,
        list(SCENARIOS.keys()),
        index=list(SCENARIOS.keys()).index(st.session_state.selected_scenario),
        key=f"scenario_selector_{role}_{'compact' if compact else 'full'}",
    )
    st.session_state.selected_scenario = selected
    if not compact:
        access_text = {
            "authorize": "You may compare and authorize the selected scenario.",
            "coordinate": "You may compare all scenarios and coordinate the scenario workflow.",
            "recommend": "You may compare scenarios and make a recommendation.",
            "edit": "You may analyse and revise scenario assumptions.",
            "view": "You may view the implications relevant to your role.",
            "assess": "You may assess scenario-specific risks and controls.",
            "read_only": "Read-only scenario review.",
            "summary": "Authorized scenario summary only.",
            "technical_only": "Technical access only; no financial decision authority.",
        }.get(access, "")
        st.caption(access_text)
    return st.session_state.selected_scenario

def current_scenario():
    init_scenario_state()
    return SCENARIOS[st.session_state.selected_scenario]

def scenario_status_tone(value):
    if value in ("Low", "Good", "Favourable"):
        return "green"
    if value in ("Moderate", "Watch", "At Risk"):
        return "orange"
    if value in ("High", "Critical", "Unfavourable"):
        return "red"
    return "blue"

def scenario_adjusted_budgets(base_df, scenario_name):
    multipliers = {
        "Optimistic Scenario": {"budget": 1.04, "actual": 0.96, "committed": 0.95},
        "Main Scenario": {"budget": 1.00, "actual": 1.00, "committed": 1.00},
        "Pessimistic Scenario": {"budget": 0.93, "actual": 1.08, "committed": 1.05},
    }[scenario_name]
    df = base_df.copy()
    for col, mult in multipliers.items():
        df[col] = df[col] * mult
    return df

def scenario_adjusted_risks(base_df, scenario_name):
    delta = {"Optimistic Scenario": -1, "Main Scenario": 0, "Pessimistic Scenario": 1}[scenario_name]
    df = base_df.copy()
    df["likelihood"] = (df["likelihood"] + delta).clip(1, 5)
    df["impact"] = (df["impact"] + (1 if scenario_name == "Pessimistic Scenario" else 0)).clip(1, 5)
    df["score"] = df["likelihood"] * df["impact"]
    return df

ROLES = [
    "CEO/Managing Director",
    "SFPMS Process Owner",
    "SFP Committee Member",
    "Finance Manager",
    "Department Manager",
    "Budget Owner",
    "Risk/Internal Control Officer",
    "Internal Auditor/Reviewer",
    "Key Stakeholder",
    "System Administrator",
]

ROLE_PAGES = {
    "CEO/Managing Director": ["Executive Dashboard", "Planning & Decisions", "Financial Performance", "Risks & Controls", "Evaluation & Learning"],
    "SFPMS Process Owner": ["Control Centre", "Planning & Decisions", "Financial Performance", "Risks & Controls", "Stakeholders & Resources", "Evaluation & Learning"],
    "SFP Committee Member": ["Planning & Decisions", "Financial Performance", "Risks & Controls", "Stakeholders & Resources", "Evaluation & Learning"],
    "Finance Manager": ["Finance Dashboard", "Planning & Decisions", "Financial Performance", "Data Quality", "Evaluation & Learning"],
    "Department Manager": ["Department Dashboard", "My Tasks", "Budgets", "Resources", "Risks"],
    "Budget Owner": ["My Budget & Actions", "My Tasks", "Resources"],
    "Risk/Internal Control Officer": ["Risk & Control Dashboard", "Planning & Decisions", "Data Quality"],
    "Internal Auditor/Reviewer": ["Audit & Assurance", "Planning & Decisions", "Data Quality", "Evaluation & Learning"],
    "Key Stakeholder": ["Consultation & Feedback"],
    "System Administrator": ["System Administration"],
}



def page_header(title, subtitle):
    st.markdown(f"# {title}")
    st.caption(subtitle)

def metric_card(label, value, note="", tone="blue"):
    tones = {
        "blue": NAVY_800,
        "green": STATUS_GREEN,
        "orange": STATUS_ORANGE,
        "red": STATUS_RED,
        "purple": GOLD_600,
        "muted": SLATE_500,
    }
    accent = tones.get(tone, tones["blue"])
    st.markdown(
        f"""
        <div style="
            background:#FFFFFF;
            border:1px solid {HAIRLINE};
            border-left:5px solid {accent};
            border-radius:14px;
            padding:14px 16px;
            min-height:112px;
            box-shadow:0 4px 14px rgba(15,35,68,.06);
        ">
            <div style="font-size:.74rem;color:{SLATE_500};font-weight:700;text-transform:uppercase;letter-spacing:.03em;">
                {label}
            </div>
            <div style="font-family:'Fraunces',serif;font-size:1.55rem;color:{NAVY_900};font-weight:700;margin:.28rem 0;">
                {value}
            </div>
            <div style="font-size:.76rem;color:{accent};font-weight:600;">
                {note}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def panel_title(title, eyebrow=None):
    if eyebrow:
        st.markdown(
            f"<div style='font-size:.72rem;color:{GOLD_600};font-weight:800;"
            f"text-transform:uppercase;letter-spacing:.1em'>{eyebrow}</div>",
            unsafe_allow_html=True,
        )
    st.markdown(f"### {title}")

def style_plotly(fig, height=360):
    fig.update_layout(
        height=height,
        margin=dict(l=20, r=20, t=55, b=20),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(color=SLATE_700, family="IBM Plex Sans, sans-serif"),
        title_font=dict(family="Fraunces, serif", color=NAVY_900, size=17),
        legend_title_text="",
        colorway=[NAVY_800, GOLD_600, STATUS_GREEN, STATUS_ORANGE, STATUS_RED, "#6E86A6"],
    )
    fig.update_xaxes(showgrid=False, linecolor=HAIRLINE)
    fig.update_yaxes(gridcolor="#E9EEF5", zeroline=False, linecolor=HAIRLINE)
    return fig

def show_capability_cards():
    items = list(BASELINES.items())
    for start in range(0, len(items), 3):
        cols = st.columns(3)
        for idx, (code, score) in enumerate(items[start:start + 3]):
            with cols[idx]:
                metric_card(
                    CONSTRUCT_LABELS[code],
                    f"{score:.3f}",
                    "Research baseline score",
                    "purple" if code == "SFPE" else "blue",
                )

def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS planning_cycles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        start_date TEXT,
        end_date TEXT,
        phase TEXT,
        status TEXT,
        owner TEXT
    );
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        owner_role TEXT,
        due_date TEXT,
        status TEXT,
        priority TEXT,
        cycle_id INTEGER
    );
    CREATE TABLE IF NOT EXISTS budgets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        department TEXT,
        category TEXT,
        budget REAL,
        actual REAL,
        committed REAL,
        owner TEXT,
        period TEXT
    );
    CREATE TABLE IF NOT EXISTS risks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        category TEXT,
        likelihood INTEGER,
        impact INTEGER,
        owner TEXT,
        mitigation TEXT,
        status TEXT,
        due_date TEXT
    );
    CREATE TABLE IF NOT EXISTS stakeholders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        category TEXT,
        influence TEXT,
        interest TEXT,
        expectation TEXT,
        status TEXT
    );
    CREATE TABLE IF NOT EXISTS resources (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        department TEXT,
        resource_type TEXT,
        available REAL,
        required REAL,
        allocated REAL,
        owner TEXT
    );
    CREATE TABLE IF NOT EXISTS approvals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        gate_name TEXT,
        owner_role TEXT,
        status TEXT,
        evidence_complete INTEGER,
        comments TEXT
    );
    CREATE TABLE IF NOT EXISTS assessments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cycle_label TEXT,
        construct TEXT,
        score REAL,
        assessment_date TEXT
    );
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        stakeholder TEXT,
        subject TEXT,
        feedback_text TEXT,
        response TEXT,
        status TEXT
    );
    """)

    if cur.execute("SELECT COUNT(*) FROM planning_cycles").fetchone()[0] == 0:
        cur.execute("INSERT INTO planning_cycles(name,start_date,end_date,phase,status,owner) VALUES(?,?,?,?,?,?)",
                    ("2026 Strategic Financial Planning Cycle", "2026-01-01", "2026-12-31", "Analyse & Develop Options", "Active", "SFPMS Process Owner"))
    cycle_id = cur.execute("SELECT id FROM planning_cycles LIMIT 1").fetchone()[0]

    if cur.execute("SELECT COUNT(*) FROM tasks").fetchone()[0] == 0:
        cur.executemany("INSERT INTO tasks(title,owner_role,due_date,status,priority,cycle_id) VALUES(?,?,?,?,?,?)", [
            ("Validate 2025 closing balances", "Finance Manager", "2026-07-25", "In Progress", "High", cycle_id),
            ("Review strategic assumptions", "SFP Committee Member", "2026-07-28", "Pending", "High", cycle_id),
            ("Update liquidity risk response", "Risk/Internal Control Officer", "2026-07-23", "Overdue", "Critical", cycle_id),
            ("Submit departmental resource needs", "Department Manager", "2026-07-30", "Pending", "Medium", cycle_id),
            ("Approve scenario baseline", "CEO/Managing Director", "2026-08-02", "Pending", "High", cycle_id),
        ])

    if cur.execute("SELECT COUNT(*) FROM budgets").fetchone()[0] == 0:
        cur.executemany("INSERT INTO budgets(department,category,budget,actual,committed,owner,period) VALUES(?,?,?,?,?,?,?)", [
            ("Finance", "Operations", 1200000, 980000, 100000, "Finance Manager", "2026"),
            ("Operations", "Operations", 1800000, 1650000, 80000, "Department Manager", "2026"),
            ("IT", "Capital", 1500000, 900000, 400000, "Department Manager", "2026"),
            ("Marketing", "Operations", 800000, 620000, 90000, "Budget Owner", "2026"),
        ])

    if cur.execute("SELECT COUNT(*) FROM risks").fetchone()[0] == 0:
        cur.executemany("INSERT INTO risks(title,category,likelihood,impact,owner,mitigation,status,due_date) VALUES(?,?,?,?,?,?,?,?)", [
            ("Cash-flow shortfall", "Liquidity", 4, 5, "Risk/Internal Control Officer", "Weekly cash forecast and contingency funding", "Open", "2026-07-24"),
            ("Data inconsistency", "Information", 3, 4, "Finance Manager", "Reconcile source reports and lock approved version", "Open", "2026-07-26"),
            ("Delayed stakeholder approval", "Stakeholder", 3, 3, "SFPMS Process Owner", "Escalation and consultation plan", "Monitoring", "2026-07-31"),
            ("Resource over-allocation", "Resource", 4, 3, "Department Manager", "Reallocation and prioritisation", "Open", "2026-08-01"),
        ])

    if cur.execute("SELECT COUNT(*) FROM stakeholders").fetchone()[0] == 0:
        cur.executemany("INSERT INTO stakeholders(name,category,influence,interest,expectation,status) VALUES(?,?,?,?,?,?)", [
            ("Employees", "Internal", "Medium", "High", "Clear priorities and realistic workload", "Consultation Open"),
            ("Partners", "External", "High", "High", "Reliable forecasts and timely decisions", "Consulted"),
            ("Suppliers", "External", "Medium", "Medium", "Predictable payment and procurement plans", "Pending"),
            ("Management Team", "Internal", "High", "High", "Strategic alignment and financial visibility", "Consulted"),
        ])

    if cur.execute("SELECT COUNT(*) FROM resources").fetchone()[0] == 0:
        cur.executemany("INSERT INTO resources(department,resource_type,available,required,allocated,owner) VALUES(?,?,?,?,?,?)", [
            ("Finance", "Human", 5, 7, 5, "Finance Manager"),
            ("Operations", "Human", 12, 14, 12, "Department Manager"),
            ("IT", "Technology", 8, 10, 7, "Department Manager"),
            ("Corporate", "Financial", 5000000, 6200000, 4800000, "CEO/Managing Director"),
        ])

    if cur.execute("SELECT COUNT(*) FROM approvals").fetchone()[0] == 0:
        cur.executemany("INSERT INTO approvals(gate_name,owner_role,status,evidence_complete,comments) VALUES(?,?,?,?,?)", [
            ("G1 Strategic Fit", "SFP Committee Member", "Approved", 100, "Aligned with 2026 priorities"),
            ("G2 Information Valid", "Finance Manager", "In Review", 80, "Cash reconciliation pending"),
            ("G3 Financially Feasible", "Finance Manager", "Pending", 60, "Scenario review required"),
            ("G4 Risk Acceptable", "Risk/Internal Control Officer", "Pending", 50, "Liquidity risk above tolerance"),
            ("G5 Stakeholders & Resources Ready", "SFPMS Process Owner", "Pending", 40, "Consultation incomplete"),
            ("G6 Authorized", "CEO/Managing Director", "Not Started", 0, ""),
        ])

    if cur.execute("SELECT COUNT(*) FROM assessments").fetchone()[0] == 0:
        cur.executemany("INSERT INTO assessments(cycle_label,construct,score,assessment_date) VALUES(?,?,?,?)",
                        [("Baseline", k, v, "2026-07-01") for k, v in BASELINES.items()])

    conn.commit()
    conn.close()


def load_df(query, params=None):
    conn = get_conn()
    df = pd.read_sql_query(query, conn, params=params or [])
    conn.close()
    return df



UPLOAD_DATASETS = {
    "Research Baseline": {
        "required": ["construct", "score"],
        "optional": ["full_construct_name", "cycle_label", "assessment_date", "data_classification"],
        "target_table": "assessments",
        "allowed_roles": ["SFPMS Process Owner", "Internal Auditor/Reviewer"],
    },
    "Budgets": {
        "required": ["department", "budget", "actual"],
        "optional": ["category", "committed", "owner", "period"],
        "target_table": "budgets",
        "allowed_roles": ["Finance Manager", "Department Manager"],
    },
    "Risks": {
        "required": ["title", "category", "likelihood", "impact"],
        "optional": ["owner", "mitigation", "status", "due_date"],
        "target_table": "risks",
        "allowed_roles": ["Risk/Internal Control Officer", "SFPMS Process Owner"],
    },
    "Stakeholders": {
        "required": ["name", "category"],
        "optional": ["influence", "interest", "expectation", "status"],
        "target_table": "stakeholders",
        "allowed_roles": ["SFPMS Process Owner", "Key Stakeholder"],
    },
    "Resources": {
        "required": ["department", "resource_type", "available", "required"],
        "optional": ["allocated", "owner"],
        "target_table": "resources",
        "allowed_roles": ["Department Manager", "SFPMS Process Owner"],
    },
    "Workflow Tasks": {
        "required": ["title", "owner_role", "status"],
        "optional": ["due_date", "priority", "cycle_id"],
        "target_table": "tasks",
        "allowed_roles": ["SFPMS Process Owner"],
    },
    "Decision Gates": {
        "required": ["gate_name", "owner_role", "status"],
        "optional": ["evidence_complete", "comments"],
        "target_table": "approvals",
        "allowed_roles": ["SFPMS Process Owner", "Finance Manager", "Risk/Internal Control Officer"],
    },
    "Post-Intervention Assessments": {
        "required": ["cycle_label", "construct", "score"],
        "optional": ["assessment_date"],
        "target_table": "assessments",
        "allowed_roles": ["SFPMS Process Owner", "Internal Auditor/Reviewer"],
    },
}

COLUMN_ALIASES = {
    "approved budget": "budget",
    "approved_budget": "budget",
    "actual expenditure": "actual",
    "amount spent": "actual",
    "committed expenditure": "committed",
    "budget holder": "owner",
    "financial year": "period",
    "risk title": "title",
    "risk category": "category",
    "stakeholder group": "name",
    "resource type": "resource_type",
    "required main": "required",
    "required_main": "required",
    "available quantity": "available",
    "assigned role": "owner_role",
    "activity": "title",
    "decision gate": "gate_name",
    "evidence complete": "evidence_complete",
    "evidence complete pct": "evidence_complete",
    "baseline score": "score",
    "post intervention score": "score",
    "construct code": "construct",
}

def normalize_column_name(name):
    cleaned = str(name).strip().lower()
    cleaned = cleaned.replace("—", " ").replace("-", " ").replace("/", " ")
    cleaned = re.sub(r"[^a-z0-9]+", "_", cleaned).strip("_")
    alias_key = cleaned.replace("_", " ")
    return COLUMN_ALIASES.get(alias_key, COLUMN_ALIASES.get(cleaned, cleaned))

def read_uploaded_table(uploaded_file):
    suffix = Path(uploaded_file.name).suffix.lower()
    raw = uploaded_file.getvalue()
    if suffix == ".csv":
        return pd.read_csv(BytesIO(raw))
    if suffix == ".xlsx":
        workbook = pd.ExcelFile(BytesIO(raw), engine="openpyxl")
        if len(workbook.sheet_names) == 1:
            return workbook.parse(workbook.sheet_names[0])
        return {sheet: workbook.parse(sheet) for sheet in workbook.sheet_names}
    if suffix == ".txt":
        decoded = raw.decode("utf-8-sig", errors="replace")
        try:
            return pd.read_csv(StringIO(decoded), sep=None, engine="python")
        except Exception:
            lines = [line.strip() for line in decoded.splitlines() if line.strip()]
            return pd.DataFrame({"text": lines})
    raise ValueError("Unsupported file type. Use CSV, XLSX, or TXT.")

def standardize_dataframe(df):
    cleaned = df.copy()
    cleaned.columns = [normalize_column_name(col) for col in cleaned.columns]
    cleaned = cleaned.dropna(how="all")
    cleaned = cleaned.loc[:, ~cleaned.columns.duplicated()]
    return cleaned

def validate_uploaded_dataframe(df, dataset_name):
    config = UPLOAD_DATASETS[dataset_name]
    required = config["required"]
    report = []
    missing_columns = [col for col in required if col not in df.columns]
    report.append({
        "Check": "Required columns",
        "Status": "Passed" if not missing_columns else "Failed",
        "Details": "All required columns present" if not missing_columns else f"Missing: {', '.join(missing_columns)}",
    })

    duplicate_count = int(df.duplicated().sum())
    report.append({
        "Check": "Duplicate rows",
        "Status": "Passed" if duplicate_count == 0 else "Warning",
        "Details": f"{duplicate_count} duplicate row(s)",
    })

    if missing_columns:
        missing_required_values = None
    else:
        missing_required_values = int(df[required].isna().sum().sum())
    report.append({
        "Check": "Missing required values",
        "Status": "Not evaluated" if missing_required_values is None else ("Passed" if missing_required_values == 0 else "Failed"),
        "Details": "Required columns missing" if missing_required_values is None else str(missing_required_values),
    })

    numeric_requirements = {
        "Budgets": ["budget", "actual", "committed"],
        "Risks": ["likelihood", "impact"],
        "Resources": ["available", "required", "allocated"],
        "Research Baseline": ["score"],
        "Post-Intervention Assessments": ["score"],
        "Decision Gates": ["evidence_complete"],
    }.get(dataset_name, [])

    invalid_numeric = 0
    for col in numeric_requirements:
        if col in df.columns:
            converted = pd.to_numeric(df[col], errors="coerce")
            invalid_numeric += int((converted.isna() & df[col].notna()).sum())
    report.append({
        "Check": "Numeric fields",
        "Status": "Passed" if invalid_numeric == 0 else "Failed",
        "Details": f"{invalid_numeric} invalid numeric value(s)",
    })

    invalid_ranges = 0
    if dataset_name == "Risks":
        for col in ["likelihood", "impact"]:
            if col in df.columns:
                values = pd.to_numeric(df[col], errors="coerce")
                invalid_ranges += int(((values < 1) | (values > 5)).sum())
    if dataset_name in ["Research Baseline", "Post-Intervention Assessments"] and "score" in df.columns:
        values = pd.to_numeric(df["score"], errors="coerce")
        invalid_ranges += int(((values < 1) | (values > 5)).sum())
    if dataset_name == "Decision Gates" and "evidence_complete" in df.columns:
        values = pd.to_numeric(df["evidence_complete"], errors="coerce")
        invalid_ranges += int(((values < 0) | (values > 100)).sum())

    report.append({
        "Check": "Allowed ranges",
        "Status": "Passed" if invalid_ranges == 0 else "Failed",
        "Details": f"{invalid_ranges} out-of-range value(s)",
    })
    ready = all(item["Status"] not in ["Failed", "Not evaluated"] for item in report)
    return pd.DataFrame(report), ready

def ensure_import_tables():
    conn = get_conn()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS import_batches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        batch_id TEXT NOT NULL UNIQUE,
        filename TEXT NOT NULL,
        file_type TEXT,
        dataset_name TEXT NOT NULL,
        target_table TEXT,
        rows_received INTEGER DEFAULT 0,
        rows_imported INTEGER DEFAULT 0,
        rows_rejected INTEGER DEFAULT 0,
        uploaded_by TEXT,
        uploaded_at TEXT,
        status TEXT,
        file_hash TEXT,
        notes TEXT
    );
    CREATE TABLE IF NOT EXISTS import_rejections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        batch_id TEXT NOT NULL,
        row_number INTEGER,
        reason TEXT,
        row_data TEXT
    );
    """)
    conn.commit()
    conn.close()

def dataframe_to_records(df):
    clean = df.where(pd.notna(df), None)
    return clean.to_dict(orient="records")

def import_dataframe(df, dataset_name, role, filename):
    config = UPLOAD_DATASETS[dataset_name]
    table = config["target_table"]
    batch_id = f"IMP-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    file_hash = hashlib.sha256(df.to_csv(index=False).encode("utf-8")).hexdigest()
    imported = 0
    rejected = 0
    rejections = []
    conn = get_conn()
    try:
        for idx, record in enumerate(dataframe_to_records(df), start=2):
            try:
                if table == "assessments":
                    conn.execute(
                        "INSERT INTO assessments(cycle_label,construct,score,assessment_date) VALUES(?,?,?,?)",
                        (
                            record.get("cycle_label") or ("Baseline" if dataset_name == "Research Baseline" else "Cycle 1"),
                            record.get("construct"),
                            float(record.get("score")),
                            str(record.get("assessment_date") or date.today()),
                        ),
                    )
                elif table == "budgets":
                    conn.execute(
                        "INSERT INTO budgets(department,category,budget,actual,committed,owner,period) VALUES(?,?,?,?,?,?,?)",
                        (
                            record.get("department"),
                            record.get("category") or "Unclassified",
                            float(record.get("budget") or 0),
                            float(record.get("actual") or 0),
                            float(record.get("committed") or 0),
                            record.get("owner") or role,
                            str(record.get("period") or date.today().year),
                        ),
                    )
                elif table == "risks":
                    conn.execute(
                        "INSERT INTO risks(title,category,likelihood,impact,owner,mitigation,status,due_date) VALUES(?,?,?,?,?,?,?,?)",
                        (
                            record.get("title"),
                            record.get("category"),
                            int(float(record.get("likelihood"))),
                            int(float(record.get("impact"))),
                            record.get("owner") or role,
                            record.get("mitigation") or "",
                            record.get("status") or "Open",
                            str(record.get("due_date") or ""),
                        ),
                    )
                elif table == "stakeholders":
                    conn.execute(
                        "INSERT INTO stakeholders(name,category,influence,interest,expectation,status) VALUES(?,?,?,?,?,?)",
                        (
                            record.get("name"),
                            record.get("category"),
                            record.get("influence") or "Medium",
                            record.get("interest") or "Medium",
                            record.get("expectation") or "",
                            record.get("status") or "Pending",
                        ),
                    )
                elif table == "resources":
                    conn.execute(
                        "INSERT INTO resources(department,resource_type,available,required,allocated,owner) VALUES(?,?,?,?,?,?)",
                        (
                            record.get("department"),
                            record.get("resource_type"),
                            float(record.get("available") or 0),
                            float(record.get("required") or 0),
                            float(record.get("allocated") or 0),
                            record.get("owner") or role,
                        ),
                    )
                elif table == "tasks":
                    conn.execute(
                        "INSERT INTO tasks(title,owner_role,due_date,status,priority,cycle_id) VALUES(?,?,?,?,?,?)",
                        (
                            record.get("title"),
                            record.get("owner_role"),
                            str(record.get("due_date") or ""),
                            record.get("status") or "Pending",
                            record.get("priority") or "Medium",
                            int(record.get("cycle_id") or 1),
                        ),
                    )
                elif table == "approvals":
                    conn.execute(
                        "INSERT INTO approvals(gate_name,owner_role,status,evidence_complete,comments) VALUES(?,?,?,?,?)",
                        (
                            record.get("gate_name"),
                            record.get("owner_role"),
                            record.get("status") or "Pending",
                            int(float(record.get("evidence_complete") or 0)),
                            record.get("comments") or "",
                        ),
                    )
                imported += 1
            except Exception as row_error:
                rejected += 1
                rejections.append((batch_id, idx, str(row_error), json.dumps(record, default=str)))

        conn.execute(
            """
            INSERT INTO import_batches(
                batch_id,filename,file_type,dataset_name,target_table,
                rows_received,rows_imported,rows_rejected,uploaded_by,
                uploaded_at,status,file_hash,notes
            ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                batch_id, filename, Path(filename).suffix.lower(), dataset_name, table,
                len(df), imported, rejected, role, datetime.now().isoformat(timespec="seconds"),
                "Completed" if rejected == 0 else "Completed with Rejections",
                file_hash, "Validated through SFPMS Data Import Centre"
            ),
        )
        if rejections:
            conn.executemany(
                "INSERT INTO import_rejections(batch_id,row_number,reason,row_data) VALUES(?,?,?,?)",
                rejections,
            )
        conn.commit()
    finally:
        conn.close()
    return {"batch_id": batch_id, "received": len(df), "imported": imported, "rejected": rejected}

def data_import_centre(role):
    st.header("Data Import Centre")
    st.caption("Upload, preview, validate, map and import cleaned CSV, XLSX or TXT files into the SFPMS.")
    ensure_import_tables()

    dataset_name = st.selectbox("Destination dataset", list(UPLOAD_DATASETS.keys()))
    allowed_roles = UPLOAD_DATASETS[dataset_name]["allowed_roles"]
    authorized = role in allowed_roles or role == "CEO/Managing Director"

    if not authorized:
        st.warning(f"Read-only access. Authorized upload roles: {', '.join(allowed_roles)}.")

    uploaded_file = st.file_uploader(
        "Upload cleaned data file",
        type=["csv", "xlsx", "txt"],
        accept_multiple_files=False,
        help="Accepted formats: CSV, XLSX and TXT.",
    )

    if uploaded_file is not None:
        try:
            parsed = read_uploaded_table(uploaded_file)
            if isinstance(parsed, dict):
                sheet_name = st.selectbox("Select Excel worksheet", list(parsed.keys()))
                raw_df = parsed[sheet_name]
            else:
                raw_df = parsed

            df = standardize_dataframe(raw_df)
            tabs = st.tabs(["1. Preview", "2. Validation", "3. Column Mapping", "4. Import", "5. Import History"])

            with tabs[0]:
                st.write(f"**Filename:** {uploaded_file.name}")
                st.write(f"**Rows:** {len(df):,} · **Columns:** {len(df.columns):,}")
                st.dataframe(df.head(100), use_container_width=True, hide_index=True)

            validation_report, ready = validate_uploaded_dataframe(df, dataset_name)

            with tabs[1]:
                st.dataframe(validation_report, use_container_width=True, hide_index=True)
                st.success("The file passed mandatory validation checks.") if ready else st.error("Correct failed checks before import.")

            with tabs[2]:
                config = UPLOAD_DATASETS[dataset_name]
                mapping = []
                for col in df.columns:
                    if col in config["required"]:
                        status = "Required field matched"
                    elif col in config["optional"]:
                        status = "Optional field matched"
                    else:
                        status = "Not used by current importer"
                    mapping.append({"Uploaded/normalized column": col, "Mapping status": status})
                st.dataframe(pd.DataFrame(mapping), use_container_width=True, hide_index=True)

            with tabs[3]:
                st.write(f"**Target table:** `{UPLOAD_DATASETS[dataset_name]['target_table']}`")
                acknowledgement = st.checkbox("I confirm that the data classification and source have been reviewed.")
                if st.button("Approve and Import", type="primary", disabled=not (authorized and ready and acknowledgement)):
                    result = import_dataframe(df, dataset_name, role, uploaded_file.name)
                    st.success(
                        f"Batch {result['batch_id']} completed: "
                        f"{result['imported']} imported and {result['rejected']} rejected."
                    )

            with tabs[4]:
                history = load_df(
                    "SELECT batch_id,filename,dataset_name,target_table,rows_received,"
                    "rows_imported,rows_rejected,uploaded_by,uploaded_at,status "
                    "FROM import_batches ORDER BY id DESC"
                )
                st.dataframe(history, use_container_width=True, hide_index=True)
        except Exception as error:
            st.error(f"Could not process the uploaded file: {error}")
    else:
        history = load_df(
            "SELECT batch_id,filename,dataset_name,target_table,rows_received,"
            "rows_imported,rows_rejected,uploaded_by,uploaded_at,status "
            "FROM import_batches ORDER BY id DESC"
        )
        if not history.empty:
            st.subheader("Recent Import History")
            st.dataframe(history, use_container_width=True, hide_index=True)

def capability_cards():
    cols = st.columns(6)
    for idx, (name, score) in enumerate(BASELINES.items()):
        cols[idx].metric(name, f"{score:.3f}", "Baseline")


def executive_dashboard():
    scenario_name = st.session_state.selected_scenario
    scenario = current_scenario()
    page_header(
        "Executive Strategic Dashboard",
        f"Enterprise overview of strategic financial planning performance under the {scenario_name}."
    )

    tasks = load_df("SELECT * FROM tasks")
    risks = load_df("SELECT * FROM risks")
    budgets = scenario_adjusted_budgets(load_df("SELECT * FROM budgets"), scenario_name)
    approvals = load_df("SELECT * FROM approvals")
    risks = scenario_adjusted_risks(risks, scenario_name)

    budget_total = budgets["budget"].sum()
    actual_total = budgets["actual"].sum()
    variance_pct = ((actual_total - budget_total) / budget_total * 100) if budget_total else 0

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        metric_card("Planning Scenario", scenario_name.replace(" Scenario", ""), "Active scenario", "blue")
    with c2:
        metric_card("Overall Completion", f"{scenario['completion']}%", "Scenario-adjusted progress", "green")
    with c3:
        metric_card("Pending Approvals", scenario["pending_approvals"], "Requires attention", "orange")
    with c4:
        metric_card("Critical Risks", scenario["critical_risks"], "Scenario-adjusted", "red")
    with c5:
        metric_card(
            "Strategic Financial Planning Effectiveness (SFPE)",
            f"{BASELINES['SFPE']:.3f}",
            "Research baseline score",
            "purple",
        )

    panel_title("Scenario Financial Summary", "Dynamic Analytics")
    s1, s2, s3, s4, s5 = st.columns(5)
    with s1:
        metric_card("Revenue", f"{scenario['revenue']:,.0f}", "Projected", "blue")
    with s2:
        metric_card("Operating Cost", f"{scenario['operating_cost']:,.0f}", "Projected", "orange")
    with s3:
        tone = "green" if scenario["net_cash_flow"] >= 0 else "red"
        metric_card("Net Cash Flow", f"{scenario['net_cash_flow']:,.0f}", "Projected", tone)
    with s4:
        tone = "green" if scenario["financing_need"] == 0 else "red"
        metric_card("Financing Need", f"{scenario['financing_need']:,.0f}", "Projected", tone)
    with s5:
        metric_card("Closing Cash", f"{scenario['closing_cash']:,.0f}", "Projected", "purple")

    panel_title("Research Baseline Scores", "Pre-Implementation")
    show_capability_cards()

    left, right = st.columns(2)
    with left:
        summary = budgets.groupby("department", as_index=False)[["budget", "actual"]].sum()
        fig = px.bar(
            summary,
            x="department",
            y=["budget", "actual"],
            barmode="group",
            title=f"Budget vs Actual by Department — {scenario_name}",
        )
        st.plotly_chart(style_plotly(fig), use_container_width=True)

    with right:
        risk_summary = risks.groupby("category", as_index=False)["score"].max()
        fig = px.bar(
            risk_summary,
            x="category",
            y="score",
            title=f"Maximum Risk Score by Category — {scenario_name}",
        )
        st.plotly_chart(style_plotly(fig), use_container_width=True)

    st.subheader("Scenario Recommendation")
    tone = scenario_status_tone(
        "High" if scenario["risk_exposure"] >= 15 else "Moderate" if scenario["risk_exposure"] >= 10 else "Low"
    )
    st.markdown(
        f"""
        <div class="panel-card">
            <div class="section-title">{scenario_name}</div>
            <p><strong>Risk exposure:</strong> {scenario['risk_exposure']} ·
            <strong>Resource pressure:</strong> {scenario['resource_pressure']} ·
            <strong>Forecast accuracy:</strong> {scenario['forecast_accuracy']}%</p>
            <p>{scenario['recommendation']}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("Decisions Requiring Attention")
    st.dataframe(
        approvals[approvals["status"] != "Approved"],
        use_container_width=True,
        hide_index=True,
    )

def control_centre():
    page_header("SFPMS Process Owner Dashboard", f"Monitor workflow, gates and adoption under the {st.session_state.selected_scenario}.")
    cycles = load_df("SELECT * FROM planning_cycles")
    tasks = load_df("SELECT * FROM tasks")
    approvals = load_df("SELECT * FROM approvals")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Active Cycles", int((cycles["status"] == "Active").sum()))
    c2.metric("Open Tasks", int((tasks["status"] != "Complete").sum()))
    c3.metric("Overdue Tasks", int((tasks["status"] == "Overdue").sum()))
    c4.metric("Gates Approved", int((approvals["status"] == "Approved").sum()))
    st.dataframe(cycles, use_container_width=True, hide_index=True)
    st.dataframe(tasks, use_container_width=True, hide_index=True)
    st.plotly_chart(px.bar(approvals, x="gate_name", y="evidence_complete", color="status", title="Decision-Gate Readiness"), use_container_width=True)


def planning_decisions():
    scenario_name = st.session_state.selected_scenario
    scenario = current_scenario()
    page_header(
        "Planning and Decision Dashboard",
        f"Planning phases, gate readiness and approvals under the {scenario_name}."
    )

    readiness_shift = {
        "Optimistic Scenario": 10,
        "Main Scenario": 0,
        "Pessimistic Scenario": -15,
    }[scenario_name]

    approvals = load_df("SELECT * FROM approvals")
    approvals["evidence_complete"] = (approvals["evidence_complete"] + readiness_shift).clip(0, 100)

    phases = pd.DataFrame({
        "Phase": ["Initiate & Plan", "Analyse & Develop Options", "Plan & Approve", "Execute & Monitor", "Review & Adapt"],
        "Completion": [
            min(100, max(0, value + readiness_shift))
            for value in [100, 75, 40, 10, 0]
        ],
        "Status": ["Complete", "In Progress", "Pending", "Pending", "Pending"],
    })

    c1, c2, c3 = st.columns(3)
    with c1:
        metric_card("Scenario", scenario_name.replace(" Scenario", ""), "Current planning basis", "blue")
    with c2:
        metric_card("Completion", f"{scenario['completion']}%", "Scenario-adjusted", "green")
    with c3:
        metric_card("Pending Approvals", scenario["pending_approvals"], "Scenario-adjusted", "orange")

    st.dataframe(phases, use_container_width=True, hide_index=True)
    fig = px.bar(
        phases,
        x="Phase",
        y="Completion",
        color="Status",
        range_y=[0, 100],
        title=f"Planning Cycle Progress — {scenario_name}",
    )
    st.plotly_chart(style_plotly(fig), use_container_width=True)

    st.subheader("Decision Gates")
    st.dataframe(approvals, use_container_width=True, hide_index=True)

def financial_performance():
    scenario_name = st.session_state.selected_scenario
    scenario = current_scenario()
    page_header(
        "Financial Planning & Performance Dashboard",
        f"Budgets, actuals, forecasts and scenario analytics for the {scenario_name}."
    )

    budgets = scenario_adjusted_budgets(load_df("SELECT * FROM budgets"), scenario_name)
    budgets["variance"] = budgets["actual"] - budgets["budget"]
    budgets["variance_pct"] = budgets.apply(
        lambda r: (r["variance"] / r["budget"] * 100) if r["budget"] else 0,
        axis=1,
    )

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        metric_card("Data Quality Score", "87%", "Current validation", "green")
    with c2:
        tone = "green" if scenario["budget_variance"] <= 0 else "red"
        metric_card("Budget Variance", f"{scenario['budget_variance']:.2f}%", scenario_name, tone)
    with c3:
        metric_card("Cash Balance", f"{scenario['closing_cash']:,.0f}", "Projected", "blue")
    with c4:
        metric_card("Forecast Accuracy", f"{scenario['forecast_accuracy']}%", scenario_name, "green")
    with c5:
        metric_card("Overdue Submissions", scenario["pending_approvals"], "Requires action", "red")

    st.subheader("Budget Performance")
    st.dataframe(budgets, use_container_width=True, hide_index=True)

    left, right = st.columns(2)
    with left:
        fig = px.bar(
            budgets,
            x="department",
            y=["budget", "actual", "committed"],
            barmode="group",
            title=f"Budget, Actual and Committed — {scenario_name}",
        )
        st.plotly_chart(style_plotly(fig), use_container_width=True)

    with right:
        monthly = pd.DataFrame({
            "Month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
            "Forecast": [
                scenario["revenue"] * p for p in [0.10, 0.13, 0.15, 0.18, 0.21, 0.23]
            ],
            "Actual": [
                scenario["revenue"] * p for p in [0.09, 0.12, 0.14, 0.17, 0.20, 0.19]
            ],
        })
        fig = px.line(
            monthly,
            x="Month",
            y=["Forecast", "Actual"],
            markers=True,
            title=f"Forecast vs Actual — {scenario_name}",
        )
        st.plotly_chart(style_plotly(fig), use_container_width=True)

    st.subheader("Scenario Summary")
    scenario_df = pd.DataFrame([
        {"Scenario": name, **values}
        for name, values in SCENARIOS.items()
    ])[[
        "Scenario", "revenue", "operating_cost", "net_cash_flow",
        "financing_need", "closing_cash", "risk_exposure",
        "resource_pressure", "forecast_accuracy"
    ]]
    scenario_df.columns = [
        "Scenario", "Revenue", "Operating Cost", "Net Cash Flow",
        "Financing Need", "Closing Cash", "Risk Exposure",
        "Resource Pressure", "Forecast Accuracy"
    ]
    st.dataframe(scenario_df, use_container_width=True, hide_index=True)

def finance_dashboard():
    page_header("Financial Planning & Performance Dashboard", "Manage financial information quality, forecasts, budgets and performance.")
    tasks = load_df("SELECT * FROM tasks WHERE owner_role='Finance Manager'")
    st.dataframe(tasks, use_container_width=True, hide_index=True)
    financial_performance()


def department_dashboard():
    scenario_name = st.session_state.selected_scenario
    scenario = current_scenario()
    page_header(
        "Department Planning & Performance Dashboard",
        f"Departmental budget, resource and action implications under the {scenario_name}."
    )

    dept = st.selectbox("Department", ["Finance", "Operations", "IT", "Marketing"])
    budgets = scenario_adjusted_budgets(
        load_df("SELECT * FROM budgets WHERE department=?", [dept]),
        scenario_name,
    )
    resources = load_df("SELECT * FROM resources WHERE department=?", [dept])
    if not resources.empty:
        resources["required"] = resources["required"] * {
            "Optimistic Scenario": 0.95,
            "Main Scenario": 1.00,
            "Pessimistic Scenario": 1.15,
        }[scenario_name]
        resources["gap"] = resources["required"] - resources["available"]
    tasks = load_df("SELECT * FROM tasks WHERE owner_role IN ('Department Manager','Budget Owner')")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Department", dept, scenario_name, "blue")
    with c2:
        metric_card("Budget", f"{budgets['budget'].sum():,.0f}", "Scenario-adjusted", "blue")
    with c3:
        metric_card("Actual", f"{budgets['actual'].sum():,.0f}", "Scenario-adjusted", "orange")
    with c4:
        variance = budgets["actual"].sum() - budgets["budget"].sum()
        metric_card("Variance", f"{variance:,.0f}", "Actual minus budget", "red" if variance > 0 else "green")

    st.subheader(f"{dept} Budget")
    st.dataframe(budgets, use_container_width=True, hide_index=True)

    st.subheader(f"{dept} Resources")
    st.dataframe(resources, use_container_width=True, hide_index=True)

    st.subheader("Assigned Tasks")
    st.dataframe(tasks, use_container_width=True, hide_index=True)

def my_budget_actions():
    st.header("My Budget and Actions")
    st.dataframe(load_df("SELECT * FROM budgets WHERE owner IN ('Budget Owner','Department Manager')"), use_container_width=True, hide_index=True)
    st.dataframe(load_df("SELECT * FROM tasks WHERE owner_role IN ('Budget Owner','Department Manager')"), use_container_width=True, hide_index=True)


def risk_control_dashboard():
    scenario_name = st.session_state.selected_scenario
    scenario = current_scenario()
    page_header(
        "Risk & Control Dashboard",
        f"Scenario-adjusted risks, controls and mitigations for the {scenario_name}."
    )

    risks = scenario_adjusted_risks(load_df("SELECT * FROM risks"), scenario_name)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Total Risks", len(risks), scenario_name, "blue")
    with c2:
        metric_card("High Risks", int((risks["score"] >= 16).sum()), "Critical attention", "red")
    with c3:
        metric_card("Risk Exposure", scenario["risk_exposure"], "Scenario index", "orange")
    with c4:
        tone = scenario_status_tone(scenario["resource_pressure"])
        metric_card("Resource Pressure", scenario["resource_pressure"], "Scenario effect", tone)

    fig = px.scatter(
        risks,
        x="likelihood",
        y="impact",
        size="score",
        color="category",
        hover_name="title",
        range_x=[0, 5.5],
        range_y=[0, 5.5],
        title=f"Risk Heatmap — {scenario_name}",
    )
    st.plotly_chart(style_plotly(fig), use_container_width=True)
    st.dataframe(risks, use_container_width=True, hide_index=True)

    st.subheader("Scenario Risk Recommendation")
    st.info(scenario["recommendation"])

    with st.expander("Add a new risk"):
        with st.form("risk_form"):
            title = st.text_input("Risk title")
            category = st.selectbox(
                "Category",
                ["Liquidity", "Credit", "Debt", "Operational", "Information", "Compliance", "Stakeholder", "Resource"],
            )
            likelihood = st.slider("Likelihood", 1, 5, 3)
            impact = st.slider("Impact", 1, 5, 3)
            owner = st.text_input("Owner")
            mitigation = st.text_area("Mitigation")
            due_date = st.date_input("Due date")
            submitted = st.form_submit_button("Save risk")
            if submitted and title:
                conn = get_conn()
                conn.execute("""
                    INSERT INTO risks(title,category,likelihood,impact,owner,mitigation,status,due_date)
                    VALUES(?,?,?,?,?,?,?,?)
                """, (title, category, likelihood, impact, owner, mitigation, "Open", str(due_date)))
                conn.commit()
                conn.close()
                st.success("Risk saved. Refresh the page to update the table.")

def data_quality():
    page_header("Financial Information Quality Dashboard", "Assess accuracy, completeness, consistency and timeliness of financial information.")
    issues = pd.DataFrame({
        "Data Source": ["Balance Sheet", "Cash Flow", "Budget File", "Department Submission"],
        "Accuracy": [92, 78, 88, 82],
        "Completeness": [95, 84, 90, 76],
        "Consistency": [89, 70, 85, 79],
        "Timeliness": [90, 86, 80, 72],
        "Status": ["Green", "Red", "Amber", "Amber"],
    })
    st.dataframe(issues, use_container_width=True, hide_index=True)
    long_df = issues.melt(id_vars=["Data Source", "Status"], value_vars=["Accuracy", "Completeness", "Consistency", "Timeliness"], var_name="Dimension", value_name="Score")
    st.plotly_chart(px.bar(long_df, x="Data Source", y="Score", color="Dimension", barmode="group", title="Information Quality by Source"), use_container_width=True)


def stakeholders_resources():
    scenario_name = st.session_state.selected_scenario
    scenario = current_scenario()
    page_header(
        "Stakeholder & Resource Dashboard",
        f"Stakeholder readiness and scenario-adjusted resource capacity for the {scenario_name}."
    )

    stakeholders = load_df("SELECT * FROM stakeholders")
    resources = load_df("SELECT * FROM resources")

    resource_multiplier = {
        "Optimistic Scenario": 0.95,
        "Main Scenario": 1.00,
        "Pessimistic Scenario": 1.15,
    }[scenario_name]
    resources["required"] = resources["required"] * resource_multiplier
    resources["gap"] = resources["required"] - resources["available"]

    c1, c2, c3 = st.columns(3)
    with c1:
        metric_card("Open Consultations", int((stakeholders["status"] != "Consulted").sum()), "Stakeholder actions", "orange")
    with c2:
        metric_card("Resource Pressure", scenario["resource_pressure"], scenario_name, scenario_status_tone(scenario["resource_pressure"]))
    with c3:
        metric_card("Total Resource Gap", f"{resources['gap'].sum():,.0f}", "Scenario-adjusted", "red" if resources["gap"].sum() > 0 else "green")

    st.subheader("Stakeholder Register")
    st.dataframe(stakeholders, use_container_width=True, hide_index=True)

    st.subheader("Resource Capacity")
    st.dataframe(resources, use_container_width=True, hide_index=True)

    fig = px.bar(
        resources,
        x="department",
        y=["available", "required", "allocated"],
        barmode="group",
        title=f"Resource Capacity by Department — {scenario_name}",
    )
    st.plotly_chart(style_plotly(fig), use_container_width=True)

def consultation_feedback():
    page_header("Stakeholder Engagement Dashboard", "View consultations, stakeholder responses, issues and management feedback.")
    st.dataframe(load_df("SELECT * FROM stakeholders"), use_container_width=True, hide_index=True)
    with st.form("feedback_form"):
        stakeholder = st.text_input("Stakeholder name")
        subject = st.text_input("Subject")
        text = st.text_area("Feedback")
        if st.form_submit_button("Submit feedback") and stakeholder and text:
            conn = get_conn()
            conn.execute("INSERT INTO feedback(stakeholder,subject,feedback_text,response,status) VALUES(?,?,?,?,?)", (stakeholder, subject, text, "", "Open"))
            conn.commit(); conn.close()
            st.success("Feedback submitted.")
    feedback = load_df("SELECT * FROM feedback")
    if not feedback.empty:
        st.dataframe(feedback, use_container_width=True, hide_index=True)


def evaluation_learning():
    page_header("Evaluation & Action Research Dashboard", "Track research baselines, intervention cycles, post-intervention evidence and lessons learned.")
    assessments = load_df("SELECT * FROM assessments")
    assessments["construct_full"] = assessments["construct"].map(CONSTRUCT_LABELS).fillna(assessments["construct"])

    pivot = assessments.pivot_table(
        index="construct_full",
        columns="cycle_label",
        values="score",
        aggfunc="mean"
    )
    st.dataframe(pivot, use_container_width=True)

    baseline = assessments[assessments["cycle_label"] == "Baseline"]
    fig = px.bar(
        baseline,
        x="construct_full",
        y="score",
        range_y=[0, 5],
        title="Research Baseline Construct Scores",
        labels={"construct_full": "Construct", "score": "Baseline Score"}
    )
    st.plotly_chart(style_plotly(fig), use_container_width=True)
    st.info("Post-intervention values remain blank until actual Action Research data are collected.")

    with st.expander("Record a new assessment cycle"):
        with st.form("assessment_form"):
            cycle_label = st.text_input("Cycle label", placeholder="Cycle 1")
            construct_label = st.selectbox("Construct", list(CONSTRUCT_LABELS.values()))
            construct = next(code for code, label in CONSTRUCT_LABELS.items() if label == construct_label)
            score = st.slider("Score", 1.0, 5.0, 3.0, 0.001)
            assessment_date = st.date_input("Assessment date")
            submitted = st.form_submit_button("Save assessment")
            if submitted and cycle_label:
                conn = get_conn()
                conn.execute("""
                    INSERT INTO assessments(cycle_label,construct,score,assessment_date)
                    VALUES(?,?,?,?)
                """, (cycle_label, construct, score, str(assessment_date)))
                conn.commit()
                conn.close()
                st.success("Assessment saved.")

def audit_assurance():
    page_header("Internal Reviewer / Auditor Dashboard", "Review controls, approvals, audit evidence, exceptions and assurance findings.")
    st.dataframe(load_df("SELECT * FROM approvals"), use_container_width=True, hide_index=True)
    high = load_df("SELECT *, likelihood*impact AS score FROM risks WHERE likelihood*impact >= 12")
    st.dataframe(high, use_container_width=True, hide_index=True)
    st.warning("Approved source records should be read-only. Audit observations should be recorded separately.")


def system_admin():
    page_header("System Administrator Dashboard", "Manage users, roles, platform health, backups, logs and technical alerts.")
    st.dataframe(pd.DataFrame({"Metric": ["Active users", "Failed logins", "Backups completed", "Open technical issues"], "Value": [18,2,7,1]}), use_container_width=True, hide_index=True)
    st.caption("Demo only: production authentication and audit logging are not implemented.")


def my_tasks(role):
    st.header("My Tasks")
    st.dataframe(load_df("SELECT * FROM tasks WHERE owner_role=?", [role]), use_container_width=True, hide_index=True)


def construct_glossary():
    st.header("Research Construct Glossary")
    rows = [
        {
            "Abbreviation": code,
            "Full construct name": CONSTRUCT_LABELS[code],
            "Research baseline score": score,
        }
        for code, score in BASELINES.items()
    ]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    st.caption(
        "Full names are used in thesis text and principal dashboard labels. "
        "Abbreviations remain available for compact charts and internal data fields."
    )


def render_page(page, role):
    routes = {
        "Executive Dashboard": executive_dashboard,
        "Control Centre": control_centre,
        "Planning & Decisions": planning_decisions,
        "Financial Performance": financial_performance,
        "Finance Dashboard": finance_dashboard,
        "Department Dashboard": department_dashboard,
        "My Budget & Actions": my_budget_actions,
        "Risk & Control Dashboard": risk_control_dashboard,
        "Risks & Controls": risk_control_dashboard,
        "Risks": risk_control_dashboard,
        "Data Quality": data_quality,
        "Stakeholders & Resources": stakeholders_resources,
        "Consultation & Feedback": consultation_feedback,
        "Evaluation & Learning": evaluation_learning,
        "Audit & Assurance": audit_assurance,
        "System Administration": system_admin,
        "My Tasks": lambda: my_tasks(role),
        "Budgets": financial_performance,
        "Resources": stakeholders_resources,
        "Data Import Centre": lambda: data_import_centre(role),
        "Research Construct Glossary": construct_glossary,
    }
    routes.get(page, executive_dashboard)()


def main():
    st.set_page_config(page_title=f"{ORG_NAME} · SFPMS", page_icon="📊", layout="wide")
    inject_corporate_theme()
    init_db()
    ensure_import_tables()
    init_scenario_state()

    with st.sidebar:
        render_sidebar_brand()
        st.subheader("Demo Profile")
        role = st.selectbox("Profile", ROLES, label_visibility="collapsed")
        st.subheader("Planning Scenario")
        scenario_selector(role, compact=True)
        pages = ROLE_PAGES[role] + ["Data Import Centre"]
        page = st.radio("Navigation", pages)
        st.divider()
        st.caption("All construct scores shown are research baseline values. Post-intervention values must come from collected Action Research data.")

    render_masthead(role, st.session_state.selected_scenario)
    render_page(page, role)
    render_footer(role)


if __name__ == "__main__":
    main()
