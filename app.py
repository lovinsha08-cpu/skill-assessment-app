"""
app.py
------
Main entry point for the Skill Assessment & Career Recommender app.

Run with:
    streamlit run app.py

This file:
  1. Configures global Streamlit page settings
  2. Initialises session state
  3. Renders the sidebar navigation
  4. Acts as the landing redirect to Page 1
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import warnings
warnings.filterwarnings("ignore", message="missing ScriptRunContext")

import streamlit as st
import config
from modules.session_state import SessionStateManager as SM
from utils.logger import get_logger

logger = get_logger(__name__)

# ── Global page config ────────────────────────────────────────────────────────
st.set_page_config(
    page_title=config.APP_TITLE,
    page_icon=config.APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Init session state on first load ─────────────────────────────────────────
SM.init()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"## {config.APP_ICON} Skill Assessment")
    st.caption(f"v{config.APP_VERSION}")
    st.divider()

    # Progress indicator
    match_result = SM.get_match_result()
    quiz_done    = SM.is_quiz_complete()
    skill_scores = SM.get_skill_scores()
    recs         = SM.get_recommendations()

    steps_status = [
        ("📄 Upload Resume",            True),
        ("🔍 Skill Results",            bool(match_result)),
        ("📝 Quiz",                     bool(SM.get_quiz_questions())),
        ("📊 Score Report",             quiz_done),
        ("📈 Dashboard",                bool(skill_scores)),
        ("🎓 Course Recommendations",   bool(recs)),
        ("⬇ Download Report",           bool(recs)),
    ]

    st.markdown("**Your Progress**")
    for label, done in steps_status:
        icon = "✅" if done else "⬜"
        st.markdown(f"{icon} {label}")

    st.divider()

    # Candidate info display
    name  = SM.get_employee_name()
    email = SM.get_employee_email()
    if name:
        st.markdown(f"👤 **{name}**")
    if email:
        st.caption(email)

    if match_result:
        cat   = match_result.get("category", "")
        score = match_result.get("match_score", 0)
        st.markdown(f"🎯 **{cat}**")
        st.caption(f"Match score: {score:.1f}%")

    st.divider()

    # Reset button
    if st.button("🔄 Start Over", use_container_width=True):
        SM.reset()
        st.rerun()

    st.divider()
    st.caption(config.APP_DESCRIPTION)

# ── Landing page ──────────────────────────────────────────────────────────────
st.title(f"{config.APP_ICON} {config.APP_TITLE}")
st.markdown(config.APP_DESCRIPTION)
st.divider()

# Flow overview
col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
steps_info = [
    ("📄", "Upload", "PDF / TXT / DOCX"),
    ("🔍", "Match",  "Skills vs 10 categories"),
    ("📝", "Quiz",   "5 Qs per skill"),
    ("📊", "Scores", "Per-skill %"),
    ("📈", "Analyse","Visual charts"),
    ("🎓", "Learn",  "Course links"),
    ("⬇",  "Export", "PDF report"),
]
for col, (icon, label, sub) in zip(
    [col1, col2, col3, col4, col5, col6, col7], steps_info
):
    with col:
        st.markdown(
            f"<div style='text-align:center; border:1px solid #D3D1C7; "
            f"border-radius:8px; padding:12px 6px;'>"
            f"<div style='font-size:24px;'>{icon}</div>"
            f"<div style='font-weight:600; font-size:13px; margin-top:4px;'>{label}</div>"
            f"<div style='color:#888; font-size:11px;'>{sub}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

st.divider()

# CTA button
if st.button("🚀 Start Assessment", type="primary", use_container_width=False):
    st.switch_page("pages/1_upload_resume.py")

logger.info("App loaded — session initialised.")