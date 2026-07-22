"""
modules/recommender.py
----------------------
Generates personalised course recommendations based on:
  1. Missing skills  → always recommend BEGINNER level courses
  2. Matching skills → recommend level based on quiz score:
        score < 40%  → beginner
        score < 60%  → intermediate
        score < 80%  → advanced
        score >= 80% → no recommendation needed (mastery)
"""

import json
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config import COURSES_JSON_PATH, MISSING_SKILL_COURSE_LEVEL
from utils.helpers import get_score_level
from utils.logger import get_logger

logger = get_logger(__name__)


class Recommender:
    """
    Build the course recommendation list for a candidate.

    Usage:
        rec   = Recommender()
        plans = rec.recommend(missing_skills, skill_scores)
    """

    def __init__(self, courses_json_path: str | None = None):
        path = courses_json_path or str(COURSES_JSON_PATH)
        self._courses: dict = {}
        self._load(path)

    # ── Public API ────────────────────────────────────────────

    def recommend(
        self,
        missing_skills: list[str],
        skill_scores: dict[str, dict],
    ) -> list[dict]:
        """
        Build the full recommendation list.

        Args:
            missing_skills: Skills the candidate lacks (from SkillMatcher).
            skill_scores:   Per-skill score results (from Scorer.evaluate()).

        Returns:
            List of recommendation dicts:
            [
              {
                skill:       str,
                reason:      str,   # 'missing' | 'score_<level>'
                level:       str,   # 'beginner' | 'intermediate' | 'advanced'
                score_pct:   float | None,
                courses:     [
                  {id, title, platform, instructor, duration,
                   price, url, description}, ...
                ]
              },
              ...
            ]
        """
        recommendations: list[dict] = []

        # 1. Missing skills → beginner courses
        for skill in missing_skills:
            courses = self._get_courses(skill, MISSING_SKILL_COURSE_LEVEL)
            recommendations.append({
                "skill":      skill,
                "reason":     "missing",
                "level":      MISSING_SKILL_COURSE_LEVEL,
                "score_pct":  None,
                "courses":    courses,
            })
            logger.info("Missing skill '%s' → beginner courses.", skill)

        # 2. Matching skills → level from score
        for skill, score_data in skill_scores.items():
            score_pct = score_data["score_pct"]
            level     = get_score_level(score_pct)

            if level == "mastery":
                logger.info("Skill '%s' at mastery (%.1f%%) — no course needed.", skill, score_pct)
                continue

            courses = self._get_courses(skill, level)
            recommendations.append({
                "skill":      skill,
                "reason":     f"score_{level}",
                "level":      level,
                "score_pct":  score_pct,
                "courses":    courses,
            })
            logger.info(
                "Skill '%s' score %.1f%% → %s courses.", skill, score_pct, level
            )

        return recommendations

    def get_courses_for_skill_level(
        self,
        skill: str,
        level: str,
    ) -> list[dict]:
        """Direct lookup: courses for a specific skill + level."""
        return self._get_courses(skill, level)

    # ── Private helpers ───────────────────────────────────────

    def _load(self, path: str) -> None:
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._courses = data.get("courses", {})
            logger.info(
                "Loaded courses JSON: %d skills available.", len(self._courses)
            )
        except FileNotFoundError:
            logger.error("Courses JSON not found at '%s'.", path)
            self._courses = {}
        except json.JSONDecodeError as e:
            logger.error("Invalid JSON in courses file: %s", e)
            self._courses = {}

    def _get_courses(self, skill: str, level: str) -> list[dict]:
        """
        Fetch courses for a skill at a given level.
        Returns empty list if skill or level not found.
        """
        skill_data = self._courses.get(skill, {})
        if not skill_data:
            logger.warning("No courses found for skill '%s'.", skill)
            return []
        level_courses = skill_data.get(level, [])
        if not level_courses:
            logger.warning(
                "No '%s' courses found for skill '%s'.", level, skill
            )
        return level_courses