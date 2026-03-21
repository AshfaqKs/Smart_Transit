"""
AI Face Detector — SmartTransit
Uses face_recognition library to compare an input image against
known faces (criminals + missing persons) stored in the uploads dir.

Returns:
    {
        "matched":      bool,
        "person_type":  "criminal" | "missing_person" | None,
        "reference_id": int | None,
        "confidence":   float | None,
    }
"""
import os
import numpy as np
from flask import current_app
from models.criminal import Criminal
from models.missing_person import MissingPerson

# Optional AI dependency — requires dlib (C++ compiler on Windows)
try:
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    print("[FaceDetector] face_recognition not installed. AI detection disabled.")
    print("[FaceDetector] To enable: pip install dlib face_recognition opencv-python")

# ── Load known faces from DB + photo files ────────────────────────────────────
def _load_known_encodings():
    """
    Read Criminal and MissingPerson records, load their photos,
    compute face encodings, and return two parallel lists.
    """
    known_encodings = []
    known_metadata  = []   # list of dicts {"person_type": ..., "reference_id": ...}

    upload_dir = current_app.config.get("UPLOAD_FOLDER", "uploads")

    # Criminals
    for criminal in Criminal.query.all():
        if criminal.photo:
            photo_path = os.path.join(upload_dir, criminal.photo)
            if os.path.isfile(photo_path):
                encodings = _encode_from_file(photo_path)
                for enc in encodings:
                    known_encodings.append(enc)
                    known_metadata.append({
                        "person_type":  "criminal",
                        "reference_id": criminal.criminal_id,
                    })

    # Missing Persons
    for mp in MissingPerson.query.all():
        if mp.photo:
            photo_path = os.path.join(upload_dir, mp.photo)
            if os.path.isfile(photo_path):
                encodings = _encode_from_file(photo_path)
                for enc in encodings:
                    known_encodings.append(enc)
                    known_metadata.append({
                        "person_type":  "missing_person",
                        "reference_id": mp.missing_id,
                    })

    return known_encodings, known_metadata


def _encode_from_file(path):
    """Return a list of face encodings from an image file."""
    try:
        image = face_recognition.load_image_file(path)
        return face_recognition.face_encodings(image)
    except Exception as e:
        print(f"[FaceDetector] Warning: could not encode {path}: {e}")
        return []


# ── Main detection function ────────────────────────────────────────────────────
def detect_face(image_path: str) -> dict:
    """
    Compare the image at `image_path` against all known faces.
    Returns match result dict.
    """
    default = {"matched": False, "person_type": None, "reference_id": None, "confidence": None}

    if not FACE_RECOGNITION_AVAILABLE:
        print("[FaceDetector] face_recognition not installed — skipping detection.")
        return {**default, "error": "face_recognition library not installed"}

    # Load and encode the query image
    query_encodings = _encode_from_file(image_path)
    if not query_encodings:
        print(f"[FaceDetector] No face found in: {image_path}")
        return default

    # Load known faces (done inside request context)
    known_encodings, known_metadata = _load_known_encodings()
    if not known_encodings:
        print("[FaceDetector] No known faces loaded.")
        return default

    # Compare each face found in the query image
    for query_enc in query_encodings:
        distances = face_recognition.face_distance(known_encodings, query_enc)
        best_idx  = int(np.argmin(distances))
        best_dist = float(distances[best_idx])

        THRESHOLD = 0.55  # lower = stricter match
        if best_dist <= THRESHOLD:
            confidence = round((1 - best_dist) * 100, 2)
            meta = known_metadata[best_idx]
            print(f"[FaceDetector] MATCH: {meta} confidence={confidence}%")
            return {
                "matched":      True,
                "person_type":  meta["person_type"],
                "reference_id": meta["reference_id"],
                "confidence":   confidence,
            }

    return default
