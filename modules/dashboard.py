"""
modules/dashboard.py
--------------------
Builds Plotly chart figures for the visual analytics dashboard (Page 5).

Charts produced:
  1. Radar chart       – per-skill score comparison
  2. Bar chart         – per-skill score with colour-coded bands
  3. Gauge chart       – overall score
  4. Pie chart         – skills mastered vs to-improve
  5. Heatmap table     – question-level correctness grid
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import plotly.graph_objects as go
import plotly.express as px
from utils.logger import get_logger

logger = get_logger(__name__)

# Score band colours (consistent with config.py)
_COLORS = {
    "beginner":     "#E24B4A",
    "intermediate": "#FFC107",
    "advanced":     "#4CAF50",
    "mastery":      "#9C27B0",
}


class DashboardBuilder:
    """
    Stateless factory class for generating Plotly figures.

    Usage:
        db  = DashboardBuilder()
        fig = db.radar_chart(skill_scores)
        st.plotly_chart(fig, use_container_width=True)
    """

    # ── 1. Radar chart ─────────────────────────────────────────

    def radar_chart(self, skill_scores: dict[str, dict]) -> go.Figure:
        """Radar/spider chart showing each skill's score."""
        skills = list(skill_scores.keys())
        values = [skill_scores[s]["score_pct"] for s in skills]

        # Close the polygon
        skills_closed = skills + [skills[0]]
        values_closed = values + [values[0]]

        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=values_closed,
            theta=skills_closed,
            fill="toself",
            fillcolor="rgba(29,158,117,0.2)",
            line=dict(color="#1D9E75", width=2),
            name="Your scores",
        ))
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100]),
            ),
            showlegend=False,
            title="Skill Score Radar",
            margin=dict(t=50, b=20, l=40, r=40),
            height=420,
        )
        return fig

    # ── 2. Bar chart ──────────────────────────────────────────

    def bar_chart(self, skill_scores: dict[str, dict]) -> go.Figure:
        """Horizontal bar chart with per-skill colour coding."""
        skills  = list(skill_scores.keys())
        scores  = [skill_scores[s]["score_pct"] for s in skills]
        colors  = [skill_scores[s]["color"] for s in skills]
        levels  = [skill_scores[s]["level"].capitalize() for s in skills]

        fig = go.Figure(go.Bar(
            y=skills,
            x=scores,
            orientation="h",
            marker_color=colors,
            text=[f"{s:.1f}%" for s in scores],
            textposition="outside",
            customdata=levels,
            hovertemplate="<b>%{y}</b><br>Score: %{x:.1f}%<br>Level: %{customdata}<extra></extra>",
        ))
        fig.add_vline(x=40, line_dash="dash", line_color="#E24B4A",
                      annotation_text="Beginner / Intermediate boundary", annotation_position="top right")
        fig.add_vline(x=60, line_dash="dash", line_color="#EF9F27",
                      annotation_text="Intermediate / Advanced boundary", annotation_position="top right")
        fig.add_vline(x=80, line_dash="dash", line_color="#639922",
                      annotation_text="Advanced / Mastery boundary", annotation_position="top right")
        fig.update_layout(
            title="Per-Skill Quiz Scores",
            xaxis=dict(range=[0, 110], title="Score (%)"),
            yaxis=dict(title=""),
            height=350,
            margin=dict(t=50, b=40, l=20, r=120),
        )
        return fig

    # ── 3. Gauge chart ────────────────────────────────────────

    def gauge_chart(self, overall_score: float) -> go.Figure:
        """Gauge / indicator showing the overall average score."""
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=overall_score,
            delta={"reference": 60},
            title={"text": "Overall Score"},
            gauge={
                "axis":  {"range": [0, 100]},
                "bar":   {"color": self._level_color(overall_score)},
                "steps": [
                    {"range": [0,  40], "color": "#FCEBEB"},
                    {"range": [40, 60], "color": "#FAEEDA"},
                    {"range": [60, 80], "color": "#EAF3DE"},
                    {"range": [80, 100], "color": "#E1F5EE"},
                ],
                "threshold": {
                    "line": {"color": "#2C2C2A", "width": 2},
                    "thickness": 0.75,
                    "value": overall_score,
                },
            },
        ))
        fig.update_layout(height=300, margin=dict(t=30, b=0, l=20, r=20))
        return fig

    # ── 4. Pie chart ──────────────────────────────────────────

    def pie_chart(self, skill_scores: dict[str, dict]) -> go.Figure:
        """Pie showing mastered vs to-improve skill ratio."""
        mastered   = sum(1 for v in skill_scores.values() if v["score_pct"] >= 80)
        to_improve = len(skill_scores) - mastered

        fig = go.Figure(go.Pie(
            labels=["Mastered (≥80%)", "Needs Improvement (<80%)"],
            values=[mastered, to_improve],
            marker_colors=["#1D9E75", "#E24B4A"],
            hole=0.45,
            textinfo="label+percent",
        ))
        fig.update_layout(
            title="Skills Mastered vs To Improve",
            height=320,
            margin=dict(t=50, b=20, l=20, r=20),
            showlegend=False,
        )
        return fig

    # ── 5. Question heatmap ───────────────────────────────────

    def question_heatmap(self, skill_scores: dict[str, dict]) -> go.Figure:
        """
        Grid heatmap: rows = skills, columns = questions,
        cells = 1 (correct, green) or 0 (wrong, red).
        """
        skills = list(skill_scores.keys())
        max_q  = max(len(v["question_results"]) for v in skill_scores.values())
        z_matrix = []
        hover_text = []

        for skill in skills:
            qrs = skill_scores[skill]["question_results"]
            row  = [1 if q["is_correct"] else 0 for q in qrs]
            htxt = [
                f"Q{i+1}: {'✓ Correct' if q['is_correct'] else '✗ Wrong'}"
                for i, q in enumerate(qrs)
            ]
            # Pad shorter rows
            pad = max_q - len(row)
            row  += [-1] * pad
            htxt += ["No question"] * pad
            z_matrix.append(row)
            hover_text.append(htxt)

        colorscale = [
            [0.0,  "#888780"],   # -1 padding
            [0.5,  "#E24B4A"],   # 0  wrong
            [0.5,  "#E24B4A"],
            [1.0,  "#1D9E75"],   # 1  correct
        ]

        fig = go.Figure(go.Heatmap(
            z=z_matrix,
            y=skills,
            x=[f"Q{i+1}" for i in range(max_q)],
            colorscale=colorscale,
            showscale=False,
            text=hover_text,
            hovertemplate="%{y} — %{text}<extra></extra>",
            zmin=-1,
            zmax=1,
        ))
        fig.update_layout(
            title="Question-Level Correctness Heatmap",
            height=max(250, len(skills) * 55 + 80),
            margin=dict(t=50, b=40, l=20, r=20),
            yaxis=dict(autorange="reversed"),
        )
        return fig

    # ── Helper ────────────────────────────────────────────────

    def _level_color(self, score: float) -> str:
        if score < 40:
            return _COLORS["beginner"]
        elif score < 60:
            return _COLORS["intermediate"]
        elif score < 80:
            return _COLORS["advanced"]
        return _COLORS["mastery"]