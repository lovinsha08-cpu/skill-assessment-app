"""
skills_reference.py
-------------------
Central reference for job categories and their required skills.
Drives resume matching, quiz selection, and course recommendations.
"""

SKILLS_REFERENCE = {
    "Data Scientist": [
        "Python",
        "Machine Learning",
        "Data Visualization",
        "Statistical Analysis"
    ],
    "Web Developer": [
        "HTML/CSS",
        "JavaScript",
        "React",
        "REST APIs"
    ],
    "DevOps Engineer": [
        "Docker",
        "CI/CD Pipelines",
        "Kubernetes",
        "Linux Administration"
    ],
    "Cybersecurity Analyst": [
        "Network Security",
        "Penetration Testing",
        "SIEM Tools",
        "Incident Response"
    ],
    "Cloud Architect": [
        "AWS",
        "Cloud Networking",
        "Infrastructure as Code",
        "Cost Optimization"
    ],
    "Mobile App Developer": [
        "Flutter",
        "React Native",
        "Mobile UI Design",
        "App Store Deployment"
    ],
    "Data Engineer": [
        "SQL",
        "Apache Spark",
        "ETL Pipelines",
        "Data Warehousing"
    ],
    "AI/ML Engineer": [
        "Deep Learning",
        "NLP",
        "Model Deployment",
        "TensorFlow/PyTorch"
    ],
    "Business Analyst": [
        "Requirements Gathering",
        "Data Analysis",
        "Process Mapping",
        "Stakeholder Communication"
    ],
    "UI/UX Designer": [
        "Wireframing",
        "Figma",
        "User Research",
        "Prototyping"
    ]
}

ALL_SKILLS = list({skill for skills in SKILLS_REFERENCE.values() for skill in skills})


def get_skills_for_category(category: str) -> list:
    """Return required skills for a job category."""
    return SKILLS_REFERENCE.get(category, [])


def get_all_categories() -> list:
    """Return all job category names."""
    return list(SKILLS_REFERENCE.keys())


def match_skills(resume_skills: list) -> dict:
    """
    Given a list of skills extracted from a resume:
    - Predict the best matching job category
    - Return matching_skills, missing_skills, and match_score
    """
    resume_lower = [s.lower().strip() for s in resume_skills]
    best_match = None
    best_score = -1

    for category, required in SKILLS_REFERENCE.items():
        req_lower = [s.lower().strip() for s in required]
        hits = sum(1 for s in req_lower if s in resume_lower)
        score = hits / len(required)
        if score > best_score:
            best_score = score
            best_match = category

    required = SKILLS_REFERENCE[best_match]
    matching = [s for s in required if s.lower().strip() in resume_lower]
    missing  = [s for s in required if s.lower().strip() not in resume_lower]

    return {
        "category":        best_match,
        "matching_skills": matching,
        "missing_skills":  missing,
        "match_score":     round(best_score * 100, 2)
    }


if __name__ == "__main__":
    sample = ["Python", "Machine Learning", "SQL", "Statistical Analysis"]
    result = match_skills(sample)
    print("Predicted Category :", result["category"])
    print("Match Score        :", result["match_score"], "%")
    print("Matching Skills    :", result["matching_skills"])
    print("Missing Skills     :", result["missing_skills"])
