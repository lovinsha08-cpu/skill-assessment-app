"""
modules/scorer.py
-----------------
Calculates per-skill quiz scores from the candidate's answers.

Score formula per skill:
    score_pct = (correct_answers / total_questions_for_skill) * 100

Also determines score level (beginner / intermediate / advanced / mastery)
for use by the Recommender.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.helpers import percentage, get_score_level, get_score_color
from utils.logger import get_logger

logger = get_logger(__name__)


class Scorer:
    """
    Evaluate quiz answers and produce per-skill score reports.

    Usage:
        scorer  = Scorer()
        results = scorer.evaluate(questions, answers)
    """

    # ── Public API ────────────────────────────────────────────

    def evaluate(
        self,
        questions: list[dict],
        answers: dict[str, str],
    ) -> dict[str, dict]:
        """
        Calculate scores for all skills attempted in the quiz.

        Args:
            questions: Full list of question dicts (from QuizEngine),
                       each must contain: id, answer (correct), skill.
            answers:   Dict mapping question_id → selected_option_letter
                       e.g. {"DS_PY_1": "B", "DS_ML_1": "A", ...}

        Returns:
            Dict keyed by skill name, each value is:
            {
                skill:        str,
                correct:      int,
                total:        int,
                score_pct:    float,
                level:        str,   # 'beginner' | 'intermediate' | 'advanced' | 'mastery'
                color:        str,   # hex color for the level
                question_results: [
                    {id, question, correct_answer, selected_answer,
                     is_correct, explanation}, ...
                ]
            }
        """
        # Group questions by skill
        skill_questions: dict[str, list[dict]] = {}
        for q in questions:
            skill = q.get("skill", "Unknown")
            skill_questions.setdefault(skill, []).append(q)

        results: dict[str, dict] = {}

        for skill, qs in skill_questions.items():
            correct_count = 0
            question_results = []

            for q in qs:
                q_id            = q["id"]
                correct_letter  = q["answer"].strip().upper()
                selected_letter = answers.get(q_id, "").strip().upper()
                is_correct      = selected_letter == correct_letter
                if is_correct:
                    correct_count += 1

                question_results.append({
                    "id":              q_id,
                    "question":        q["question"],
                    "options":         q.get("options", []),
                    "correct_answer":  correct_letter,
                    "selected_answer": selected_letter or "—",
                    "is_correct":      is_correct,
                    "explanation":     q.get("explanation", ""),
                })

            score_pct = percentage(correct_count, len(qs))
            level     = get_score_level(score_pct)
            color     = get_score_color(score_pct)

            results[skill] = {
                "skill":            skill,
                "correct":          correct_count,
                "total":            len(qs),
                "score_pct":        score_pct,
                "level":            level,
                "color":            color,
                "question_results": question_results,
            }

            logger.info(
                "Skill '%s': %d/%d correct (%.1f%%) → %s",
                skill, correct_count, len(qs), score_pct, level,
            )

        return results

    def overall_score(self, skill_scores: dict[str, dict]) -> float:
        """
        Compute the overall average score across all skills.

        Args:
            skill_scores: Return value of evaluate().

        Returns:
            Average score percentage (float).
        """
        if not skill_scores:
            return 0.0
        total = sum(v["score_pct"] for v in skill_scores.values())
        return round(total / len(skill_scores), 1)

    def summary(self, skill_scores: dict[str, dict]) -> dict:
        """
        Return a high-level summary dict for dashboard display.

        Returns:
            {
                overall_score:   float,
                skills_mastered: list[str],    # score >= 80
                skills_to_improve: list[str],  # score < 80
                strongest_skill: str,
                weakest_skill:   str,
            }
        """
        if not skill_scores:
            return {}

        overall = self.overall_score(skill_scores)
        mastered    = [s for s, v in skill_scores.items() if v["score_pct"] >= 80]
        to_improve  = [s for s, v in skill_scores.items() if v["score_pct"] < 80]
        sorted_by   = sorted(skill_scores.items(), key=lambda x: x[1]["score_pct"])

        return {
            "overall_score":     overall,
            "skills_mastered":   mastered,
            "skills_to_improve": to_improve,
            "strongest_skill":   sorted_by[-1][0] if sorted_by else "",
            "weakest_skill":     sorted_by[0][0]  if sorted_by else "",
        }