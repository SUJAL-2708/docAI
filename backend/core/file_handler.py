import shutil

from pathlib import Path
from datetime import datetime


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

FOLDERS_DIR = BASE_DIR / "folders"

MANAGED_DIRECTORIES = {
    "Incoming": FOLDERS_DIR / "Incoming",
    "Organized": FOLDERS_DIR / "Organized",
    "Unclassified": FOLDERS_DIR / "Unclassified",
    "Errors": FOLDERS_DIR / "Errors"
}

SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".pptx",
    ".txt"
}


# ============================================================
# CUSTOM EXCEPTION
# ============================================================

class FileOperationError(Exception):
    """Raised when a file operation fails."""
    pass


# ============================================================
# DIRECTORY INITIALIZATION
# ============================================================

def initialize_directories():
    """
    Create AIDoc's managed directories if they do not exist.
    """

    for directory in MANAGED_DIRECTORIES.values():
        directory.mkdir(parents=True, exist_ok=True)


# ============================================================
# PATH VALIDATION
# ============================================================

def validate_file(file_path):
    """
    Validate whether a file exists and is supported.
    """

    path = Path(file_path).resolve()

    if not path.exists():
        raise FileOperationError(
            f"File does not exist: {path}"
        )

    if not path.is_file():
        raise FileOperationError(
            f"Path is not a file: {path}"
        )

    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise FileOperationError(
            f"Unsupported file format: {path.suffix}"
        )

    return path


def validate_managed_path(file_path):
    """
    Ensure a path belongs to one of AIDoc's managed folders.
    """

    path = Path(file_path).resolve()

    for directory in MANAGED_DIRECTORIES.values():

        try:
            path.relative_to(directory.resolve())
            return path

        except ValueError:
            continue

    raise FileOperationError(
        "File is outside AIDoc's managed directories."
    )


# ============================================================
# UNIQUE DESTINATION GENERATION
# ============================================================

def get_unique_destination(destination_dir, filename):
    """
    Generate a destination path without overwriting existing files.

    Example:
        notes.pdf
        notes_1.pdf
        notes_2.pdf
    """

    destination_dir = Path(destination_dir).resolve()

    destination_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    filename = Path(filename)

    destination = destination_dir / filename.name

    counter = 1

    while destination.exists():

        new_name = (
            f"{filename.stem}_{counter}"
            f"{filename.suffix}"
        )

        destination = destination_dir / new_name

        counter += 1

    return destination


# ============================================================
# SAFE FILE MOVING
# ============================================================

def move_file(source_path, destination_dir):
    """
    Move a document to another directory.

    The source and destination must be inside AIDoc's
    managed directories.

    Existing files are never overwritten.
    """

    source = validate_file(source_path)
    validate_managed_path(source)

    destination_dir = Path(destination_dir).resolve()

    # Destination must be inside a managed directory.
    managed_destination = False

    for directory in MANAGED_DIRECTORIES.values():

        try:
            destination_dir.relative_to(directory.resolve())
            managed_destination = True
            break

        except ValueError:
            continue

    if not managed_destination:

        raise FileOperationError(
            "Destination is outside AIDoc's managed directories."
        )

    if source.parent == destination_dir:

        raise FileOperationError(
            "Source and destination directories are identical."
        )

    destination = get_unique_destination(
        destination_dir,
        source.name
    )

    try:

        shutil.move(
            str(source),
            str(destination)
        )

    except OSError as error:

        raise FileOperationError(
            f"Could not move file: {error}"
        ) from error

    return {
        "status": "success",
        "operation": "move",
        "original_path": str(source),
        "new_path": str(destination),
        "filename": destination.name
    }


# ============================================================
# SAFE FILE COPYING
# ============================================================

def copy_file(source_path, destination_dir):
    """
    Copy a document without deleting the original.

    Both paths must belong to AIDoc's managed directories.
    """

    source = validate_file(source_path)
    validate_managed_path(source)

    destination_dir = Path(destination_dir).resolve()

    managed_destination = False

    for directory in MANAGED_DIRECTORIES.values():

        try:
            destination_dir.relative_to(directory.resolve())
            managed_destination = True
            break

        except ValueError:
            continue

    if not managed_destination:

        raise FileOperationError(
            "Destination is outside AIDoc's managed directories."
        )

    destination = get_unique_destination(
        destination_dir,
        source.name
    )

    try:

        shutil.copy2(
            str(source),
            str(destination)
        )

    except OSError as error:

        raise FileOperationError(
            f"Could not copy file: {error}"
        ) from error

    return {
        "status": "success",
        "operation": "copy",
        "original_path": str(source),
        "new_path": str(destination),
        "filename": destination.name
    }


# ============================================================
# SAFE FILE DELETION
# ============================================================

def delete_file(file_path):
    """
    Delete a document only if it is inside an AIDoc-managed folder.

    This operation is permanent.
    """

    path = validate_file(file_path)
    validate_managed_path(path)

    try:

        path.unlink()

    except OSError as error:

        raise FileOperationError(
            f"Could not delete file: {error}"
        ) from error

    return {
        "status": "success",
        "operation": "delete",
        "deleted_path": str(path),
        "filename": path.name
    }


# ============================================================
# FILE INFORMATION
# ============================================================

def get_file_info(file_path):
    """
    Return basic information about a document.
    """

    path = validate_file(file_path)

    stats = path.stat()

    return {
        "filename": path.name,
        "extension": path.suffix.lower(),
        "size_bytes": stats.st_size,
        "size_kb": round(stats.st_size / 1024, 2),
        "size_mb": round(stats.st_size / (1024 * 1024), 2),
        "created_at": datetime.fromtimestamp(
            stats.st_ctime
        ).isoformat(),
        "modified_at": datetime.fromtimestamp(
            stats.st_mtime
        ).isoformat(),
        "absolute_path": str(path)
    }


# ============================================================
# LIST DOCUMENTS
# ============================================================

def list_documents(directory_name="Incoming"):
    """
    List supported documents in a managed directory.
    """

    if directory_name not in MANAGED_DIRECTORIES:

        raise FileOperationError(
            f"Unknown directory: {directory_name}"
        )

    directory = MANAGED_DIRECTORIES[directory_name]

    directory.mkdir(parents=True, exist_ok=True)

    documents = []

    for path in directory.iterdir():

        if not path.is_file():
            continue

        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        documents.append({
            "filename": path.name,
            "path": str(path.resolve()),
            "extension": path.suffix.lower(),
            "size_bytes": path.stat().st_size
        })

    return documents