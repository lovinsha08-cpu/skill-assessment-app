"""
utils/helpers.py
----------------
Shared utility functions used across pages and modules.
"""

import re
from config import (
    SCORE_BEGINNER_MAX,
    SCORE_INTERMEDIATE_MAX,
    SCORE_ADVANCED_MAX,
    SCORE_COLORS,
)


def get_score_level(score_pct: float) -> str:
    """
    Return the course level string for a given score percentage.
    Used both for course recommendation and badge display.

    Args:
        score_pct: A float between 0 and 100.

    Returns:
        One of: 'beginner', 'intermediate', 'advanced', 'mastery'
    """
    if score_pct < SCORE_BEGINNER_MAX:
        return "beginner"
    elif score_pct < SCORE_INTERMEDIATE_MAX:
        return "intermediate"
    elif score_pct < SCORE_ADVANCED_MAX:
        return "advanced"
    else:
        return "mastery"


def get_score_color(score_pct: float) -> str:
    """Return hex colour string matching the score band."""
    level = get_score_level(score_pct)
    return SCORE_COLORS.get(level, "#888780")


def percentage(correct: int, total: int) -> float:
    """Safe percentage calculation, returns 0.0 if total is 0."""
    if total == 0:
        return 0.0
    return round((correct / total) * 100, 1)


def sanitise_skill_name(skill: str) -> str:
    """
    Normalise a skill name for consistent lookup:
    strips whitespace and lowercases.
    """
    return skill.strip().lower()


def extract_option_letter(option_text: str) -> str:
    """
    Given a full option string like 'A. Use Docker...',
    extract just the letter 'A'.
    """
    match = re.match(r"^([A-D])\.", option_text.strip())
    if match:
        return match.group(1)
    # fallback: return first character if no dot pattern
    return option_text.strip()[0].upper() if option_text.strip() else ""


def format_score_badge(score_pct: float) -> str:
    """Return a human-readable score badge string."""
    level = get_score_level(score_pct)
    icons = {
        "beginner":     "🟥",
        "intermediate": "🟧",
        "advanced":     "🟨",
        "mastery":      "🟩",
    }
    labels = {
        "beginner":     "Beginner",
        "intermediate": "Intermediate",
        "advanced":     "Advanced",
        "mastery":      "Mastery",
    }
    return f"{icons[level]} {score_pct:.1f}% — {labels[level]}"


def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp a float between min and max."""
    return max(min_val, min(value, max_val))
