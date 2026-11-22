from backend.config import settings


def evaluate_confidence(classification: dict) -> dict:

    confidence = classification.get("confidence", 0.0)

    filename_match = classification.get(
        "filename_content_match",
        False
    )

    subject = classification.get("primary_subject")

    if subject == "Other":

        return {
            "decision": "review",
            "auto_organize": False,
            "reason": "Document does not match a recognized subject."
        }

    if confidence >= settings.CONFIDENCE_THRESHOLD:

        return {
            "decision": "auto_organize",
            "auto_organize": True,
            "reason": "AI classification confidence meets the threshold."
        }

    return {
        "decision": "review",
        "auto_organize": False,
        "reason": (
            "Classification confidence is below the required threshold."
        )
    }