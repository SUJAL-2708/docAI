import fitz
from pathlib import Path


def extract_pdf(file_path: str) -> str:

    """
    Extract text from PDF documents using PyMuPDF.
    """

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    extracted_text = []

    try:

        with fitz.open(file_path) as document:

            for page_number, page in enumerate(document, start=1):

                text = page.get_text("text")

                if text.strip():

                    extracted_text.append(
                        f"\n--- Page {page_number} ---\n{text}"
                    )

        return "\n".join(extracted_text).strip()

    except Exception as error:

        raise RuntimeError(
            f"PDF extraction failed: {error}"
        ) from error