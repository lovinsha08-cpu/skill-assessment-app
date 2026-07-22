"""
pages/1_upload_resume.py
------------------------
Page 1 — Upload Resume

User uploads a PDF / TXT / DOCX resume.
The app extracts text, matches skills against skills_reference.py,
and stores results in session state before routing to Page 2.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
from config import SessionKeys, APP_ICON
from modules.resume_parser  import ResumeParser
from modules.skill_matcher  import SkillMatcher
from modules.session_state  import SessionStateManager as SM
from utils.validators       import is_valid_resume_file, is_valid_email, is_non_empty_string
from utils.logger           import get_logger

# Load data
import json
from data.skills_reference import SKILLS_REFERENCE, ALL_SKILLS

logger = get_logger(__name__)

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Upload Resume | Skill Assessment",
    page_icon=APP_ICON,
    layout="centered",
)

SM.init()

# ── Header ─────────────────────────────────────────────────────────────────────
st.title(f"{APP_ICON} Skill Assessment & Career Recommender")
st.markdown(
    "Upload your resume to get your **predicted job category**, "
    "**skill gap analysis**, a **personalised quiz**, and **course recommendations**."
)
st.divider()

# ── Step indicator ─────────────────────────────────────────────────────────────
steps = ["📄 Upload", "🔍 Skills", "📝 Quiz", "📊 Scores", "📈 Dashboard", "🎓 Courses", "⬇ Download"]
cols  = st.columns(len(steps))
for i, (col, label) in enumerate(zip(cols, steps)):
    if i == 0:
        col.markdown(f"**{label}**")
    else:
        col.markdown(f"<span style='color:#888'>{label}</span>", unsafe_allow_html=True)

st.divider()

# ── Candidate info form ────────────────────────────────────────────────────────
st.subheader("👤 Your Details")

col1, col2 = st.columns(2)
with col1:
    name = st.text_input(
        "Full Name",
        value=SM.get_employee_name(),
        placeholder="e.g. Arun Sharma",
    )
with col2:
    email = st.text_input(
        "Email Address",
        value=SM.get_employee_email(),
        placeholder="e.g. arun@email.com",
    )

# ── File uploader ──────────────────────────────────────────────────────────────
st.subheader("📄 Upload Resume")
st.caption("Supported formats: PDF, TXT, DOCX — Max size: 5 MB")

uploaded_file = st.file_uploader(
    label="Drag and drop or click to browse",
    type=["pdf", "txt", "docx"],
    help="Your resume will be scanned for known technical and professional skills.",
)

# ── Demo mode: pick from ev_resumes.csv ───────────────────────────────────────
st.markdown("---")
st.subheader("🧪 Or Use a Demo Resume")
st.caption("Select an employee from the sample dataset to pre-fill the assessment.")

import pandas as pd
from config import RESUMES_CSV_PATH

try:
    df_demo = pd.read_csv(RESUMES_CSV_PATH)
    demo_names = ["— Select a demo employee —"] + df_demo["full_name"].tolist()
    demo_choice = st.selectbox("Demo Employees", demo_names)
except Exception:
    demo_choice = "— Select a demo employee —"
    df_demo     = pd.DataFrame()

# ── Analyse button ─────────────────────────────────────────────────────────────
st.divider()

analyse_clicked = st.button(
    "🔍 Analyse Resume",
    type="primary",
    use_container_width=True,
    disabled=(uploaded_file is None and demo_choice == "— Select a demo employee —"),
)

if analyse_clicked:

    # ── Validate inputs ────────────────────────────────────────────────────────
    errors = []
    if not is_non_empty_string(name):
        errors.append("Please enter your full name.")
    if email and not is_valid_email(email):
        errors.append("Please enter a valid email address.")

    if errors:
        for err in errors:
            st.error(err)
        st.stop()

    SM.set_employee_info(name.strip(), email.strip())

    # ── Demo path ──────────────────────────────────────────────────────────────
    if demo_choice != "— Select a demo employee —" and not uploaded_file:
        row = df_demo[df_demo["full_name"] == demo_choice].iloc[0]
        raw_skills = [s.strip() for s in row["skills_present"].split("|") if s.strip()]  # type: ignore
        # Include missing skills in the full text so the parser can find them
        full_skills_text = "|".join(
            raw_skills + [s.strip() for s in row["missing_skills"].split("|") if s.strip()]  # type: ignore
        )

        # Simulate parsed skills = skills_present only (as if reading the resume)
        parsed_skills = raw_skills
        SM.set_parsed_skills(parsed_skills)
        SM.set_employee_info(row["full_name"], row["email"])  # type: ignore

        matcher  = SkillMatcher(SKILLS_REFERENCE)
        result   = matcher.match(parsed_skills)
        SM.set_match_result(result)

        logger.info("Demo employee selected: %s", demo_choice)
        st.success(f"✅ Demo resume loaded for **{row['full_name']}**.")  # type: ignore
        st.switch_page("pages/2_skill_results.py")

    # ── Real file upload path ──────────────────────────────────────────────────
    elif uploaded_file:
        if not is_valid_resume_file(uploaded_file.name):
            st.error("Unsupported file type. Please upload PDF, TXT, or DOCX.")
            st.stop()

        with st.spinner("Parsing your resume…"):
            file_bytes = uploaded_file.read()
            parser     = ResumeParser(ALL_SKILLS)
            parsed     = parser.extract_skills(file_bytes, uploaded_file.name)

        if not parsed:
            st.warning(
                "⚠️ No known skills were detected in your resume. "
                "Make sure the file contains readable text. "
                "Try the demo mode to see how the app works."
            )
            st.stop()

        SM.set_parsed_skills(parsed)
        SM.set_uploaded_file(uploaded_file.name)

        matcher = SkillMatcher(SKILLS_REFERENCE)
        result  = matcher.match(parsed)
        SM.set_match_result(result)

        logger.info(
            "Uploaded resume: %d skills found, predicted: %s",
            len(parsed),
            result["category"],
        )
        st.success(f"✅ Resume parsed! Found **{len(parsed)} skills**.")
        st.switch_page("pages/2_skill_results.py")

# ── Footer hint ────────────────────────────────────────────────────────────────
with st.expander("ℹ️ How does this work?"):
    st.markdown("""
**Step 1 — Upload:** Your resume is scanned for technical skills.

**Step 2 — Match:** We compare your skills against 10 job categories and identify gaps.

**Step 3 — Quiz:** You answer 5 scenario-based questions per matched skill.

**Step 4 — Scores:** Per-skill scores are calculated with level badges.

**Step 5 — Dashboard:** Visual analytics of your performance.

**Step 6 — Courses:** Personalised course links at the right level for each skill.

**Step 7 — Download:** Export your full report as a PDF.
    """)