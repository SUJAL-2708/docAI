import hashlib
import json
import re
import unicodedata

from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

STORAGE_DIR = BASE_DIR / "storage"

HASH_DATABASE = STORAGE_DIR / "file_hashes.json"


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

def load_hash_database():
    """
    Load previously registered file hashes.
    """

    STORAGE_DIR.mkdir(parents=True, exist_ok=True)

    if not HASH_DATABASE.exists():
        return {}

    try:

        with open(HASH_DATABASE, "r", encoding="utf-8") as file:
            data = json.load(file)

        if isinstance(data, dict):
            return data

        return {}

    except (json.JSONDecodeError, OSError):

        print("[WARNING] Could not read hash database.")
        return {}


def save_hash_database(data):
    """
    Save hash records safely using a temporary file.
    """

    STORAGE_DIR.mkdir(parents=True, exist_ok=True)

    temp_file = HASH_DATABASE.with_suffix(".tmp")

    with open(temp_file, "w", encoding="utf-8") as file:

        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )

    temp_file.replace(HASH_DATABASE)


# ============================================================
# LEVEL 1: EXACT FILE DUPLICATE DETECTION
# ============================================================

def calculate_file_hash(file_path: str) -> str:
    """
    Calculate SHA-256 hash of the complete file.

    Identical file contents produce identical hashes,
    regardless of filename.
    """

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:

        for chunk in iter(
            lambda: file.read(1024 * 1024),
            b""
        ):

            sha256.update(chunk)

    return sha256.hexdigest()


def check_duplicate(file_hash: str):
    """
    Check whether an exact file hash already exists.

    Returns:
        Existing record if duplicate exists.
        None if file is new.
    """

    database = load_hash_database()

    return database.get(file_hash)


# ============================================================
# LEVEL 2: DOCUMENT TEXT NORMALIZATION
# ============================================================

def normalize_document_text(text: str) -> str:
    """
    Normalize extracted document text.

    Operations:
    - Unicode normalization
    - Case normalization
    - Newline normalization
    - Whitespace normalization
    """

    if not isinstance(text, str):
        text = str(text)

    # Normalize Unicode characters
    text = unicodedata.normalize("NFKC", text)

    # Ignore uppercase/lowercase differences
    text = text.casefold()

    # Normalize line endings
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Collapse repeated whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ============================================================
# LEVEL 2: EXTRACTED TEXT HASH
# ============================================================

def calculate_text_hash(text: str) -> str:
    """
    Generate SHA-256 hash from normalized extracted text.

    This allows documents with different file metadata
    or formatting to be detected when their normalized
    extracted text is identical.
    """

    normalized_text = normalize_document_text(text)

    return hashlib.sha256(
        normalized_text.encode("utf-8")
    ).hexdigest()


def check_text_duplicate(text_hash: str):
    """
    Search existing records for matching text hashes.

    Returns:
        Matching document record if found.
        None if no matching content exists.
    """

    database = load_hash_database()

    for file_hash, record in database.items():

        if not isinstance(record, dict):
            continue

        existing_text_hash = record.get("text_hash")

        if existing_text_hash == text_hash:

            return {
                "file_hash": file_hash,
                "filename": record.get("filename"),
                "path": record.get("path"),
                "text_hash": existing_text_hash
            }

    return None


# ============================================================
# REGISTER DOCUMENT
# ============================================================

def register_file(
    file_hash: str,
    filename: str,
    file_path: str,
    text_hash: str | None = None
):
    """
    Register a successfully organized document.

    Stores:
    - Original filename
    - Organized file path
    - Exact file SHA-256
    - Extracted-text SHA-256
    """

    database = load_hash_database()

    database[file_hash] = {
        "filename": filename,
        "path": str(file_path),
        "text_hash": text_hash
    }

    save_hash_database(database)

    return True


# ============================================================
# DATABASE STATISTICS
# ============================================================

def get_database_statistics():
    """
    Return the number of registered documents
    and the number having text hashes.
    """

    database = load_hash_database()

    total_files = len(database)

    text_hash_count = sum(
        1
        for record in database.values()
        if isinstance(record, dict)
        and record.get("text_hash")
    )

    return {
        "total_registered_files": total_files,
        "files_with_text_hash": text_hash_count
    }