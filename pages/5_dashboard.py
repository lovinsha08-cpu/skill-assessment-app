"""
pages/5_dashboard.py
--------------------
Page 5 — Visual Analytics Dashboard

Displays five Plotly charts:
  1. Gauge  — overall score
  2. Radar  — per-skill comparison
  3. Bar    — per-skill horizontal bars with band lines
  4. Pie    — mastered vs to-improve ratio
  5. Heatmap — question-level correctness grid
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
from config import APP_ICON
from modules.dashboard     import DashboardBuilder
from modules.scorer        import Scorer
from modules.session_state import SessionStateManager as SM
from utils.logger          import get_logger

logger = get_logger(__name__)

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard | Skill Assessment",
    page_icon=APP_ICON,
    layout="wide",
)

SM.init()

# ── Guard ──────────────────────────────────────────────────────────────────────
skill_scores = SM.get_skill_scores()

if not skill_scores:
    # Try to rebuild from quiz data
    questions = SM.get_quiz_questions()
    answers   = SM.get_quiz_answers()

    if questions and answers:
        scorer = Scorer()
        skill_scores = scorer.evaluate(questions, answers)
        SM.set_skill_scores(skill_scores)
    else:
        st.warning("⚠️ No score data found. Please complete the quiz first.")
        if st.button("← Go to Quiz"):
            st.switch_page("pages/3_quiz.py")
        st.stop()

if not skill_scores:
    st.error("No skill scores available to display.")
    st.stop()

# ── Compute overall ────────────────────────────────────────────────────────────
scorer  = Scorer()
summary = scorer.summary(skill_scores)
overall = summary.get("overall_score", 0.0)
db      = DashboardBuilder()

name = SM.get_employee_name() or "Candidate"
cat  = SM.get_match_result().get("category", "")

# ── Header ─────────────────────────────────────────────────────────────────────
st.title("📈 Analytics Dashboard")
st.caption(f"**{name}** — {cat}")
st.divider()

# ── Row 1: Gauge + Pie ─────────────────────────────────────────────────────────
col_gauge, col_pie = st.columns(2)

with col_gauge:
    st.subheader("Overall Score")
    try:
        fig_gauge = db.gauge_chart(overall)
        st.plotly_chart(fig_gauge, use_container_width=True)
    except Exception as e:
        st.error(f"Error creating gauge chart: {e}")

with col_pie:
    st.subheader("Mastery Overview")
    try:
        fig_pie = db.pie_chart(skill_scores)
        st.plotly_chart(fig_pie, use_container_width=True)
    except Exception as e:
        st.error(f"Error creating pie chart: {e}")

st.divider()

# ── Row 2: Radar chart ─────────────────────────────────────────────────────────
if len(skill_scores) >= 3:
    st.subheader("Skill Score Radar")
    try:
        fig_radar = db.radar_chart(skill_scores)
        st.plotly_chart(fig_radar, use_container_width=True)
    except Exception as e:
        st.error(f"Error creating radar chart: {e}")
    st.divider()

# ── Row 3: Bar chart ───────────────────────────────────────────────────────────
st.subheader("Per-Skill Scores")
try:
    fig_bar = db.bar_chart(skill_scores)
    st.plotly_chart(fig_bar, use_container_width=True)
except Exception as e:
    st.error(f"Error creating bar chart: {e}")
st.divider()

# ── Row 4: Heatmap ─────────────────────────────────────────────────────────────
st.subheader("Question-Level Correctness")
st.caption("Green = correct  |  Red = incorrect  |  Gray = no question")
try:
    fig_heatmap = db.question_heatmap(skill_scores)
    st.plotly_chart(fig_heatmap, use_container_width=True)
except Exception as e:
    st.error(f"Error creating heatmap: {e}")
st.divider()

# ── Key insights ───────────────────────────────────────────────────────────────
st.subheader("📌 Key Insights")

insight_cols = st.columns(3)

with insight_cols[0]:
    st.metric(
        label="Overall Score",
        value=f"{overall:.1f}%",
        delta=f"{overall - 60:.1f}% vs 60% target",
    )

with insight_cols[1]:
    mastered_count = len(summary.get("skills_mastered", []))
    total_skills   = len(skill_scores)
    st.metric(
        label="Skills Mastered",
        value=f"{mastered_count} / {total_skills}",
    )

with insight_cols[2]:
    strongest = summary.get("strongest_skill", "—")
    weakest   = summary.get("weakest_skill",   "—")
    st.metric(label="Strongest Skill", value=strongest)
    st.metric(label="Needs Most Work", value=weakest)

# ── Navigation ─────────────────────────────────────────────────────────────────
st.divider()
col_back, col_next = st.columns([1, 3])

with col_back:
    if st.button("← Score Report", use_container_width=True):
        st.switch_page("pages/4_score_report.py")

with col_next:
    if st.button("🎓 Get Course Recommendations →", type="primary", use_container_width=True):
        st.switch_page("pages/6_courses.py")