"""
pages/6_courses.py
------------------
Page 6 — Course Recommendations

Logic:
  • Missing skills   → always Beginner courses
  • Score < 40%      → Beginner courses
  • 40% ≤ score < 60% → Intermediate courses
  • 60% ≤ score < 80% → Advanced courses
  • score ≥ 80%      → No recommendation (Mastery)

Each course card shows: title, platform, instructor, duration,
price, level badge, and a clickable direct link.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
from config import APP_ICON
from modules.recommender   import Recommender
from modules.session_state import SessionStateManager as SM
from utils.logger          import get_logger

logger = get_logger(__name__)

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Courses | Skill Assessment",
    page_icon=APP_ICON,
    layout="wide",
)

SM.init()

# ── Gather data ────────────────────────────────────────────────────────────────
match_result = SM.get_match_result()
skill_scores = SM.get_skill_scores()

if not match_result:
    st.warning("⚠️ No assessment data. Please start from Page 1.")
    if st.button("← Start Over"):
        st.switch_page("pages/1_upload_resume.py")
    st.stop()

missing_skills = match_result.get("missing_skills", [])

# ── Build recommendations ──────────────────────────────────────────────────────
try:
    rec    = Recommender()
    if not rec._courses:
        st.error("Course data not available. Please contact support.")
        st.stop()
    plans  = rec.recommend(missing_skills, skill_scores)
except Exception as e:
    st.error(f"Error generating recommendations: {e}")
    st.stop()

# Persist for PDF generation
SM.set_recommendations(plans)

# ── Header ─────────────────────────────────────────────────────────────────────
name = SM.get_employee_name() or "Candidate"
cat  = match_result.get("category", "")

st.title("🎓 Course Recommendations")
st.caption(f"Personalised learning plan for **{name}** — {cat}")
st.divider()

# ── Summary strip ──────────────────────────────────────────────────────────────
total_courses = sum(len(p["courses"]) for p in plans)
skill_count   = len(plans)

col_a, col_b, col_c = st.columns(3)
col_a.metric("Skills with Recommendations", skill_count)
col_b.metric("Total Courses Recommended",   total_courses)
col_c.metric("Missing Skills (Beginner)",   len(missing_skills))

st.divider()

# ── Level badge helper ─────────────────────────────────────────────────────────
_BADGE = {
    "beginner":     ("#FCEBEB", "#791F1F", "🟥 Beginner"),
    "intermediate": ("#FAEEDA", "#633806", "🟧 Intermediate"),
    "advanced":     ("#EAF3DE", "#173404", "🟨 Advanced"),
    "mastery":      ("#E1F5EE", "#04342C", "🟩 Mastery"),
}

def level_badge(level: str) -> str:
    bg, fg, label = _BADGE.get(level, ("#F1EFE8", "#2C2C2A", level.capitalize()))
    return (
        f"<span style='background:{bg}; color:{fg}; "
        f"padding:2px 10px; border-radius:12px; "
        f"font-size:12px; font-weight:500;'>{label}</span>"
    )

# ── Course card helper ─────────────────────────────────────────────────────────
def course_card(course: dict, level: str) -> None:
    bg, fg, badge_label = _BADGE.get(level, ("#F1EFE8", "#2C2C2A", level.capitalize()))
    free_tag = (
        "<span style='background:#E1F5EE; color:#04342C; "
        "padding:2px 8px; border-radius:10px; font-size:11px;'>Free</span>"
        if "free" in course.get("price", "").lower()
        else ""
    )
    st.markdown(
        f"<div style='border:1px solid #D3D1C7; border-radius:10px; "
        f"padding:16px 18px; margin-bottom:10px;'>"
        f"<div style='display:flex; justify-content:space-between; align-items:flex-start;'>"
        f"<div style='font-size:15px; font-weight:600; flex:1;'>{course['title']}</div>"
        f"<div style='display:flex; gap:6px; margin-left:12px; flex-shrink:0;'>"
        f"{level_badge(level)} {free_tag}</div>"
        f"</div>"
        f"<div style='color:#5F5E5A; font-size:13px; margin-top:6px;'>"
        f"🎓 {course['platform']} &nbsp;|&nbsp; "
        f"👤 {course.get('instructor','—')} &nbsp;|&nbsp; "
        f"⏱ {course.get('duration','—')} &nbsp;|&nbsp; "
        f"💰 {course.get('price','—')}"
        f"</div>"
        f"<div style='color:#444; font-size:13px; margin-top:8px; line-height:1.5;'>"
        f"{course.get('description','')}</div>"
        f"<div style='margin-top:10px;'>"
        f"<a href='{course['url']}' target='_blank' "
        f"style='background:#534AB7; color:#fff; padding:6px 16px; "
        f"border-radius:6px; font-size:13px; text-decoration:none; "
        f"font-weight:500;'>🔗 Open Course</a>"
        f"</div>"
        f"</div>",
        unsafe_allow_html=True,
    )

# ── Render each skill's recommendations ───────────────────────────────────────
if not plans:
    st.success(
        "🎉 Excellent work! You have mastered all your matching skills (≥80%). "
        "No course recommendations needed at this time."
    )
else:
    # Tabs: one per skill
    skill_labels = [
        f"{'🔴' if p['reason']=='missing' else '🟡'} {p['skill']}"
        for p in plans
    ]
    tabs = st.tabs(skill_labels)

    for tab, plan in zip(tabs, plans):
        with tab:
            skill    = plan["skill"]
            level    = plan["level"]
            reason   = plan["reason"]
            score_pct = plan.get("score_pct")
            courses  = plan.get("courses", [])

            # Reason banner
            if reason == "missing":
                st.markdown(
                    f"<div style='background:#FCEBEB; border-left:4px solid #E24B4A; "
                    f"padding:10px 14px; border-radius:4px; margin-bottom:12px;'>"
                    f"<b>Missing Skill</b> — This skill was not found in your resume. "
                    f"Beginner courses will help you build a foundation.</div>",
                    unsafe_allow_html=True,
                )
            else:
                score_display = f"{score_pct:.1f}%" if score_pct is not None else "—"
                banner_colors = {
                    "score_beginner":     ("#FCEBEB", "#E24B4A"),
                    "score_intermediate": ("#FAEEDA", "#EF9F27"),
                    "score_advanced":     ("#EAF3DE", "#639922"),
                }.get(reason, ("#F1EFE8", "#888780"))
                st.markdown(
                    f"<div style='background:{banner_colors[0]}; "
                    f"border-left:4px solid {banner_colors[1]}; "
                    f"padding:10px 14px; border-radius:4px; margin-bottom:12px;'>"
                    f"<b>Quiz Score: {score_display}</b> — "
                    f"{level.capitalize()} level courses recommended.</div>",
                    unsafe_allow_html=True,
                )

            if courses:
                st.markdown(f"**{len(courses)} courses recommended:**")
                for course in courses:
                    course_card(course, level)
            else:
                st.warning(f"No courses found for **{skill}** at {level} level.")

# ── Legend ─────────────────────────────────────────────────────────────────────
st.divider()
with st.expander("📖 Recommendation Logic"):
    st.markdown("""
| Score Range | Recommended Level |
|---|---|
| Skill missing from resume | 🟥 Beginner |
| Quiz score < 40% | 🟥 Beginner |
| Quiz score 40% – 59% | 🟧 Intermediate |
| Quiz score 60% – 79% | 🟨 Advanced |
| Quiz score ≥ 80% | 🟩 No course needed (Mastery) |
    """)

# ── Navigation ─────────────────────────────────────────────────────────────────
st.divider()
col_back, col_next = st.columns([1, 3])

with col_back:
    if st.button("← Dashboard", use_container_width=True):
        st.switch_page("pages/5_dashboard.py")

with col_next:
    if st.button("⬇ Download Full Report (PDF) →", type="primary", use_container_width=True):
        st.switch_page("pages/7_download.py")