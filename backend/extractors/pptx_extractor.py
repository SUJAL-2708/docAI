from pptx import Presentation
from pathlib import Path


def extract_pptx(file_path: str) -> str:

    """
    Extract text from PowerPoint presentations.
    """

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    extracted_text = []

    try:

        presentation = Presentation(file_path)

        for slide_number, slide in enumerate(
            presentation.slides,
            start=1
        ):

            slide_text = []

            for shape in slide.shapes:

                if shape.has_text_frame:

                    text = shape.text.strip()

                    if text:
                        slide_text.append(text)

                if shape.has_table:

                    for row in shape.table.rows:

                        row_text = [
                            cell.text.strip()
                            for cell in row.cells
                        ]

                        slide_text.append(
                            " | ".join(row_text)
                        )

            if slide_text:

                extracted_text.append(
                    f"\n--- Slide {slide_number} ---\n"
                    + "\n".join(slide_text)
                )

        return "\n".join(extracted_text).strip()

    except Exception as error:

        raise RuntimeError(
            f"PPTX extraction failed: {error}"
        ) from error