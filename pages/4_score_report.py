"""
pages/4_score_report.py
-----------------------
Page 4 — Score Report

Displays per-skill score cards with:
  - Score percentage
  - Level badge (Beginner / Intermediate / Advanced / Mastery)
  - Correct / Total count
  - Question-level breakdown (expandable)
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
from config import APP_ICON
from modules.scorer        import Scorer
from modules.session_state import SessionStateManager as SM
from utils.helpers         import format_score_badge
from utils.logger          import get_logger

logger = get_logger(__name__)

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Score Report | Skill Assessment",
    page_icon=APP_ICON,
    layout="wide",
)

SM.init()

# ── Guard ──────────────────────────────────────────────────────────────────────
if not SM.is_quiz_complete():
    st.warning("⚠️ Please complete the quiz first.")
    if st.button("← Go to Quiz"):
        st.switch_page("pages/3_quiz.py")
    st.stop()

questions = SM.get_quiz_questions()
answers   = SM.get_quiz_answers()

if not questions:
    st.error("No quiz data found. Please restart the assessment.")
    st.stop()

# ── Evaluate scores ────────────────────────────────────────────────────────────
try:
    scorer       = Scorer()
    skill_scores = scorer.evaluate(questions, answers)
    summary      = scorer.summary(skill_scores)
    overall      = summary.get("overall_score", 0.0)
except Exception as e:
    st.error(f"Error calculating scores: {e}")
    st.error("Please try retaking the quiz or contact support.")
    st.stop()

# Persist scores for later pages
SM.set_skill_scores(skill_scores)

logger.info(
    "Score report: overall=%.1f%%, skills=%s",
    overall,
    list(skill_scores.keys()),
)

# ── Header ─────────────────────────────────────────────────────────────────────
st.title("📊 Score Report")
name = SM.get_employee_name() or "Candidate"
st.caption(f"Assessment for **{name}**")
st.divider()

# ── Overall score banner ───────────────────────────────────────────────────────
from utils.helpers import get_score_color, get_score_level
overall_color = get_score_color(overall)
overall_level = get_score_level(overall).capitalize()

st.markdown(
    f"<div style='background: linear-gradient(135deg, #E8F4FD, #B3E0F7); border-radius:12px; padding:20px 28px; "
    f"display:flex; align-items:center; gap:24px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>"
    f"<div>"
    f"<div style='font-size:13px; color:#0A7BC4; font-weight:500;'>Overall Score</div>"
    f"<div style='font-size:42px; font-weight:700; color:{overall_color}; line-height:1.1;'>"
    f"{overall:.1f}%</div>"
    f"<div style='font-size:14px; color:#085A94;'>{overall_level} level</div>"
    f"</div>"
    f"<div style='flex:1; border-left:2px solid #7EC9F1; padding-left:24px;'>"
    f"<div style='font-size:13px; color:#0A4068;'>"
    f"✅ Skills mastered: <b>{len(summary.get('skills_mastered',[]))}</b> &nbsp;|&nbsp; "
    f"📈 Skills to improve: <b>{len(summary.get('skills_to_improve',[]))}</b>"
    f"</div>"
    f"<div style='font-size:13px; color:#0A4068; margin-top:6px;'>"
    f"💪 Strongest: <b>{summary.get('strongest_skill','—')}</b> &nbsp;|&nbsp; "
    f"🎯 Needs work: <b>{summary.get('weakest_skill','—')}</b>"
    f"</div>"
    f"</div>"
    f"</div>",
    unsafe_allow_html=True,
)

st.divider()

# ── Per-skill score cards ──────────────────────────────────────────────────────
st.subheader("Per-Skill Results")

# Layout: 2 cards per row
skill_list = list(skill_scores.items())
for row_start in range(0, len(skill_list), 2):
    row_items = skill_list[row_start : row_start + 2]
    cols = st.columns(len(row_items))

    for col, (skill, data) in zip(cols, row_items):
        with col:
            score_pct = data["score_pct"]
            level     = data["level"]
            color     = data["color"]
            correct   = data["correct"]
            total     = data["total"]

            # Level badge colours
            badge_bg = {
                "beginner":     "#FCEBEB",
                "intermediate": "#FFF8E1",
                "advanced":     "#E8F5E8",
                "mastery":      "#F3E5F5",
            }.get(level, "#FAFAFA")

            badge_color = {
                "beginner":     "#791F1F",
                "intermediate": "#FF8F00",
                "advanced":     "#2E7D32",
                "mastery":      "#6A1B9A",
            }.get(level, "#212121")

            # Card background based on level
            card_bg = {
                "beginner":     "linear-gradient(135deg, #FCEBEB, #F8DADA)",
                "intermediate": "linear-gradient(135deg, #FFF8E1, #FFF3C4)",
                "advanced":     "linear-gradient(135deg, #E8F5E8, #D4EDDA)",
                "mastery":      "linear-gradient(135deg, #F3E5F5, #E9D4F0)",
            }.get(level, "#FFFFFF")

            # Score card
            st.markdown(
                f"<div style='background: {card_bg}; border:1px solid #E0E0E0; border-radius:10px; "
                f"padding:18px; margin-bottom:12px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>"
                f"<div style='font-size:15px; font-weight:600; margin-bottom:8px;'>"
                f"{skill}</div>"
                f"<div style='font-size:32px; font-weight:700; color:{color};'>"
                f"{score_pct:.1f}%</div>"
                f"<div style='display:flex; align-items:center; gap:8px; margin-top:6px;'>"
                f"<span style='background:{badge_bg}; color:{badge_color}; "
                f"padding:2px 10px; border-radius:12px; font-size:12px; font-weight:500;'>"
                f"{level.capitalize()}</span>"
                f"<span style='color:#616161; font-size:12px;'>{correct}/{total} correct</span>"
                f"</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

            # Progress bar
            st.progress(score_pct / 100)

            # Expandable question breakdown
            with st.expander(f"View {total} questions"):
                for q_result in data["question_results"]:
                    icon = "✅" if q_result["is_correct"] else "❌"
                    st.markdown(
                        f"{icon} **{q_result['question'][:90]}…**  \n"
                        f"Your answer: **{q_result['selected_answer']}** | "
                        f"Correct: **{q_result['correct_answer']}**"
                    )
                    if not q_result["is_correct"] and q_result["explanation"]:
                        st.caption(f"💡 {q_result['explanation']}")
                    st.divider()

st.divider()

# ── Score band legend ──────────────────────────────────────────────────────────
with st.expander("📖 Score Band Guide"):
    bands = [
        ("🟥 Beginner",     "0 – 39%",   "Beginner courses recommended"),
        ("🟧 Intermediate", "40 – 59%",  "Intermediate courses recommended"),
        ("🟨 Advanced",     "60 – 79%",  "Advanced courses recommended"),
        ("🟩 Mastery",      "80 – 100%", "No course needed — you've mastered this skill!"),
    ]
    for label, rng, desc in bands:
        st.markdown(f"**{label}** ({rng}) — {desc}")

# ── Navigation ─────────────────────────────────────────────────────────────────
col_back, col_dash, col_courses = st.columns(3)

with col_back:
    if st.button("← Back to Quiz", use_container_width=True):
        st.switch_page("pages/3_quiz.py")

with col_dash:
    if st.button("📈 View Dashboard", type="primary", use_container_width=True):
        st.switch_page("pages/5_dashboard.py")

with col_courses:
    if st.button("🎓 Get Course Recommendations →", use_container_width=True):
        st.switch_page("pages/6_courses.py")