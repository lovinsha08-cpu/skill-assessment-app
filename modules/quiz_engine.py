"""
modules/quiz_engine.py
----------------------
Loads quiz questions from all_skills_quiz.json and builds
the question set for the current session based on the candidate's
matching skills.

Provides 5 questions per matching skill (scenario-based, MCQ).
"""

from __future__ import annotations
import json
import random
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config import QUESTIONS_PER_SKILL, QUIZ_JSON_PATH
from utils.logger import get_logger

logger = get_logger(__name__)


class QuizEngine:
    """
    Load questions and build a personalised quiz for a candidate.

    Usage:
        engine    = QuizEngine()
        questions = engine.build_quiz(matching_skills=["Python", "SQL"])
    """

    def __init__(self, quiz_json_path: str | None = None):
        path = quiz_json_path or str(QUIZ_JSON_PATH)
        self._raw: dict = {}
        self._load(path)

    # ── Public API ────────────────────────────────────────────

    def build_quiz(
        self,
        matching_skills: list[str],
        questions_per_skill: int = QUESTIONS_PER_SKILL,
        shuffle: bool = True,
    ) -> list[dict]:
        """
        Build the full quiz question list for the session.

        For each skill in matching_skills, fetch up to
        `questions_per_skill` questions from the JSON dataset.
        Each question dict gets a `skill` key injected so the
        scorer can group results by skill.

        Args:
            matching_skills:      Skills the candidate has (from SkillMatcher).
            questions_per_skill:  How many questions per skill (default 5).
            shuffle:              Randomly shuffle question order.

        Returns:
            Flat list of question dicts, each containing:
              id, question, options, answer, explanation, skill
        """
        questions: list[dict] = []

        for skill in matching_skills:
            skill_qs = self._get_questions_for_skill(skill, questions_per_skill)
            for q in skill_qs:
                q_copy = dict(q)
                q_copy["skill"] = skill  # tag each question with its skill
                questions.append(q_copy)

        if shuffle:
            random.shuffle(questions)

        logger.info(
            "Built quiz: %d questions for %d skills: %s",
            len(questions),
            len(matching_skills),
            matching_skills,
        )
        return questions

    def get_available_skills(self) -> list[str]:
        """Return all skill names present in the quiz dataset."""
        return list(self._raw.get("skills", {}).keys())

    def get_question_count(self, skill: str) -> int:
        """Return how many questions exist for a given skill."""
        return len(self._raw.get("skills", {}).get(skill, []))

    # ── Private helpers ───────────────────────────────────────

    def _load(self, path: str) -> None:
        try:
            with open(path, "r", encoding="utf-8") as f:
                self._raw = json.load(f)
            skill_count = len(self._raw.get("skills", {}))
            logger.info("Loaded quiz JSON: %d skills found.", skill_count)
        except FileNotFoundError:
            logger.error("Quiz JSON not found at '%s'.", path)
            self._raw = {"skills": {}}
        except json.JSONDecodeError as e:
            logger.error("Invalid JSON in quiz file: %s", e)
            self._raw = {"skills": {}}

    def _get_questions_for_skill(
        self,
        skill: str,
        n: int,
    ) -> list[dict]:
        """
        Retrieve up to n questions for a skill.
        Falls back gracefully if skill not in dataset.
        """
        skill_bank = self._raw.get("skills", {}).get(skill, [])

        if not skill_bank:
            logger.warning("No questions found for skill '%s'.", skill)
            return []

        # If bank has fewer than n, use all available
        selected = skill_bank[:n] if len(skill_bank) >= n else skill_bank
        return selected