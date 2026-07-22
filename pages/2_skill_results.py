"""
pages/2_skill_results.py
------------------------
Page 2 — Skill Results

Displays:
  - Predicted job category with match score
  - Matching skills (green chips)
  - Missing skills (red chips)
  - Top 3 alternative category matches
  - Proceed to Quiz button
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
from config import APP_ICON
from modules.session_state import SessionStateManager as SM
from modules.skill_matcher import SkillMatcher
from utils.logger import get_logger

from data.skills_reference import SKILLS_REFERENCE

logger = get_logger(__name__)

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Skill Results | Skill Assessment",
    page_icon=APP_ICON,
    layout="wide",
)

SM.init()

# ── Guard: must have match result ──────────────────────────────────────────────
match_result = SM.get_match_result()
if not match_result:
    st.warning("⚠️ No resume data found. Please go back to Page 1 and upload your resume.")
    if st.button("← Back to Upload"):
        st.switch_page("pages/1_upload_resume.py")
    st.stop()

# ── Unpack result ──────────────────────────────────────────────────────────────
category        = match_result["category"]
matching_skills = match_result["matching_skills"]
missing_skills  = match_result["missing_skills"]
match_score     = match_result["match_score"]
name            = SM.get_employee_name() or "Candidate"

# ── Header ─────────────────────────────────────────────────────────────────────
st.title("🔍 Your Skill Results")
st.caption(f"Assessment for **{name}**")
st.divider()

# ── Predicted job category card ────────────────────────────────────────────────
col_cat, col_score = st.columns([3, 1])

with col_cat:
    st.subheader("🎯 Predicted Job Category")
    st.markdown(
        f"<h2 style='color:#534AB7; margin:0'>{category}</h2>",
        unsafe_allow_html=True,
    )
    st.caption("Based on the skills found in your resume")

with col_score:
    st.subheader("Match Score")
    score_color = "#1D9E75" if match_score >= 75 else "#EF9F27" if match_score >= 50 else "#E24B4A"
    st.markdown(
        f"<h2 style='color:{score_color}; margin:0'>{match_score:.1f}%</h2>",
        unsafe_allow_html=True,
    )
    st.caption(f"{len(matching_skills)} of {len(matching_skills)+len(missing_skills)} skills matched")

st.divider()

# ── Skills side by side ────────────────────────────────────────────────────────
col_match, col_miss = st.columns(2)

# Skill chip helper
def skill_chip(skill: str, color: str, bg: str) -> str:
    return (
        f"<span style='background:{bg}; color:{color}; "
        f"padding:4px 12px; border-radius:20px; "
        f"font-size:13px; font-weight:500; "
        f"display:inline-block; margin:3px;'>"
        f"{skill}</span>"
    )

with col_match:
    st.subheader(f"✅ Matching Skills ({len(matching_skills)})")
    if matching_skills:
        chips = " ".join(skill_chip(s, "#085041", "#9FE1CB") for s in matching_skills)
        st.markdown(chips, unsafe_allow_html=True)
        st.caption("These skills will be tested in the quiz.")
    else:
        st.info("No matching skills found for this category.")

with col_miss:
    st.subheader(f"❌ Missing Skills ({len(missing_skills)})")
    if missing_skills:
        chips = " ".join(skill_chip(s, "#791F1F", "#F7C1C1") for s in missing_skills)
        st.markdown(chips, unsafe_allow_html=True)
        st.caption("Beginner-level courses will be recommended for these skills.")
    else:
        st.success("🎉 You have all required skills for this category!")

st.divider()

# ── Skill requirements for category ───────────────────────────────────────────
with st.expander(f"📋 All required skills for {category}"):
    required = SKILLS_REFERENCE.get(category, [])
    for skill in required:
        icon = "✅" if skill in matching_skills else "❌"
        st.markdown(f"{icon} **{skill}**")

# ── Alternative categories ─────────────────────────────────────────────────────
st.subheader("🔄 Other Close Matches")
parsed_skills = SM.get_parsed_skills()
matcher       = SkillMatcher(SKILLS_REFERENCE)
top_3         = matcher.top_n_categories(parsed_skills, n=4)

# Skip the top match (already displayed)
alt_matches = [m for m in top_3 if m["category"] != category][:3]

if alt_matches:
    alt_cols = st.columns(len(alt_matches))
    for col, match in zip(alt_cols, alt_matches):
        with col:
            pct = match["score_pct"]
            bar_color = "#1D9E75" if pct >= 75 else "#EF9F27" if pct >= 50 else "#E24B4A"
            st.markdown(
                f"<div style='border:1px solid #D3D1C7; border-radius:8px; "
                f"padding:12px; text-align:center;'>"
                f"<div style='font-weight:500; font-size:14px;'>{match['category']}</div>"
                f"<div style='color:{bar_color}; font-size:22px; font-weight:600;'>{pct:.1f}%</div>"
                f"<div style='color:#888; font-size:12px;'>match score</div>"
                f"</div>",
                unsafe_allow_html=True,
            )
else:
    st.caption("No significant alternative matches found.")

st.divider()

# ── What happens next info ─────────────────────────────────────────────────────
if matching_skills:
    st.info(
        f"📝 **Next step:** You will answer **{len(matching_skills) * 5} questions** "
        f"({len(matching_skills)} skills × 5 questions each) to test your practical knowledge."
    )
else:
    st.warning(
        "No matching skills were detected. You can still proceed — "
        "you will receive beginner course recommendations for all required skills."
    )

# ── Navigation ─────────────────────────────────────────────────────────────────
col_back, col_next = st.columns([1, 3])

with col_back:
    if st.button("← Back to Upload", use_container_width=True):
        st.switch_page("pages/1_upload_resume.py")

with col_next:
    btn_label = (
        f"Start Quiz ({len(matching_skills)} skills × 5 questions) →"
        if matching_skills
        else "Skip to Courses →"
    )
    if st.button(btn_label, type="primary", use_container_width=True):
        if matching_skills:
            st.switch_page("pages/3_quiz.py")
        else:
            st.switch_page("pages/6_courses.py")