import time
import queue
import threading

from pathlib import Path

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from backend.core.processor import extract_document
from backend.core.classifier import process_classification
from backend.core.organizer import organize_document

from backend.core.duplicate_detector import (
    calculate_file_hash,
    calculate_text_hash,
    check_duplicate,
    check_text_duplicate,
    register_file
)


# ============================================================
# CONFIGURATION
# ============================================================

# Project root: docAI/
BASE_DIR = Path(__file__).resolve().parents[2]

INCOMING_DIR = BASE_DIR / "folders" / "Incoming"

SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".docx",
    ".pptx",
    ".txt"
}

STABILITY_INTERVAL = 1
STABILITY_REQUIRED_COUNT = 3
MAX_STABILITY_ATTEMPTS = 30


# ============================================================
# QUEUE MANAGEMENT
# ============================================================

document_queue = queue.Queue()

pending_files = set()
pending_lock = threading.Lock()

STOP_SIGNAL = object()


# ============================================================
# FILE STABILITY
# ============================================================

def wait_until_file_is_stable(file_path):

    previous_size = -1
    stable_count = 0

    for _ in range(MAX_STABILITY_ATTEMPTS):

        if not file_path.exists():
            return False

        try:
            current_size = file_path.stat().st_size
        except OSError:
            time.sleep(STABILITY_INTERVAL)
            continue

        if current_size > 0 and current_size == previous_size:
            stable_count += 1
        else:
            stable_count = 0

        if stable_count >= STABILITY_REQUIRED_COUNT:
            return True

        previous_size = current_size
        time.sleep(STABILITY_INTERVAL)

    return False


# ============================================================
# FILE VALIDATION
# ============================================================

def is_valid_incoming_file(file_path):

    try:
        resolved_path = Path(file_path).resolve()
        resolved_path.relative_to(INCOMING_DIR.resolve())
    except (ValueError, OSError):
        return False

    return (
        resolved_path.is_file()
        and resolved_path.suffix.lower() in SUPPORTED_EXTENSIONS
    )


# ============================================================
# DOCUMENT PROCESSING
# ============================================================

def process_incoming_document(file_path):

    file_path = Path(file_path)

    print("\n" + "=" * 60)
    print(f"PROCESSING: {file_path.name}")
    print("=" * 60)

    # STEP 1: FILE STABILITY

    print("\n[1/6] Checking file stability...")

    if not wait_until_file_is_stable(file_path):
        print("[ERROR] File did not become stable.")
        return

    print("[OK] File is stable.")

    # STEP 2: LEVEL 1 DUPLICATE DETECTION

    print("\n[2/6] Checking exact file duplicates...")

    file_hash = calculate_file_hash(str(file_path))

    print(f"File SHA-256: {file_hash}")

    duplicate_record = check_duplicate(file_hash)

    if duplicate_record is not None:

        print("\n[DUPLICATE] Exact file duplicate detected!")
        print("Original filename:", duplicate_record.get("filename"))
        print("Original location:", duplicate_record.get("path"))
        print("[SKIPPED] Document will not be processed again.")

        return

    print("[OK] No exact file duplicate found.")

    # STEP 3: EXTRACT DOCUMENT CONTENT

    print("\n[3/6] Extracting document content...")

    extracted_document = extract_document(str(file_path))

    extracted_text = extracted_document.get("text", "")

    if not extracted_text or not extracted_text.strip():

        print("[ERROR] No readable text extracted.")
        return

    print(f"[OK] Extracted {len(extracted_text)} characters.")

    # STEP 4: LEVEL 2 CONTENT DUPLICATE DETECTION

    print("\n[4/6] Checking extracted-text duplicates...")

    text_hash = calculate_text_hash(extracted_text)

    print(f"Text SHA-256: {text_hash}")

    text_duplicate = check_text_duplicate(text_hash)

    if text_duplicate is not None:

        print("\n[DUPLICATE] Matching document content detected!")
        print("Original filename:", text_duplicate.get("filename"))
        print("Original location:", text_duplicate.get("path"))
        print("[SKIPPED] AI classification will not run.")

        return

    print("[OK] No matching extracted text found.")

    # STEP 5: AI CLASSIFICATION

    print("\n[5/6] Running AI classification...")

    classification_result = process_classification(
        filename=file_path.name,
        extracted_text=extracted_text
    )

    classification = classification_result["classification"]
    decision = classification_result["decision"]

    print("\n[CLASSIFICATION RESULT]")
    print("Subject:", classification.get("primary_subject"))
    print("Topic:", classification.get("topic"))
    print("Confidence:", classification.get("confidence"))
    print("Decision:", decision)

    # STEP 6: ORGANIZATION

    print("\n[6/6] Organizing document...")

    organization_result = organize_document(
        file_path=str(file_path),
        classification=classification,
        decision=decision
    )

    print("\n[ORGANIZATION RESULT]")
    print("Status:", organization_result.get("status"))
    print("Subject:", organization_result.get("subject"))
    print("Message:", organization_result.get("message"))

    new_path = organization_result.get("new_path")

    if not new_path:

        print("[WARNING] No destination path returned.")
        print("[WARNING] Hashes were not registered.")
        return

    new_path = Path(new_path)

    if not new_path.exists():

        print("[WARNING] Organized file not found.")
        print("[WARNING] Hashes were not registered.")
        return

    # REGISTER BOTH HASHES

    register_file(
        file_hash=file_hash,
        filename=file_path.name,
        file_path=str(new_path),
        text_hash=text_hash
    )

    print("\n[REGISTERED]")
    print("[OK] Exact file hash registered.")
    print("[OK] Extracted-text hash registered.")

    print("\n" + "=" * 60)
    print("DOCUMENT PROCESSING COMPLETED")
    print("=" * 60)


# ============================================================
# WATCHDOG EVENT HANDLER
# ============================================================

class DocumentEventHandler(FileSystemEventHandler):

    def add_to_queue(self, file_path):

        path = Path(file_path)

        if not is_valid_incoming_file(path):
            return

        resolved_path = str(path.resolve())

        with pending_lock:

            if resolved_path in pending_files:
                return

            pending_files.add(resolved_path)

        print(f"\n[DETECTED] {path.name}")

        document_queue.put(path)

    def on_created(self, event):

        if not event.is_directory:
            self.add_to_queue(event.src_path)

    def on_moved(self, event):

        if not event.is_directory:
            self.add_to_queue(event.dest_path)


# ============================================================
# DOCUMENT WORKER
# ============================================================

def document_worker():

    print("[WORKER] Document worker started.")

    while True:

        file_path = document_queue.get()

        try:

            if file_path is STOP_SIGNAL:
                return

            process_incoming_document(file_path)

        except Exception as error:

            print(f"\n[ERROR] {error}")

        finally:

            if file_path is not STOP_SIGNAL:

                with pending_lock:
                    pending_files.discard(str(Path(file_path).resolve()))

            document_queue.task_done()


# ============================================================
# MONITOR STARTUP
# ============================================================

def start_monitor():

    INCOMING_DIR.mkdir(parents=True, exist_ok=True)

    print("\n" + "=" * 60)
    print("          AIDOC CONTENT-AWARE MONITOR")
    print("=" * 60)

    print(f"\nMonitoring: {INCOMING_DIR}")

    worker_thread = threading.Thread(
        target=document_worker,
        name="AIDoc-Document-Worker",
        daemon=False
    )

    worker_thread.start()

    observer = Observer()

    event_handler = DocumentEventHandler()

    observer.schedule(
        event_handler,
        str(INCOMING_DIR),
        recursive=False
    )

    observer.start()

    print("\n[ACTIVE] AIDoc is monitoring Incoming.")
    print("[LEVEL 1] Exact SHA-256 detection: ACTIVE")
    print("[LEVEL 2] Extracted-text detection: ACTIVE")
    print("[INFO] Add a document to Incoming.")
    print("[INFO] Press CTRL+C to stop.\n")

    try:

        while True:
            time.sleep(1)

    except KeyboardInterrupt:

        print("\n[SHUTDOWN] Stopping monitor...")

    finally:

        observer.stop()
        observer.join()

        document_queue.join()

        document_queue.put(STOP_SIGNAL)
        document_queue.join()

        worker_thread.join()

        print("[STOPPED] Monitor shut down successfully.")


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    start_monitor()