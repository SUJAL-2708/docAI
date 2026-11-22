from pathlib import Path

from backend.core.file_handler import (
    move_file,
    FileOperationError
)


# ============================================================
# PROJECT DIRECTORIES
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

INCOMING_DIR = (BASE_DIR / "folders" / "Incoming").resolve()

ORGANIZED_DIR = BASE_DIR / "folders" / "Organized"

UNCLASSIFIED_DIR = BASE_DIR / "folders" / "Unclassified"


# ============================================================
# ORGANIZE DOCUMENT
# ============================================================

def organize_document(
    file_path: str,
    classification: dict,
    decision: dict
) -> dict:

    """
    Determines the destination of a classified document.

    High-confidence documents:
        folders/Organized/<Subject>/

    Low-confidence documents:
        folders/Unclassified/

    Actual file movement is handled by file_handler.py.
    """

    source = Path(file_path).resolve()

    # --------------------------------------------------------
    # 1. VALIDATE SOURCE
    # --------------------------------------------------------

    if not source.exists():

        raise FileNotFoundError(
            f"Document not found: {source}"
        )

    if not source.is_file():

        raise ValueError(
            "Source path is not a file."
        )

    # Only allow files from Incoming.

    try:

        source.relative_to(INCOMING_DIR)

    except ValueError:

        raise ValueError(
            "For safety, only files inside Incoming can be organized."
        )

    # --------------------------------------------------------
    # 2. DETERMINE DESTINATION
    # --------------------------------------------------------

    auto_organize = decision.get(
        "auto_organize",
        False
    )

    subject = classification.get(
        "primary_subject"
    )

    if auto_organize and subject and subject != "Other":

        subject = str(subject).strip()

        # Prevent unsafe folder names.
        if (
            subject in {".", ".."}
            or "/" in subject
            or "\\" in subject
            or Path(subject).name != subject
        ):
            raise ValueError("Invalid subject folder name.")

        destination_folder = ORGANIZED_DIR / subject

        status = "organized"

    else:

        destination_folder = UNCLASSIFIED_DIR

        status = "unclassified"

    # --------------------------------------------------------
    # 3. MOVE FILE THROUGH FILE HANDLER
    # --------------------------------------------------------

    try:

        movement_result = move_file(
            source_path=str(source),
            destination_dir=str(destination_folder)
        )

    except FileOperationError:
        raise

    except Exception as error:

        raise FileOperationError(
            f"Document organization failed: {error}"
        ) from error

    # --------------------------------------------------------
    # 4. RETURN RESULT
    # --------------------------------------------------------

    new_path = movement_result["new_path"]

    return {

        "status": status,

        "original_path": str(source),

        "new_path": new_path,

        "subject": subject,

        "message": (
            "Document successfully organized."
            if status == "organized"
            else "Document moved to manual review."
        )

    }