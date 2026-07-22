"""
modules/session_state.py
------------------------
Thin wrapper around Streamlit's session_state.
Provides typed getters/setters and a clean reset mechanism
so all pages share consistent state management.
"""

from __future__ import annotations
import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config import SessionKeys


class SessionStateManager:
    """
    Manages the Streamlit session state for the whole app.

    Usage:
        sm = SessionStateManager()
        sm.set_match_result(result_dict)
        result = sm.get_match_result()
    """

    # ── Initialise defaults ───────────────────────────────────

    @staticmethod
    def init() -> None:
        """
        Call once at the top of app.py to seed all session keys
        with their default values so no KeyError occurs on first run.
        """
        defaults = {
            SessionKeys.UPLOADED_FILE:    None,
            SessionKeys.PARSED_SKILLS:    [],
            SessionKeys.MATCH_RESULT:     {},
            SessionKeys.QUIZ_QUESTIONS:   [],
            SessionKeys.QUIZ_ANSWERS:     {},
            SessionKeys.QUIZ_CURRENT_IDX: 0,
            SessionKeys.QUIZ_COMPLETE:    False,
            SessionKeys.SKILL_SCORES:     {},
            SessionKeys.RECOMMENDATIONS:  [],
            SessionKeys.EMPLOYEE_NAME:    "",
            SessionKeys.EMPLOYEE_EMAIL:   "",
        }
        for key, default in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = default

    @staticmethod
    def reset() -> None:
        """Clear all app session keys (called on 'Start Over')."""
        keys = [
            SessionKeys.UPLOADED_FILE,
            SessionKeys.PARSED_SKILLS,
            SessionKeys.MATCH_RESULT,
            SessionKeys.QUIZ_QUESTIONS,
            SessionKeys.QUIZ_ANSWERS,
            SessionKeys.QUIZ_CURRENT_IDX,
            SessionKeys.QUIZ_COMPLETE,
            SessionKeys.SKILL_SCORES,
            SessionKeys.RECOMMENDATIONS,
            SessionKeys.EMPLOYEE_NAME,
            SessionKeys.EMPLOYEE_EMAIL,
        ]
        for key in keys:
            if key in st.session_state:
                del st.session_state[key]

    # ── Typed getters / setters ───────────────────────────────

    @staticmethod
    def set_uploaded_file(file) -> None:
        st.session_state[SessionKeys.UPLOADED_FILE] = file

    @staticmethod
    def get_uploaded_file():
        return st.session_state.get(SessionKeys.UPLOADED_FILE)

    @staticmethod
    def set_parsed_skills(skills: list[str]) -> None:
        st.session_state[SessionKeys.PARSED_SKILLS] = skills

    @staticmethod
    def get_parsed_skills() -> list[str]:
        return st.session_state.get(SessionKeys.PARSED_SKILLS, [])

    @staticmethod
    def set_match_result(result: dict) -> None:
        st.session_state[SessionKeys.MATCH_RESULT] = result

    @staticmethod
    def get_match_result() -> dict:
        return st.session_state.get(SessionKeys.MATCH_RESULT, {})

    @staticmethod
    def set_quiz_questions(questions: list[dict]) -> None:
        st.session_state[SessionKeys.QUIZ_QUESTIONS] = questions

    @staticmethod
    def get_quiz_questions() -> list[dict]:
        return st.session_state.get(SessionKeys.QUIZ_QUESTIONS, [])

    @staticmethod
    def set_quiz_answer(question_id: str, answer: str) -> None:
        answers = st.session_state.get(SessionKeys.QUIZ_ANSWERS, {})
        answers[question_id] = answer
        st.session_state[SessionKeys.QUIZ_ANSWERS] = answers

    @staticmethod
    def get_quiz_answers() -> dict[str, str]:
        return st.session_state.get(SessionKeys.QUIZ_ANSWERS, {})

    @staticmethod
    def get_quiz_current_idx() -> int:
        return st.session_state.get(SessionKeys.QUIZ_CURRENT_IDX, 0)

    @staticmethod
    def set_quiz_current_idx(idx: int) -> None:
        st.session_state[SessionKeys.QUIZ_CURRENT_IDX] = idx

    @staticmethod
    def is_quiz_complete() -> bool:
        return st.session_state.get(SessionKeys.QUIZ_COMPLETE, False)

    @staticmethod
    def set_quiz_complete(complete: bool = True) -> None:
        st.session_state[SessionKeys.QUIZ_COMPLETE] = complete

    @staticmethod
    def set_skill_scores(scores: dict) -> None:
        st.session_state[SessionKeys.SKILL_SCORES] = scores

    @staticmethod
    def get_skill_scores() -> dict:
        return st.session_state.get(SessionKeys.SKILL_SCORES, {})

    @staticmethod
    def set_recommendations(recs: list[dict]) -> None:
        st.session_state[SessionKeys.RECOMMENDATIONS] = recs

    @staticmethod
    def get_recommendations() -> list[dict]:
        return st.session_state.get(SessionKeys.RECOMMENDATIONS, [])

    @staticmethod
    def set_employee_info(name: str, email: str) -> None:
        st.session_state[SessionKeys.EMPLOYEE_NAME]  = name
        st.session_state[SessionKeys.EMPLOYEE_EMAIL] = email

    @staticmethod
    def get_employee_name() -> str:
        return st.session_state.get(SessionKeys.EMPLOYEE_NAME, "")

    @staticmethod
    def get_employee_email() -> str:
        return st.session_state.get(SessionKeys.EMPLOYEE_EMAIL, "")