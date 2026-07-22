"""
pages/7_download.py
-------------------
Page 7 — Download Report

Generates a PDF summary of the full assessment and provides
a download button. Also shows a completion summary card and
a "Start Over" button to reset the session.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
from config import APP_ICON
from modules.pdf_generator import PDFGenerator
from modules.scorer        import Scorer
from modules.session_state import SessionStateManager as SM
from utils.logger          import get_logger

logger = get_logger(__name__)

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Download Report | Skill Assessment",
    page_icon=APP_ICON,
    layout="centered",
)

SM.init()

# ── Gather data ────────────────────────────────────────────────────────────────
match_result    = SM.get_match_result()
skill_scores    = SM.get_skill_scores()
recommendations = SM.get_recommendations()
name            = SM.get_employee_name()
email           = SM.get_employee_email()

if not match_result:
    st.warning("⚠️ No assessment data. Please start from Page 1.")
    if st.button("← Start Over"):
        SM.reset()
        st.switch_page("pages/1_upload_resume.py")
    st.stop()

category = match_result.get("category", "")
scorer   = Scorer()
summary  = scorer.summary(skill_scores) if skill_scores else {}
overall  = summary.get("overall_score", 0.0)

# ── Header ─────────────────────────────────────────────────────────────────────
st.title("⬇ Download Your Report")
st.divider()

# ── Completion summary card ────────────────────────────────────────────────────
from utils.helpers import get_score_color, get_score_level
overall_color = get_score_color(overall)
overall_level = get_score_level(overall).capitalize()

st.markdown(
    f"<div style='background:#EEEDFE; border-radius:12px; "
    f"padding:24px; text-align:center; margin-bottom:20px;'>"
    f"<div style='font-size:14px; color:#534AB7; margin-bottom:4px;'>Assessment Complete</div>"
    f"<div style='font-size:28px; font-weight:700; color:#26215C; margin-bottom:4px;'>"
    f"{name or 'Candidate'}</div>"
    f"<div style='font-size:15px; color:#3C3489; margin-bottom:12px;'>{category}</div>"
    f"<div style='font-size:42px; font-weight:700; color:{overall_color};'>{overall:.1f}%</div>"
    f"<div style='font-size:14px; color:#5F5E5A;'>Overall Score — {overall_level}</div>"
    f"</div>",
    unsafe_allow_html=True,
)

# ── Stats row ──────────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("Matching Skills",  len(match_result.get("matching_skills", [])))
c2.metric("Missing Skills",   len(match_result.get("missing_skills",  [])))
c3.metric("Skills Mastered",  len(summary.get("skills_mastered",  [])))
c4.metric("Courses Recommended",
          sum(len(r["courses"]) for r in recommendations) if recommendations else 0)

st.divider()

# ── Generate and offer PDF ─────────────────────────────────────────────────────
st.subheader("📄 PDF Report")
st.caption(
    "Your report includes: candidate details, predicted category, "
    "skill gap summary, per-skill quiz scores, and all course recommendations with links."
)

try:
    with st.spinner("Generating PDF…"):
        gen = PDFGenerator()
        pdf_bytes = gen.build(
            candidate_name  = name,
            candidate_email = email,
            category        = category,
            match_result    = match_result,
            skill_scores    = skill_scores,
            recommendations = recommendations or [],
        )
except Exception as e:
    st.error(f"PDF generation failed: {e}")
    pdf_bytes = None

if pdf_bytes:
    st.download_button(
        label="⬇ Download PDF Report",
        data=pdf_bytes,
        file_name=f"skill_assessment_{(name or 'report').lower().replace(' ','_')}.pdf",
        mime="application/pdf",
        width='stretch',
        type="primary",
    )
    st.success("✅ PDF ready! Click the button above to download.")
else:
    st.error(
        "PDF generation failed. Please check the data and try again."
    )

st.divider()

# ── Quick links to all pages ───────────────────────────────────────────────────
st.subheader("Review Your Results")

nav_cols = st.columns(3)
with nav_cols[0]:
    if st.button("🔍 Skill Results", width='stretch'):
        st.switch_page("pages/2_skill_results.py")
with nav_cols[1]:
    if st.button("📊 Score Report", width='stretch'):
        st.switch_page("pages/4_score_report.py")
with nav_cols[2]:
    if st.button("📈 Dashboard", width='stretch'):
        st.switch_page("pages/5_dashboard.py")

nav_cols2 = st.columns(2)
with nav_cols2[0]:
    if st.button("🎓 Course Recommendations", width='stretch'):
        st.switch_page("pages/6_courses.py")
with nav_cols2[1]:
    if st.button("📝 Retake Quiz", width='stretch'):
        SM.set_quiz_complete(False)
        SM.set_quiz_current_idx(0)
        st.session_state[__import__("config").SessionKeys.QUIZ_ANSWERS] = {}
        SM.set_skill_scores({})
        st.switch_page("pages/3_quiz.py")

st.divider()

# ── Start over ─────────────────────────────────────────────────────────────────
if st.button("🔄 Start a New Assessment", width='stretch'):
    SM.reset()
    st.switch_page("pages/1_upload_resume.py")