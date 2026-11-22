from pathlib import Path


def extract_txt(file_path: str) -> str:

    """
    Extract text from TXT documents.
    """

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    encodings = [
        "utf-8",
        "utf-8-sig",
        "cp1252",
        "latin-1"
    ]

    for encoding in encodings:

        try:

            with open(
                file_path,
                "r",
                encoding=encoding
            ) as file:

                return file.read().strip()

        except UnicodeDecodeError:
            continue

    raise RuntimeError(
        "Unable to decode the text file."
    )