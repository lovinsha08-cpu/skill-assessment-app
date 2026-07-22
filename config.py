"""
config.py
---------
Central configuration for the Skill Assessment App.
All paths, thresholds, and app-wide settings live here.
"""

import os
from pathlib import Path

# ── Base paths ────────────────────────────────────────────────
BASE_DIR  = Path(__file__).resolve().parent
DATA_DIR  = BASE_DIR / "data"
STATIC_DIR = BASE_DIR / "static"

# ── Dataset file paths ────────────────────────────────────────
SKILLS_REFERENCE_PATH = DATA_DIR / "skills_reference.py"
RESUMES_CSV_PATH      = DATA_DIR / "ev_resumes.csv"
QUIZ_JSON_PATH        = DATA_DIR / "all_skills_quiz.json"
COURSES_JSON_PATH     = DATA_DIR / "courses_all_skills.json"

# ── App metadata ──────────────────────────────────────────────
APP_TITLE       = "Skill Assessment & Career Recommender"
APP_ICON        = "🎯"
APP_VERSION     = "1.0.0"
APP_DESCRIPTION = (
    "Upload your resume → get job category prediction → "
    "take a skill quiz → view your score dashboard → "
    "receive personalised course recommendations."
)

# ── Quiz settings ─────────────────────────────────────────────
QUESTIONS_PER_SKILL = 5          # questions per matching skill
MAX_QUIZ_SKILLS     = 4          # maximum skills quizzed per session

# ── Score thresholds (%) → course level ───────────────────────
SCORE_BEGINNER_MAX     = 40      # < 40%  → beginner course
SCORE_INTERMEDIATE_MAX = 60      # 40–59% → intermediate course
SCORE_ADVANCED_MAX     = 80      # 60–79% → advanced course
SCORE_MASTERY          = 80      # ≥ 80%  → no course needed (mastery)

SCORE_LEVELS = {
    "beginner":     (0,  SCORE_BEGINNER_MAX),
    "intermediate": (SCORE_BEGINNER_MAX,  SCORE_INTERMEDIATE_MAX),
    "advanced":     (SCORE_INTERMEDIATE_MAX, SCORE_ADVANCED_MAX),
    "mastery":      (SCORE_ADVANCED_MAX, 101),
}

SCORE_LEVEL_LABELS = {
    "beginner":     "🟥 Beginner",
    "intermediate": "🟧 Intermediate",
    "advanced":     "🟨 Advanced",
    "mastery":      "🟩 Mastery",
}

SCORE_COLORS = {
    "beginner":     "#E24B4A",
    "intermediate": "#FFC107",
    "advanced":     "#4CAF50",
    "mastery":      "#9C27B0",
}

# ── Recommendation logic ──────────────────────────────────────
# Missing skill → always recommend beginner
# Matching skill → recommend based on quiz score
MISSING_SKILL_COURSE_LEVEL = "beginner"

# ── PDF export ────────────────────────────────────────────────
PDF_OUTPUT_DIR  = BASE_DIR / "static"
PDF_FILE_NAME   = "skill_assessment_report.pdf"

# ── Supported resume file types ───────────────────────────────
ALLOWED_RESUME_TYPES = ["pdf", "txt", "docx"]

# ── Session state keys ────────────────────────────────────────
class SessionKeys:
    UPLOADED_FILE     = "uploaded_file"
    PARSED_SKILLS     = "parsed_skills"
    MATCH_RESULT      = "match_result"          # dict from skill_matcher
    QUIZ_QUESTIONS    = "quiz_questions"        # list of question dicts
    QUIZ_ANSWERS      = "quiz_answers"          # {q_id: selected_option}
    QUIZ_CURRENT_IDX  = "quiz_current_idx"
    QUIZ_COMPLETE     = "quiz_complete"
    SKILL_SCORES      = "skill_scores"          # {skill: score_pct}
    RECOMMENDATIONS   = "recommendations"       # list of course dicts
    EMPLOYEE_NAME     = "employee_name"
    EMPLOYEE_EMAIL    = "employee_email"
