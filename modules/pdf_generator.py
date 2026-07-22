"""
modules/pdf_generator.py
------------------------
Generates a downloadable PDF report summarising:
  - Candidate info
  - Predicted job category & skill match
  - Per-skill quiz scores with level badges
  - Course recommendations with direct links

Requires: reportlab
"""

from __future__ import annotations
import io
from datetime import date
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.logger import get_logger

logger = get_logger(__name__)

# Level badge colours (RGB tuples for reportlab)
_LEVEL_COLORS = {
    "beginner":     (226, 75,  74),
    "intermediate": (239, 159, 39),
    "advanced":     (99,  153, 34),
    "mastery":      (29,  158, 117),
}


class PDFGenerator:
    """
    Build an in-memory PDF report and return its bytes.

    Usage:
        gen = PDFGenerator()
        pdf_bytes = gen.build(
            candidate_name, category, match_result,
            skill_scores, recommendations
        )
        st.download_button("Download PDF", pdf_bytes, "report.pdf")
    """

    def build(
        self,
        candidate_name: str,
        candidate_email: str,
        category: str,
        match_result: dict,
        skill_scores: dict[str, dict],
        recommendations: list[dict],
    ) -> bytes:
        """
        Build the complete PDF and return as bytes.

        Args:
            candidate_name:  Full name of the candidate.
            candidate_email: Email address.
            category:        Predicted job category.
            match_result:    Dict from SkillMatcher.match().
            skill_scores:    Dict from Scorer.evaluate().
            recommendations: List from Recommender.recommend().

        Returns:
            Raw PDF bytes ready for st.download_button.
        """
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib import colors
            from reportlab.lib.units import cm
            from reportlab.platypus import (
                SimpleDocTemplate, Paragraph, Spacer, Table,
                TableStyle, HRFlowable,
            )
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.enums import TA_LEFT, TA_CENTER
        except ImportError:
            logger.error(
                "reportlab is not installed. "
                "Run: pip install reportlab"
            )
            return b""

        try:
            buffer = io.BytesIO()
            doc    = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=2*cm, leftMargin=2*cm,
                topMargin=2*cm,   bottomMargin=2*cm,
            )

            styles  = getSampleStyleSheet()
            story   = []

            # ── Styles ────────────────────────────────────────────
            h1 = ParagraphStyle("H1", parent=styles["Heading1"],
                                 fontSize=20, textColor=colors.HexColor("#26215C"))
            h2 = ParagraphStyle("H2", parent=styles["Heading2"],
                                 fontSize=14, textColor=colors.HexColor("#3C3489"),
                                 spaceBefore=14)
            body  = ParagraphStyle("Body", parent=styles["Normal"],
                                    fontSize=10, leading=14)
            small = ParagraphStyle("Small", parent=styles["Normal"],
                                    fontSize=9, textColor=colors.HexColor("#5F5E5A"))

            # ── Header ────────────────────────────────────────────
            story.append(Paragraph("Skill Assessment Report", h1))
            story.append(Paragraph(f"Generated: {date.today().strftime('%d %B %Y')}", small))
            story.append(HRFlowable(width="100%", thickness=1,
                                     color=colors.HexColor("#CECBF6")))
            story.append(Spacer(1, 0.3*cm))

            # ── Candidate info ────────────────────────────────────
            story.append(Paragraph("Candidate Information", h2))
            info_data = [
                ["Name",  candidate_name  or "—"],
                ["Email", candidate_email or "—"],
                ["Predicted Category", category],
                ["Match Score",
                 f"{match_result.get('match_score', 0):.1f}%"],
            ]
            info_table = Table(info_data, colWidths=[5*cm, 12*cm])
            info_table.setStyle(TableStyle([
                ("FONTSIZE",    (0, 0), (-1, -1), 10),
                ("FONTNAME",    (0, 0), (0, -1),  "Helvetica-Bold"),
                ("TEXTCOLOR",   (0, 0), (0, -1),  colors.HexColor("#3C3489")),
                ("BOTTOMPADDING",(0,0), (-1,-1),  4),
                ("TOPPADDING",  (0, 0), (-1, -1), 4),
            ]))
            story.append(info_table)
            story.append(Spacer(1, 0.4*cm))

            # ── Skill gap summary ─────────────────────────────────
            story.append(Paragraph("Skill Gap Summary", h2))
            matching = ", ".join(match_result.get("matching_skills", []))
            missing  = ", ".join(match_result.get("missing_skills", []))
            story.append(Paragraph(f"<b>Matching skills:</b> {matching or 'None'}", body))
            story.append(Paragraph(f"<b>Missing skills:</b>  {missing or 'None'}", body))
            story.append(Spacer(1, 0.4*cm))

            # ── Quiz score table ──────────────────────────────────
            if skill_scores:
                story.append(Paragraph("Quiz Score Results", h2))
                score_rows = [["Skill", "Correct", "Total", "Score", "Level"]]
                for skill, data in skill_scores.items():
                    score_rows.append([
                        skill,
                        str(data["correct"]),
                        str(data["total"]),
                        f"{data['score_pct']:.1f}%",
                        data["level"].capitalize(),
                    ])
                score_table = Table(score_rows, colWidths=[5*cm, 2*cm, 2*cm, 2.5*cm, 4*cm])
                score_table.setStyle(TableStyle([
                    ("BACKGROUND",  (0, 0), (-1, 0),  colors.HexColor("#EEEDFE")),
                    ("FONTNAME",    (0, 0), (-1, 0),  "Helvetica-Bold"),
                    ("FONTSIZE",    (0, 0), (-1, -1), 9),
                    ("GRID",        (0, 0), (-1, -1), 0.5, colors.HexColor("#D3D1C7")),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1),
                     [colors.white, colors.HexColor("#F1EFE8")]),
                    ("TOPPADDING",  (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING",(0,0), (-1,-1),  4),
                ]))
                story.append(score_table)
                story.append(Spacer(1, 0.4*cm))

            # ── Course recommendations ────────────────────────────
            if recommendations:
                story.append(Paragraph("Course Recommendations", h2))
                for rec in recommendations:
                    skill   = rec["skill"]
                    level   = rec["level"].capitalize()
                    reason  = ("Missing skill — beginner courses recommended"
                               if rec["reason"] == "missing"
                               else f"Score: {rec['score_pct']:.1f}% → {level} courses recommended")

                    story.append(Paragraph(
                        f"<b>{skill}</b> — {reason}", body
                    ))

                    for course in rec.get("courses", []):
                        line = (
                            f"  • <b>{course['title']}</b> "
                            f"({course['platform']}) — "
                            f"{course.get('duration','?')} | "
                            f"{course.get('price','?')} | "
                            f"<a href='{course['url']}'>{course['url']}</a>"
                        )
                        story.append(Paragraph(line, small))
                    story.append(Spacer(1, 0.2*cm))

            # ── Footer ────────────────────────────────────────────
            story.append(Spacer(1, 0.5*cm))
            story.append(HRFlowable(width="100%", thickness=0.5,
                                     color=colors.HexColor("#D3D1C7")))
            story.append(Paragraph(
                "Generated by Skill Assessment & Career Recommender App", small
            ))

            doc.build(story)
            pdf_bytes = buffer.getvalue()
            buffer.close()
            logger.info("PDF generated: %d bytes.", len(pdf_bytes))
            return pdf_bytes
        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            return b""