"""
pages/3_quiz.py
---------------
Page 3 — Quiz

Presents 5 scenario-based MCQ questions per matching skill.
Navigation: Previous / Next / Submit.
Tracks answers in session state.
On completion routes to Page 4 (Score Report).
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
from config import APP_ICON, QUESTIONS_PER_SKILL
from modules.quiz_engine   import QuizEngine
from modules.session_state import SessionStateManager as SM
from utils.logger          import get_logger

logger = get_logger(__name__)

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Quiz | Skill Assessment",
    page_icon=APP_ICON,
    layout="centered",
)

SM.init()

# ── Guard ──────────────────────────────────────────────────────────────────────
match_result = SM.get_match_result()
if not match_result:
    st.warning("⚠️ Please complete Pages 1 and 2 first.")
    if st.button("← Go to Upload"):
        st.switch_page("pages/1_upload_resume.py")
    st.stop()

matching_skills = match_result.get("matching_skills", [])

if not matching_skills:
    st.info("No matching skills to quiz. Redirecting to courses…")
    st.switch_page("pages/6_courses.py")
    st.stop()

# ── Build quiz if not already built ───────────────────────────────────────────
if not SM.get_quiz_questions():
    engine    = QuizEngine()
    questions = engine.build_quiz(matching_skills, QUESTIONS_PER_SKILL)
    SM.set_quiz_questions(questions)
    SM.set_quiz_current_idx(0)
    logger.info("Quiz built: %d questions.", len(questions))

questions   = SM.get_quiz_questions()
total_q     = len(questions)
answers     = SM.get_quiz_answers()
current_idx = SM.get_quiz_current_idx()

# ── If already complete, redirect ─────────────────────────────────────────────
if SM.is_quiz_complete():
    st.success("✅ Quiz already completed!")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("View Score Report", type="primary", use_container_width=True):
            st.switch_page("pages/4_score_report.py")
    with col2:
        if st.button("Retake Quiz", use_container_width=True):
            SM.set_quiz_complete(False)
            SM.set_quiz_current_idx(0)
            st.session_state[__import__("config").SessionKeys.QUIZ_ANSWERS] = {}
            st.rerun()
    st.stop()

# ── Header ─────────────────────────────────────────────────────────────────────
st.title("📝 Skill Quiz")
name = SM.get_employee_name() or "Candidate"
st.caption(f"Assessment for **{name}**")

# ── Progress bar ───────────────────────────────────────────────────────────────
answered  = sum(1 for q in questions if q["id"] in answers)
progress  = answered / total_q if total_q else 0
st.progress(progress, text=f"Progress: {answered}/{total_q} questions answered")

# ── Skill section label ────────────────────────────────────────────────────────
current_q = questions[current_idx]
current_skill = current_q.get("skill", "")

# Show skill group heading when skill changes
if current_idx == 0 or questions[current_idx - 1].get("skill") != current_skill:
    st.markdown(
        f"<div style='background:#EEEDFE; border-left:4px solid #534AB7; "
        f"padding:8px 14px; border-radius:4px; margin-bottom:8px;'>"
        f"<b>Skill:</b> {current_skill}</div>",
        unsafe_allow_html=True,
    )

# ── Question card ──────────────────────────────────────────────────────────────
q_id       = current_q["id"]
q_text     = current_q["question"]
options    = current_q.get("options", {})
saved_ans  = answers.get(q_id, None)

st.markdown(f"**Question {current_idx + 1} of {total_q}**")
st.markdown(
    f"<div style='border:1px solid #D3D1C7; border-radius:8px; "
    f"padding:18px; margin:8px 0; background:var(--background-color)'>"
    f"<p style='font-size:15px; margin:0'>{q_text}</p>"
    f"</div>",
    unsafe_allow_html=True,
)

# ── Option radio ───────────────────────────────────────────────────────────────
# Build option labels from dict (A: "text", B: "text", etc.)
option_labels = [f"{key}. {value}" for key, value in options.items()]

selected = st.radio(
    "Choose your answer:",
    options=option_labels,
    index=None if saved_ans is None else next(
        (i for i, o in enumerate(option_labels) if o.startswith(saved_ans + ".")),
        None
    ),
    key=f"radio_{q_id}",
    label_visibility="collapsed",
)

# Save answer when user selects an option
if selected:
    letter = selected.split(".")[0].strip()  # Extract "A", "B", etc.
    SM.set_quiz_answer(q_id, letter)
    answers = SM.get_quiz_answers()

# ── Show feedback if answered ──────────────────────────────────────────────────
if q_id in answers:
    chosen  = answers[q_id]
    correct = current_q["answer"].strip().upper()
    explanation = current_q.get("explanation", "")

    if chosen == correct:
        st.success(f"✅ Correct! Option **{correct}**")
    else:
        st.error(f"❌ Incorrect. You chose **{chosen}**, correct answer is **{correct}**")

    if explanation:
        with st.expander("💡 Explanation"):
            st.write(explanation)

st.divider()

# ── Navigation buttons ─────────────────────────────────────────────────────────
nav_prev, nav_counter, nav_next = st.columns([1, 2, 1])

with nav_prev:
    if st.button("← Previous", disabled=(current_idx == 0), use_container_width=True):
        SM.set_quiz_current_idx(current_idx - 1)
        st.rerun()

with nav_counter:
    st.markdown(
        f"<p style='text-align:center; color:#888; margin-top:8px;'>"
        f"{current_idx + 1} / {total_q}</p>",
        unsafe_allow_html=True,
    )

with nav_next:
    is_last = current_idx == total_q - 1
    all_answered = len(answers) == total_q

    if is_last:
        if all_answered:
            if st.button("Submit Quiz ✓", type="primary", use_container_width=True):
                SM.set_quiz_complete(True)
                st.switch_page("pages/4_score_report.py")
        else:
            remaining = total_q - len(answers)
            st.button(
                f"Submit Quiz ({remaining} unanswered)",
                disabled=True,
                use_container_width=True,
            )
            st.caption(f"Answer {remaining} more question(s) to submit.")
    else:
        if st.button("Next →", use_container_width=True, type="primary"):
            SM.set_quiz_current_idx(current_idx + 1)
            st.rerun()

# ── Quick navigation pills ─────────────────────────────────────────────────────
st.divider()
st.caption("Quick navigation — jump to any question:")

pill_cols = st.columns(min(total_q, 10))
for i, col in enumerate(pill_cols[:total_q]):
    q = questions[i]
    is_answered = q["id"] in answers
    is_current  = i == current_idx
    bg    = "#534AB7" if is_current else "#9FE1CB" if is_answered else "#F1EFE8"
    color = "#fff" if is_current else "#085041" if is_answered else "#5F5E5A"
    with col:
        if st.button(
            str(i + 1),
            key=f"pill_{i}",
            help=f"Q{i+1}: {questions[i].get('skill','')}"
        ):
            SM.set_quiz_current_idx(i)
            st.rerun()