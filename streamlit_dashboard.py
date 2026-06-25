import streamlit as st
from smart_hospital import run_patient_flow, get_doctor_status, get_beds
from datetime import datetime
import pytz

st.set_page_config(
    page_title="SHMAS — Smart Hospital Multi-Agent System",
    page_icon="+",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Design Tokens (HealthOps palette) ────────────────────────────────────────
BG         = "#F5F7FA"
WHITE      = "#FFFFFF"
TEXT       = "#101A18"
TEXT_DIM   = "#5F6D7E"
TEXT_LIGHT = "#8896A6"
CYAN       = "#007C91"
CYAN_LIGHT = "#E6F4F6"
GREEN      = "#0EAF52"
GREEN_BG   = "#EAFAF0"
RED        = "#D53411"
RED_BG     = "#FDF0ED"
AMBER      = "#E6960E"
AMBER_BG   = "#FFF8E8"
BORDER     = "#E2E8F0"
SHADOW     = "0 1px 3px rgba(16,26,24,0.06), 0 1px 2px rgba(16,26,24,0.04)"

AGENT_ICONS = {
    "MentalHealthAnalyzerAgent": "",
    "EmergencyTriageAgent": "",
    "DoctorSchedulerAgent": "",
    "BedManagerAgent": "",
    "ConflictResolverAgent": "",
}
AGENT_COLORS = {
    "MentalHealthAnalyzerAgent": "#7C3AED",
    "EmergencyTriageAgent": "#E04343",
    "DoctorSchedulerAgent": "#007C91",
    "BedManagerAgent": "#0EAF52",
    "ConflictResolverAgent": "#E6960E",
}


# ── CSS ──────────────────────────────────────────────────────────────────────
def inject_css():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Urbanist:wght@400;500;600;700;800&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded');

/* ── Global light-theme reset ─────────────────────────────── */
* { box-sizing: border-box; }
.stApp { background-color: #F1F5F9 !important; }
section[data-testid="stSidebar"] { background-color: #FFFFFF !important; }
section[data-testid="stSidebar"] > div { background-color: #FFFFFF !important; }
.block-container { background-color: transparent !important; padding-top: 1rem !important; }

/* ── Hide chrome ───────────────────────────────────────────── */
#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}
/* Hide sidebar collapse arrow text */
[data-testid="stSidebar"] button[kind="header"],
[data-testid="collapsedControl"],
section[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"],
section[data-testid="stSidebar"] > div:first-child > button {
    display: none !important;
}
section[data-testid="stSidebar"] .material-symbols-rounded {
    display: none !important;
}

/* ── Base ──────────────────────────────────────────────────── */
html, body, [data-testid="stAppViewContainer"],
[data-testid="stApp"] {
    background-color: #F1F5F9 !important;
    color: #1E293B !important;
    font-family: 'Urbanist', -apple-system, sans-serif !important;
}
.main .block-container {
    padding-top: 0.8rem !important;
    max-width: 100%;
}
[data-testid="stHeader"] {
    background-color: #FFFFFF !important;
    border-bottom: 1px solid #E2E8F0;
}
* {
    font-family: 'Urbanist', -apple-system, sans-serif !important;
}

/* ── Sidebar ───────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background-color: #FFFFFF !important;
    border-right: 1px solid #E2E8F0 !important;
}
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] .stMarkdown div,
section[data-testid="stSidebar"] .stMarkdown span,
section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] {
    color: #1E293B !important;
}

/* ── Sidebar text inputs ──────────────────────────────────── */
section[data-testid="stSidebar"] .stTextInput input,
section[data-testid="stSidebar"] .stTextArea textarea {
    background-color: #F8FAFC !important;
    color: #1E293B !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 8px !important;
    font-family: 'Urbanist', sans-serif !important;
}
section[data-testid="stSidebar"] .stTextInput input:focus,
section[data-testid="stSidebar"] .stTextArea textarea:focus {
    border-color: #0D9488 !important;
    box-shadow: 0 0 0 3px rgba(13,148,136,0.12) !important;
}

/* ── Number input: only style the text input, not container ── */
[data-testid="stNumberInput"] input {
    background: #FFFFFF !important;
    color: #1E293B !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 6px !important;
}
[data-testid="stNumberInput"] {
    background: transparent !important;
}
[data-testid="stNumberInput"] > div {
    background: transparent !important;
}
[data-testid="stNumberInput"] button {
    background: #F1F5F9 !important;
    color: #475569 !important;
    border: 1px solid #CBD5E1 !important;
}

/* ── Selectbox ─────────────────────────────────────────────── */
section[data-testid="stSidebar"] .stSelectbox > div > div {
    background-color: #F8FAFC !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 8px !important;
    color: #1E293B !important;
}

/* ── Captions ──────────────────────────────────────────────── */
section[data-testid="stSidebar"] .stCaption,
section[data-testid="stSidebar"] .stCaption p {
    color: #94A3B8 !important;
    font-size: 12px !important;
}

/* ── Admit Patient CTA (scoped to form submit only) ───────── */
section[data-testid="stSidebar"] .stFormSubmitButton button {
    background: #0D9488 !important;
    color: #FFFFFF !important;
    font-weight: 700 !important;
    font-size: 15px !important;
    border: none !important;
    border-radius: 10px !important;
    height: 48px !important;
    width: 100% !important;
    letter-spacing: 0.3px !important;
    box-shadow: none;
    transition: all 0.2s ease !important;
}
section[data-testid="stSidebar"] .stFormSubmitButton button:hover {
    background: #0F766E !important;
    box-shadow: 0 4px 12px rgba(13,148,136,0.3) !important;
    transform: translateY(-1px);
}

/* ── Expander consistency ─────────────────────────────────── */
[data-testid="stExpander"] {
    background: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 10px !important;
    margin-bottom: 8px;
    overflow: hidden;
}
[data-testid="stExpander"] summary {
    background: #F8FAFC !important;
    border-radius: 10px !important;
    color: #1E293B !important;
    font-weight: 600;
    font-size: 13px;
}
[data-testid="stExpander"] > div {
    background: #FFFFFF !important;
    border-top: 1px solid #E2E8F0;
    padding: 12px;
}
[data-testid="stExpander"] details {
    background: #FFFFFF !important;
}
[data-testid="stExpander"] summary span,
[data-testid="stExpander"] summary p {
    color: #1E293B !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    background: transparent !important;
}
/* Hide broken Material Symbols text in expanders */
[data-testid="stExpander"] .material-symbols-rounded,
[data-testid="stExpander"] summary .material-symbols-rounded,
[data-testid="stExpander"] summary span.material-symbols-rounded {
    font-size: 0 !important;
    width: 0 !important;
    height: 0 !important;
    overflow: hidden !important;
    display: none !important;
}

/* ── Dividers ──────────────────────────────────────────────── */
.stDivider, hr { border-color: #E2E8F0 !important; opacity: 0.5; }

/* ── Slider accent ─────────────────────────────────────────── */
section[data-testid="stSidebar"] .stSlider > div > div > div {
    background: #0D9488 !important;
}

/* ── Scrollbar ─────────────────────────────────────────────── */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #CBD5E1; border-radius: 3px; }

/* ── Refresh button (scoped via div.refresh-btn) ──────────── */
div.refresh-btn button,
div.refresh-btn .stButton > button,
div.refresh-btn [data-testid="stBaseButton-secondary"] {
    background-color: #F1F5F9 !important;
    color: #475569 !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 8px !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    box-shadow: none !important;
    padding: 4px 14px !important;
}
div.refresh-btn button:hover,
div.refresh-btn .stButton > button:hover,
div.refresh-btn [data-testid="stBaseButton-secondary"]:hover {
    background-color: #E2E8F0 !important;
    color: #1E293B !important;
}

/* ── Fallback: force ALL main-area buttons light ──────────── */
/* Only st.button lives in .main; form_submit is in sidebar   */
.main button,
.main .stButton button,
.main .stButton > button,
.main [data-testid="stBaseButton-secondary"],
[data-testid="column"] button,
[data-testid="column"] .stButton button,
[data-testid="column"] .stButton > button {
    background-color: #F1F5F9 !important;
    color: #475569 !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    font-size: 12px !important;
    padding: 4px 14px !important;
    box-shadow: none !important;
}
.main button:hover,
.main .stButton button:hover,
.main .stButton > button:hover,
.main [data-testid="stBaseButton-secondary"]:hover,
[data-testid="column"] button:hover,
[data-testid="column"] .stButton button:hover,
[data-testid="column"] .stButton > button:hover {
    background-color: #E2E8F0 !important;
    color: #1E293B !important;
}
</style>
""", unsafe_allow_html=True)


# ── Helpers ──────────────────────────────────────────────────────────────────
def get_priority_label(tl):
    return {5: "Critical", 4: "Emergent", 3: "Urgent", 2: "Semi-Urgent", 1: "Routine"}.get(tl, "Unknown")


def _parse_log(log):
    ts, agent, msg = "", "", log
    if "]" in log:
        ts_part, rest = log.split("]", 1)
        ts = ts_part.strip("[").strip()
        rest = rest.strip()
        if ":" in rest:
            idx = rest.index(":")
            agent, msg = rest[:idx].strip(), rest[idx + 1:].strip()
        else:
            msg = rest
    return ts, agent, msg


def _short(a):
    return (a.replace("Agent", "").replace("MentalHealthAnalyzer", "Mood Analyzer")
            .replace("EmergencyTriage", "Triage").replace("DoctorScheduler", "Doctor Scheduler")
            .replace("BedManager", "Bed Manager").replace("ConflictResolver", "Conflict Resolver"))


def _icon(a):
    for k, v in AGENT_ICONS.items():
        if k in a: return v
    return ""


def _color(a):
    for k, v in AGENT_COLORS.items():
        if k in a: return v
    return TEXT_DIM


def _badge(s):
    if s == "Success":
        return f'<span style="background:{GREEN_BG}; color:{GREEN}; border:1px solid {GREEN}40; padding:3px 12px; border-radius:20px; font-size:11px; font-weight:700; letter-spacing:0.3px;">{s}</span>'
    if s == "Failed":
        return f'<span style="background:{RED_BG}; color:{RED}; border:1px solid {RED}40; padding:3px 12px; border-radius:20px; font-size:11px; font-weight:700; letter-spacing:0.3px;">{s}</span>'
    if s == "Queued":
        return f'<span style="background:{AMBER_BG}; color:{AMBER}; border:1px solid {AMBER}40; padding:3px 12px; border-radius:20px; font-size:11px; font-weight:700; letter-spacing:0.3px;">{s}</span>'
    return f'<span style="background:{BG}; color:{TEXT_LIGHT}; border:1px solid {BORDER}; padding:3px 12px; border-radius:20px; font-size:11px; font-weight:700; letter-spacing:0.3px;">{s}</span>'


# ── Sidebar ──────────────────────────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        with st.form("patient_form", clear_on_submit=True):
            st.markdown(f'<div style="font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:0.12em; color:{TEXT_LIGHT}; margin-bottom:6px;">Patient Information</div>', unsafe_allow_html=True)
            name = st.text_input("Full Name", "John Doe")
            email = st.text_input("Email", "johndoe@example.com")
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            age = st.slider("Age", 0, 100, 45)

            st.divider()

            st.markdown(f'<div style="font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:0.12em; color:{TEXT_LIGHT}; margin-bottom:6px;">Symptoms & Duration</div>', unsafe_allow_html=True)
            symptoms_text = st.text_area("Symptoms (comma separated)", "chest pain, shortness of breath", height=80)
            duration = st.slider("Symptom Duration (hours)", 0, 72, 2)

            st.divider()

            st.markdown(f'<div style="font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:0.12em; color:{TEXT_LIGHT}; margin-bottom:6px;">Vitals</div>', unsafe_allow_html=True)
            hr = st.number_input("Heart Rate (bpm)", 30, 200, 80)
            st.caption("Normal: 60–100 bpm")
            systolic = st.number_input("Systolic BP (mmHg)", 60, 250, 120)
            st.caption("Normal: 90–120 mmHg")
            diastolic = st.number_input("Diastolic BP (mmHg)", 40, 150, 80)
            st.caption("Normal: 60–80 mmHg")

            st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
            submitted = st.form_submit_button("Admit Patient", use_container_width=True)

            if submitted:
                vitals = {"blood_pressure": {"systolic": systolic, "diastolic": diastolic}, "heart_rate": hr}
                symptoms = [s.strip() for s in symptoms_text.split(",")]
                with st.spinner("Processing admission through multi-agent pipeline..."):
                    result = run_patient_flow(
                        name=name.strip(), symptoms=symptoms, vitals=vitals,
                        symptom_duration=duration, age=age, gender=gender, email=email,
                    )
                    st.session_state["last_patient"] = result["patient"].to_dict()
                    st.session_state["last_status"] = result["status"]
                    st.session_state["logs"] = result["logs"]
                    st.session_state["show_results"] = True
                    st.rerun()


# ── Header ───────────────────────────────────────────────────────────────────
def render_header():
    now = datetime.now(pytz.timezone("US/Eastern")).strftime("%A, %b %d %Y — %I:%M:%S %p EST")
    st.markdown(f"""
    <div style="background:{WHITE}; border:1px solid {BORDER}; border-radius:16px; padding:18px 28px; margin-bottom:22px; box-shadow:{SHADOW}; display:flex; justify-content:space-between; align-items:center;">
        <div>
            <div style="display:flex; align-items:center; gap:12px;">
                <div style="width:42px; height:42px; background:{CYAN}; border-radius:12px; display:flex; align-items:center; justify-content:center;">
                    <span style="font-size:18px; line-height:1; color:#FFFFFF; font-weight:800;">+</span>
                </div>
                <div>
                    <div style="font-size:22px; font-weight:800; color:{TEXT};">SHMAS <span style="font-size:14px; font-weight:500; color:{TEXT_LIGHT}; margin-left:4px;">Dashboard</span></div>
                    <div style="font-size:12px; color:{TEXT_LIGHT}; margin-top:1px; display:flex; align-items:center; gap:6px;">
                        <span style="width:7px; height:7px; background:{GREEN}; border-radius:50%; display:inline-block; animation:pulse-dot 1.5s infinite;"></span>
                        Autonomous Hospital Operations — Powered by Multi-Agent AI
                    </div>
                </div>
            </div>
        </div>
        <div style="font-family:'Urbanist',monospace; font-size:13px; color:{CYAN}; background:{CYAN_LIGHT}; padding:8px 18px; border-radius:10px; font-weight:600;">{now}</div>
    </div>
    <style>@keyframes pulse-dot {{ 0%,100% {{ opacity:1; }} 50% {{ opacity:0.35; }} }}</style>
    """, unsafe_allow_html=True)


# ── Result Card ──────────────────────────────────────────────────────────────
def render_result_card():
    if not st.session_state.get("show_results") or "last_patient" not in st.session_state:
        return

    p = st.session_state["last_patient"]
    status = st.session_state.get("last_status", {})
    resolver = status.get("ConflictResolver", "Pending")

    if resolver == "Success":
        card_bg, accent, icon_bg = GREEN_BG, GREEN, "#D4EDDA"
        icon, headline = "OK", f"{p['name']} admitted successfully"
        detail = f"Assigned to <strong style='color:{CYAN};'>{p.get('department', '—')}</strong> · Doctor: <strong>{p.get('assigned_doctor', '—')}</strong> · Bed: <strong>#{p.get('assigned_bed', '—')}</strong>"
    elif resolver == "Queued":
        card_bg, accent, icon_bg = AMBER_BG, AMBER, "#FFF3CD"
        icon, headline = "Q", f"{p['name']} queued for admission"
        detail = "Resources currently unavailable — patient has been added to the priority queue."
    else:
        card_bg, accent, icon_bg = RED_BG, RED, "#F8D7DA"
        icon, headline = "X", f"Admission failed for {p['name']}"
        detail = "No beds or doctors available. Please try nearby hospitals."

    triage = p.get("triage_level", 0) or 0
    pill = f"background:{WHITE}; border:1px solid {BORDER}; padding:10px 18px; border-radius:12px; display:inline-block; margin-right:10px; margin-top:8px; box-shadow:{SHADOW};"
    lbl = f"font-size:10px; text-transform:uppercase; letter-spacing:0.12em; color:{TEXT_LIGHT}; display:block; font-weight:600;"
    val = f"font-size:17px; font-weight:700; color:{TEXT}; display:block; margin-top:3px;"

    st.markdown(f"""
    <div style="background:{card_bg}; border:1px solid {accent}30; border-left:5px solid {accent}; border-radius:14px; padding:22px 26px; margin-bottom:22px; box-shadow:{SHADOW};">
        <div style="display:flex; align-items:center; gap:14px; margin-bottom:10px;">
            <div style="width:40px; height:40px; background:{icon_bg}; border-radius:10px; display:flex; align-items:center; justify-content:center; font-size:20px;">{icon}</div>
            <span style="font-size:20px; font-weight:700; color:{TEXT};">{headline}</span>
        </div>
        <div style="color:{TEXT_DIM}; font-size:13px; margin-bottom:16px;">{detail}</div>
        <div>
            <span style="{pill}"><span style="{lbl}">Triage</span><span style="{val}">{triage} — {get_priority_label(triage)}</span></span>
            <span style="{pill}"><span style="{lbl}">Department</span><span style="{val} color:{CYAN};">{p.get('department', '—')}</span></span>
            <span style="{pill}"><span style="{lbl}">Priority Score</span><span style="{val}">{p.get('priority_score', '—')}</span></span>
            <span style="{pill}"><span style="{lbl}">Mood</span><span style="{val}">{p.get('mood', '—')}</span></span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── Agent Activity Feed ──────────────────────────────────────────────────────
def render_agent_feed():
    st.markdown(f'<div style="font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:0.12em; color:{TEXT_LIGHT}; margin-bottom:10px;">Agent Activity Feed</div>', unsafe_allow_html=True)

    if not st.session_state.get("show_results") or "logs" not in st.session_state:
        st.markdown(f"""
<div style="background:{WHITE}; border:1px solid {BORDER}; border-radius:14px; box-shadow:{SHADOW};">
  <div style="display:flex; flex-direction:column; align-items:center; justify-content:center; padding:48px 24px; text-align:center;">
    <div style="width:56px; height:56px; background:#F0FDF4; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:18px; font-weight:800; color:#16A34A; margin-bottom:16px;">+</div>
    <div style="color:#1E293B; font-size:16px; font-weight:600; margin-bottom:6px;">Pipeline Ready</div>
    <div style="color:#94A3B8; font-size:13px; max-width:240px; line-height:1.6;">Fill in patient details on the left and click Admit Patient to activate all 5 agents.</div>
    <div style="margin-top:20px; display:flex; gap:8px; flex-wrap:wrap; justify-content:center;">
      <span style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:20px; padding:4px 12px; font-size:11px; color:#64748B;">Mood Analyzer</span>
      <span style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:20px; padding:4px 12px; font-size:11px; color:#64748B;">Triage</span>
      <span style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:20px; padding:4px 12px; font-size:11px; color:#64748B;">Doctor Scheduler</span>
      <span style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:20px; padding:4px 12px; font-size:11px; color:#64748B;">Bed Manager</span>
      <span style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:20px; padding:4px 12px; font-size:11px; color:#64748B;">Conflict Resolver</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)
        return

    logs = st.session_state["logs"]
    status = st.session_state.get("last_status", {})

    sm = {"MoodAnalyzer": "Mood", "EmergencyTriage": "Triage", "DoctorScheduler": "Doctor", "BedManager": "Bed", "ConflictResolver": "Resolver"}
    badges = '<div style="display:flex; gap:8px; flex-wrap:wrap; margin-bottom:14px;">'
    for k, lbl in sm.items():
        s = status.get(k, "Pending")
        badges += f'<span style="font-size:12px; color:{TEXT_DIM}; font-weight:500;">{lbl}</span> {_badge(s)}'
    badges += "</div>"
    st.markdown(badges, unsafe_allow_html=True)

    rows = ""
    for log in logs:
        ts, agent, msg = _parse_log(log)
        ic = _icon(agent)
        col = _color(agent)
        sn = _short(agent)
        rows += f"""<div style="display:flex; gap:12px; padding:10px 0; border-bottom:1px solid {BORDER}; align-items:flex-start;">
  <span style="color:{TEXT_LIGHT}; font-family:monospace; font-size:11px; min-width:85px; padding-top:2px;">{ts}</span>
  <span style="color:{col}; font-size:12px; font-weight:700; min-width:150px;">{ic} {sn}</span>
  <span style="color:{TEXT}; font-size:13px; line-height:1.5;">{msg}</span>
</div>"""

    st.markdown(f'<div style="background:{WHITE}; border:1px solid {BORDER}; border-radius:14px; padding:16px 20px; box-shadow:{SHADOW};">{rows}</div>', unsafe_allow_html=True)


# ── Bed Availability ─────────────────────────────────────────────────────────
def render_beds():
    st.markdown(f'<div style="font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:0.12em; color:{TEXT_LIGHT}; margin-bottom:10px;">Bed Availability</div>', unsafe_allow_html=True)

    beds = get_beds()
    if not beds:
        st.markdown(f'<div style="background:{WHITE}; border:1px solid {BORDER}; border-radius:14px; text-align:center; padding:36px; color:{TEXT_LIGHT}; box-shadow:{SHADOW};">No bed data available.</div>', unsafe_allow_html=True)
        return

    bed_icons = {"ICU": "", "Emergency": "", "Ward": "", "Normal": ""}

    for bed_type, bed_data in beds.items():
        avail, occ = bed_data[0], bed_data[1]
        total = avail + occ
        occ_pct = (occ / total * 100) if total > 0 else 0
        bi = bed_icons.get(bed_type, "🔵")

        if avail == 0:
            sc, bar_col, st_text, st_bg, st_bdr = "#DC2626", "#DC2626", "FULL", "#FEF2F2", "#FECACA"
        elif avail == total:
            sc, bar_col, st_text, st_bg, st_bdr = "#16A34A", "#16A34A", "ALL CLEAR", "#F0FDF4", "#BBF7D0"
        else:
            sc, bar_col, st_text, st_bg, st_bdr = "#D97706", "#F59E0B", "PARTIAL", "#FFFBEB", "#FDE68A"

        st.markdown(f"""
<div style="background:{WHITE}; border:1px solid {BORDER}; border-radius:14px; padding:18px; margin-bottom:10px; box-shadow:{SHADOW};">
  <div style="display:flex; justify-content:space-between; align-items:center;">
    <span style="color:{TEXT_DIM}; font-size:12px; font-weight:600; text-transform:uppercase; letter-spacing:0.08em;">{bed_type}</span>
    <span style="background:{st_bg}; color:{sc}; border:1px solid {st_bdr}; border-radius:20px; padding:3px 12px; font-size:11px; font-weight:700;">{st_text}</span>
  </div>
  <div style="margin-top:10px; font-size:30px; font-weight:800; color:{TEXT};">
    {avail} <span style="font-size:14px; font-weight:500; color:{TEXT_LIGHT};">/ {total} beds</span>
  </div>
  <div style="margin-top:8px; background:#E2E8F0; border-radius:6px; height:6px; overflow:hidden;">
    <div style="background:{bar_col}; width:{occ_pct:.0f}%; height:6px; border-radius:6px; transition:width 0.4s ease;"></div>
  </div>
  <div style="display:flex; justify-content:space-between; margin-top:6px; font-size:12px;">
    <span style="color:#16A34A; font-weight:600;">Available: {avail}</span>
    <span style="color:#DC2626; font-weight:600;">Occupied: {occ}</span>
  </div>
</div>
""", unsafe_allow_html=True)


# ── Doctor Availability ──────────────────────────────────────────────────────
def render_doctors():
    hdr_col, btn_col = st.columns([3, 1])
    with hdr_col:
        st.markdown(f'<div style="font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:0.12em; color:{TEXT_LIGHT}; padding-top:6px;">Doctor Availability</div>', unsafe_allow_html=True)
    with btn_col:
        st.markdown('<div class="refresh-btn">', unsafe_allow_html=True)
        if st.button("Refresh", key="refresh_docs"):
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    doctors = get_doctor_status()
    if not doctors:
        st.markdown(f'<div style="background:{WHITE}; border:1px solid {BORDER}; border-radius:14px; text-align:center; padding:36px; color:{TEXT_LIGHT}; box-shadow:{SHADOW};">No doctor data.</div>', unsafe_allow_html=True)
        return

    for doc in doctors:
        busy = doc["status"] == "BUSY"
        if busy:
            b_bg, b_col, b_bdr, b_txt = RED_BG, RED, f"{RED}40", "BUSY"
        else:
            b_bg, b_col, b_bdr, b_txt = GREEN_BG, GREEN, f"{GREEN}40", "AVAILABLE"

        detail = ""
        if busy:
            rem = doc.get("time_remaining", "?")
            wp = doc.get("with_patient", "—")
            detail = f'<div style="color:{TEXT_LIGHT}; font-size:11px; margin-top:5px;">With: <span style="color:{TEXT_DIM};">{wp}</span> · <span style="color:{AMBER}; font-weight:600;">{rem} min left</span></div>'

        st.markdown(f"""
<div style="background:{WHITE}; border:1px solid {BORDER}; border-radius:14px; padding:16px 18px; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center; box-shadow:{SHADOW};">
  <div>
    <div style="color:{TEXT}; font-size:14px; font-weight:700;">{doc['doctor_name']}</div>
    <div style="color:{TEXT_LIGHT}; font-size:12px; margin-top:2px;">{doc['department']}</div>
    {detail}
  </div>
  <span style="background:{b_bg}; color:{b_col}; border:1px solid {b_bdr}; border-radius:20px; padding:4px 14px; font-size:11px; font-weight:700; white-space:nowrap;">{b_txt}</span>
</div>
""", unsafe_allow_html=True)


# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    if "last_patient" not in st.session_state:
        st.session_state["last_patient"] = None
    if "last_status" not in st.session_state:
        st.session_state["last_status"] = {}
    if "logs" not in st.session_state:
        st.session_state["logs"] = []
    if "show_results" not in st.session_state:
        st.session_state["show_results"] = False

    inject_css()
    render_sidebar()
    render_header()
    render_result_card()

    col_feed, col_beds, col_docs = st.columns([4, 3, 3])
    with col_feed:
        render_agent_feed()
    with col_beds:
        render_beds()
    with col_docs:
        render_doctors()


if __name__ == "__main__":
    main()
