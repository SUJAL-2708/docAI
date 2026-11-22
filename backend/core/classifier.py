from backend.ai.classification_engine import classify_document
from backend.ai.confidence import evaluate_confidence


def process_classification(
    filename: str,
    extracted_text: str
) -> dict:

    # Run hybrid AI classification
    classification = classify_document(
        filename=filename,
        document_content=extracted_text
    )

    # Evaluate confidence
    decision = evaluate_confidence(classification)

    return {
        "classification": classification,
        "decision": decision
    }