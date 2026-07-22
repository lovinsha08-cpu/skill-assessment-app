from __future__ import annotations

"""
utils/validators.py
-------------------
Input validation helpers — called before processing user data.
"""

from config import ALLOWED_RESUME_TYPES


def is_valid_resume_file(filename: str) -> bool:
    """
    Check whether the uploaded filename has an allowed extension.

    Args:
        filename: Original filename from the uploader widget.

    Returns:
        True if the extension is in ALLOWED_RESUME_TYPES.
    """
    if not filename:
        return False
    ext = filename.rsplit(".", 1)[-1].lower()
    return ext in ALLOWED_RESUME_TYPES


def is_valid_email(email: str) -> bool:
    """Basic email format validation."""
    import re
    pattern = r"^[\w\.\+\-]+@[\w\-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email.strip()))


def is_non_empty_string(value: str) -> bool:
    """Return True if value is a non-empty, non-whitespace string."""
    return isinstance(value, str) and len(value.strip()) > 0


def validate_quiz_answer(answer: str, valid_letters: list[str]) -> bool:
    """
    Validate that a quiz answer is one of the allowed option letters.

    Args:
        answer: The selected answer letter (e.g. 'B').
        valid_letters: Expected letters (e.g. ['A','B','C','D']).

    Returns:
        True if answer is among valid_letters.
    """
    return answer.strip().upper() in [l.upper() for l in valid_letters]