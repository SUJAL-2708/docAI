import json
import re

from backend.ai.filename_analyzer import analyze_filename
from backend.ai.prompts import build_classification_prompt
from backend.ai.ollama_client import generate_response


# ============================================================
# ALLOWED SUBJECTS
# ============================================================

ALLOWED_SUBJECTS = {
    "Engineering Mathematics",
    "Engineering Physics",
    "Programming in C",
    "Engineering Mechanics",
    "French",
    "Computer Science",
    "Other"
}


# ============================================================
# JSON RESPONSE CLEANER
# ============================================================

def clean_json_response(response: str) -> dict:
    """
    Clean and parse Ollama's JSON response.

    Handles responses wrapped in Markdown code blocks.
    """

    if not isinstance(response, str) or not response.strip():
        raise ValueError("AI returned an empty response.")

    response = response.strip()

    response = re.sub(
        r"^```(?:json)?\s*",
        "",
        response,
        flags=re.IGNORECASE
    )

    response = re.sub(
        r"\s*```$",
        "",
        response
    )

    try:
        result = json.loads(response)

    except json.JSONDecodeError as error:

        raise ValueError(
            f"AI returned invalid JSON: {error}"
        ) from error

    if not isinstance(result, dict):

        raise ValueError(
            "AI response must be a JSON object."
        )

    return result


# ============================================================
# CLASSIFICATION VALIDATION
# ============================================================

def validate_classification(result: dict) -> dict:
    """
    Validate and normalize the AI classification result.
    """

    primary_subject = result.get("primary_subject")

    if not isinstance(primary_subject, str):
        raise ValueError("AI did not return a valid primary subject.")

    primary_subject = primary_subject.strip()

    if primary_subject not in ALLOWED_SUBJECTS:

        raise ValueError(
            f"AI returned an invalid subject: {primary_subject}"
        )

    secondary_subjects = result.get(
        "secondary_subjects",
        []
    )

    if not isinstance(secondary_subjects, list):
        secondary_subjects = []

    secondary_subjects = [
        subject.strip()
        for subject in secondary_subjects
        if isinstance(subject, str)
        and subject.strip() in ALLOWED_SUBJECTS
        and subject.strip() != primary_subject
    ]

    try:
        confidence = float(result.get("confidence", 0))
    except (TypeError, ValueError):
        confidence = 0.0

    confidence = max(0.0, min(1.0, confidence))

    return {
        "primary_subject": primary_subject,
        "secondary_subjects": secondary_subjects,
        "topic": str(result.get("topic") or "Unknown"),
        "document_type": str(result.get("document_type") or "Other"),
        "confidence": confidence,
        "reasoning": str(result.get("reasoning") or "")
    }


# ============================================================
# MAIN DOCUMENT CLASSIFICATION
# ============================================================

def classify_document(
    filename: str,
    document_content: str
) -> dict:
    """
    Classify a document using:

    1. Filename analysis.
    2. AI content analysis through Ollama.
    3. Classification validation.
    4. Filename-content comparison.

    Returns a standardized classification dictionary.
    """

    # --------------------------------------------------------
    # STEP 1: VALIDATE INPUT
    # --------------------------------------------------------

    if not isinstance(document_content, str):
        raise ValueError("Document content must be text.")

    if not document_content.strip():

        raise ValueError(
            "Document contains no extractable text."
        )

    # --------------------------------------------------------
    # STEP 2: ANALYZE FILENAME
    # --------------------------------------------------------

    filename_result = analyze_filename(filename)

    predicted_subject = filename_result.get(
        "predicted_subject"
    )

    filename_confidence = filename_result.get(
        "confidence",
        0
    )

    # --------------------------------------------------------
    # STEP 3: PREPARE DOCUMENT CONTENT
    # --------------------------------------------------------

    content_for_ai = document_content[:12000]

    # --------------------------------------------------------
    # STEP 4: BUILD AI PROMPT
    # --------------------------------------------------------

    prompt = build_classification_prompt(
        filename=filename,
        filename_prediction=predicted_subject,
        document_content=content_for_ai
    )

    # --------------------------------------------------------
    # STEP 5: GET AI RESPONSE
    # --------------------------------------------------------

    response = generate_response(prompt)

    # --------------------------------------------------------
    # STEP 6: PARSE AI RESPONSE
    # --------------------------------------------------------

    raw_result = clean_json_response(response)

    # --------------------------------------------------------
    # STEP 7: VALIDATE CLASSIFICATION
    # --------------------------------------------------------

    result = validate_classification(raw_result)

    primary_subject = result["primary_subject"]

    # --------------------------------------------------------
    # STEP 8: COMPARE FILENAME WITH DOCUMENT CONTENT
    # --------------------------------------------------------

    filename_match = (
        predicted_subject is None
        or predicted_subject == primary_subject
    )

    # --------------------------------------------------------
    # STEP 9: RETURN STANDARDIZED RESULT
    # --------------------------------------------------------

    return {

        "filename": filename,

        "filename_prediction": predicted_subject,

        "filename_confidence": filename_confidence,

        "primary_subject": primary_subject,

        "secondary_subjects": result["secondary_subjects"],

        "topic": result["topic"],

        "document_type": result["document_type"],

        "confidence": result["confidence"],

        "filename_content_match": filename_match,

        "reasoning": result["reasoning"]

    }