import json
from pathlib import Path

from backend.core.processor import extract_document
from backend.core.classifier import process_classification
from backend.core.organizer import organize_document


# ==========================================
# PROJECT PATHS
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent

INCOMING_DIR = BASE_DIR / "folders" / "Incoming"

REPORT_PATH = BASE_DIR / "storage_pipeline_report.json"


# ==========================================
# SUPPORTED FILE FORMATS
# ==========================================

SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".pptx",
    ".txt"
}


# ==========================================
# PROCESS SINGLE DOCUMENT
# ==========================================

def process_document(file_path: Path) -> dict:

    print("\n" + "=" * 60)
    print(f"PROCESSING: {file_path.name}")
    print("=" * 60)

    try:

        # STEP 1: Extract document content

        print("\n[1/4] Extracting document content...")

        document = extract_document(str(file_path))

        extracted_text = document["text"]

        if not extracted_text or not extracted_text.strip():

            raise ValueError(
                "No readable text found in document."
            )

        print(
            f"Extracted {document['character_count']} characters."
        )

        # STEP 2: Hybrid AI classification

        print("\n[2/4] Running hybrid AI classification...")

        result = process_classification(
            filename=document["filename"],
            extracted_text=extracted_text
        )

        classification = result["classification"]

        decision = result["decision"]

        print("\nCLASSIFICATION RESULT")
        print("-" * 40)

        print(
            "Filename prediction:",
            classification["filename_prediction"]
        )

        print(
            "Primary subject:",
            classification["primary_subject"]
        )

        print(
            "Secondary subjects:",
            classification["secondary_subjects"]
        )

        print(
            "Topic:",
            classification["topic"]
        )

        print(
            "Document type:",
            classification["document_type"]
        )

        print(
            "AI confidence:",
            classification["confidence"]
        )

        print(
            "Filename matches content:",
            classification["filename_content_match"]
        )

        # STEP 3: Evaluate classification decision

        print("\n[3/4] Evaluating organization decision...")

        print(
            "Decision:",
            decision["decision"]
        )

        print(
            "Reason:",
            decision["reason"]
        )

        # STEP 4: Organize document

        print("\n[4/4] Organizing document...")

        organization = organize_document(
            file_path=str(file_path),
            classification=classification,
            decision=decision
        )

        print("\nORGANIZATION RESULT")
        print("-" * 40)

        print("Status:", organization["status"])

        print("Subject:", organization["subject"])

        print("New location:", organization["new_path"])

        print("Message:", organization["message"])

        return {

            "status": "success",

            "filename": document["filename"],

            "file_type": document["file_type"],

            "character_count": document["character_count"],

            "classification": classification,

            "decision": decision,

            "organization": organization

        }

    except Exception as error:

        print(f"\nERROR: {error}")

        return {

            "status": "failed",

            "filename": file_path.name,

            "file_path": str(file_path.resolve()),

            "error": str(error)

        }


# ==========================================
# SCAN INCOMING FOLDER
# ==========================================

def scan_incoming_folder() -> list:

    print("\nAIDoc Document Pipeline")
    print("=" * 60)

    INCOMING_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    files = [

        file for file in INCOMING_DIR.iterdir()

        if file.is_file()

        and file.suffix.lower() in SUPPORTED_EXTENSIONS

    ]

    if not files:

        print("\nNo supported documents found in Incoming.")

        print(
            f"Place PDF, DOCX, PPTX or TXT files inside:\n{INCOMING_DIR}"
        )

        return []

    print(f"\nFound {len(files)} document(s).")

    results = []

    for file_path in files:

        result = process_document(file_path)

        results.append(result)

    # Save processing report

    with open(
        REPORT_PATH,
        "w",
        encoding="utf-8"
    ) as report_file:

        json.dump(
            results,
            report_file,
            indent=4,
            ensure_ascii=False
        )

    # Summary

    successful = sum(
        1 for result in results
        if result["status"] == "success"
    )

    failed = len(results) - successful

    organized = sum(
        1 for result in results
        if result.get("organization", {}).get("status") == "organized"
    )

    unclassified = sum(
        1 for result in results
        if result.get("organization", {}).get("status") == "unclassified"
    )

    print("\n" + "=" * 60)
    print("AIDOC PIPELINE COMPLETED")
    print("=" * 60)

    print(f"Successfully processed: {successful}")
    print(f"Failed: {failed}")
    print(f"Automatically organized: {organized}")
    print(f"Sent for manual review: {unclassified}")

    print(f"\nReport saved at: {REPORT_PATH}")

    return results


# ==========================================
# MAIN EXECUTION
# ==========================================

if __name__ == "__main__":

    scan_incoming_folder()