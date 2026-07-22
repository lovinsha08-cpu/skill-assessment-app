"""
modules/resume_parser.py
------------------------
Extracts text and skill keywords from uploaded resume files.

Supported formats: PDF, TXT, DOCX
Skills are matched by comparing extracted text against the full
known skills list from skills_reference.py.
"""

import io
import re
import logging

logger = logging.getLogger(__name__)


class ResumeParser:
    """
    Parse an uploaded resume file and extract skill keywords.

    Usage:
        parser = ResumeParser(all_known_skills)
        skills = parser.extract_skills(uploaded_file_bytes, filename)
    """

    def __init__(self, all_known_skills):
        """
        Args:
            all_known_skills: list of all skills from skills_reference.ALL_SKILLS
        """
        self.all_skills = all_known_skills

        # Convert skills to lowercase dictionary for quick matching
        self.skill_map = {skill.lower(): skill for skill in all_known_skills}

    # --------------------------------------------------
    # PUBLIC METHODS
    # --------------------------------------------------

    def extract_skills(self, file_bytes, filename):
        """
        Extract skill keywords from resume.

        Args:
            file_bytes : uploaded file bytes
            filename   : name of the uploaded file

        Returns:
            list of detected skills
        """

        ext = filename.split(".")[-1].lower()

        try:
            if ext == "pdf":
                text = self._parse_pdf(file_bytes)

            elif ext == "docx":
                text = self._parse_docx(file_bytes)

            else:
                text = file_bytes.decode("utf-8", errors="ignore")

        except Exception as e:
            logger.error(f"Error parsing resume {filename}: {e}")
            text = ""

        logger.info(f"Extracted {len(text)} characters from resume")

        return self._match_skills(text)

    def extract_skills_from_text(self, text):
        """Extract skills directly from text"""
        return self._match_skills(text)

    # --------------------------------------------------
    # FILE PARSERS
    # --------------------------------------------------

    def _parse_pdf(self, file_bytes):
        """Extract text from PDF"""
        try:
            import PyPDF2
        except ImportError:
            logger.warning("PyPDF2 not installed")
            return file_bytes.decode("utf-8", errors="ignore")

        reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))

        text = ""
        for page in reader.pages:
            try:
                text += page.extract_text() or ""
            except:
                pass

        return text

    def _parse_docx(self, file_bytes):
        """Extract text from DOCX"""
        try:
            from docx import Document
        except ImportError:
            logger.warning("python-docx not installed")
            return file_bytes.decode("utf-8", errors="ignore")

        document = Document(io.BytesIO(file_bytes))

        text = "\n".join([para.text for para in document.paragraphs])

        return text

    # --------------------------------------------------
    # SKILL MATCHING
    # --------------------------------------------------

    def _match_skills(self, text):
        """
        Find skills in resume text
        """

        text = text.lower()

        found_skills = []

        for skill_lower, original_skill in self.skill_map.items():

            pattern = r"\b" + re.escape(skill_lower) + r"\b"

            if re.search(pattern, text):
                found_skills.append(original_skill)

        logger.info(f"Matched {len(found_skills)} skills")

        return found_skills