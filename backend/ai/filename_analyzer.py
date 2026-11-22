import re
from pathlib import Path


SUBJECT_KEYWORDS = {
    "Engineering Mathematics": [
        "math", "mathematics", "calculus", "algebra",
        "matrix", "matrices", "differentiation",
        "integration", "differential", "equation",
        "eigenvalue", "probability", "statistics"
    ],

    "Engineering Physics": [
        "physics", "semiconductor", "laser", "optics",
        "diffraction", "interference", "quantum",
        "electromagnetism", "magnetism", "wave",
        "thermodynamics", "electronic"
    ],

    "Programming in C": [
        "programming", "coding", "language", "compiler",
        "algorithm", "pointer", "array", "function",
        "loop", "structure", "c_language"
    ],

    "Engineering Mechanics": [
        "mechanics", "force", "motion", "friction",
        "statics", "dynamics", "moment", "velocity",
        "acceleration", "equilibrium"
    ],

    "French": [
        "french", "vocabulary", "grammar",
        "bonjour", "conjugation", "verb"
    ],

    "Computer Science": [
        "computer", "database", "network",
        "operating_system", "software", "hardware",
        "data_structure", "cybersecurity"
    ]
}


def normalize_filename(filename: str) -> str:

    name = Path(filename).stem.lower()

    name = re.sub(r"[_\-]+", " ", name)

    name = re.sub(r"[^a-z0-9\s]", " ", name)

    return re.sub(r"\s+", " ", name).strip()


def analyze_filename(filename: str) -> dict:

    normalized = normalize_filename(filename)

    scores = {}

    for subject, keywords in SUBJECT_KEYWORDS.items():

        score = 0
        matched_keywords = []

        for keyword in keywords:

            normalized_keyword = keyword.replace("_", " ")

            if normalized_keyword in normalized:

                score += 1
                matched_keywords.append(keyword)

        if score > 0:

            scores[subject] = {
                "score": score,
                "matched_keywords": matched_keywords
            }

    if not scores:

        return {
            "filename": filename,
            "normalized_filename": normalized,
            "predicted_subject": None,
            "confidence": 0.0,
            "matches": {}
        }

    best_subject = max(
        scores,
        key=lambda subject: scores[subject]["score"]
    )

    total_matches = sum(
        item["score"] for item in scores.values()
    )

    confidence = (
        scores[best_subject]["score"] / total_matches
    )

    return {
        "filename": filename,
        "normalized_filename": normalized,
        "predicted_subject": best_subject,
        "confidence": round(confidence, 3),
        "matches": scores
    }