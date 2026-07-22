from __future__ import annotations

"""
modules/skill_matcher.py
------------------------
Matches extracted resume skills against skills_reference.py to:
  1. Predict the best-fitting job category.
  2. Identify matching skills (skills the candidate has).
  3. Identify missing skills (gaps for that category).
  4. Compute a match score (%).
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.logger import get_logger

logger = get_logger(__name__)


class SkillMatcher:
    """
    Wraps the match_skills logic from skills_reference.py and provides
    additional helpers used by the Streamlit pages.

    Usage:
        matcher = SkillMatcher(SKILLS_REFERENCE)
        result  = matcher.match(["Python", "Machine Learning", "SQL"])
    """

    def __init__(self, skills_reference: dict[str, list[str]]):
        """
        Args:
            skills_reference: The SKILLS_REFERENCE dict from
                              data/skills_reference.py
                              e.g. {"Data Scientist": ["Python", ...], ...}
        """
        self.reference = skills_reference

    # ── Public API ────────────────────────────────────────────

    def match(self, resume_skills: list[str]) -> dict:
        """
        Given a list of skills from the resume, return a full
        match result dict.

        Returns dict with keys:
            category        – predicted job category string
            matching_skills – list of skills the candidate has
            missing_skills  – list of skills the candidate lacks
            match_score     – float (0–100), % of required skills present
            all_categories  – list of (category, score) tuples sorted desc
        """
        resume_lower = {s.lower().strip() for s in resume_skills}
        scores: list[tuple[str, float]] = []

        for category, required in self.reference.items():
            req_lower = [s.lower().strip() for s in required]
            hits = sum(1 for s in req_lower if s in resume_lower)
            score = hits / len(required) if required else 0.0
            scores.append((category, score))

        # Sort by score descending
        scores.sort(key=lambda x: x[1], reverse=True)
        best_category, best_score = scores[0]

        required = self.reference[best_category]
        matching = [s for s in required if s.lower().strip() in resume_lower]
        missing  = [s for s in required if s.lower().strip() not in resume_lower]

        result = {
            "category":        best_category,
            "matching_skills": matching,
            "missing_skills":  missing,
            "match_score":     round(best_score * 100, 1),
            "all_categories":  scores,
        }

        logger.info(
            "Best match: '%s' (%.1f%%) | matching=%s | missing=%s",
            best_category,
            result["match_score"],
            matching,
            missing,
        )
        return result

    def get_required_skills(self, category: str) -> list[str]:
        """Return the full required skill list for a category."""
        return self.reference.get(category, [])

    def get_all_categories(self) -> list[str]:
        """Return all job category names."""
        return list(self.reference.keys())

    def top_n_categories(
        self,
        resume_skills: list[str],
        n: int = 3,
    ) -> list[dict]:
        """
        Return the top-n category matches with scores, useful for
        displaying 'you also closely match…' suggestions.

        Returns a list of dicts: [{category, score_pct}, ...]
        """
        result = self.match(resume_skills)
        top = result["all_categories"][:n]
        return [
            {"category": cat, "score_pct": round(score * 100, 1)}
            for cat, score in top
        ]