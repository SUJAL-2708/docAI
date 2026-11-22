from pathlib import Path

from backend.extractors.pdf_extractor import extract_pdf
from backend.extractors.docx_extractor import extract_docx
from backend.extractors.pptx_extractor import extract_pptx
from backend.extractors.txt_extractor import extract_txt


# ==========================================
# SUPPORTED FILE FORMATS
# ==========================================

EXTRACTORS = {

    ".pdf": extract_pdf,

    ".docx": extract_docx,

    ".pptx": extract_pptx,

    ".txt": extract_txt

}


# ==========================================
# DOCUMENT PROCESSOR
# ==========================================

def extract_document(file_path: str) -> dict:

    """
    Automatically identifies document format
    and extracts its text.
    """

    file_path = Path(file_path)

    if not file_path.exists():

        raise FileNotFoundError(
            f"Document not found: {file_path}"
        )

    if not file_path.is_file():

        raise ValueError(
            "Provided path is not a file."
        )

    extension = file_path.suffix.lower()

    extractor = EXTRACTORS.get(extension)

    if extractor is None:

        raise ValueError(
            f"Unsupported document format: {extension}"
        )

    extracted_text = extractor(str(file_path))

    return {

        "filename": file_path.name,

        "file_type": extension,

        "file_path": str(file_path.resolve()),

        "text": extracted_text,

        "character_count": len(extracted_text)

    }