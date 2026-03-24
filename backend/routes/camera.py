"""
Camera Routes — SmartTransit
Receives image uploads, runs AI face detection, and returns/creates alerts.
"""
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required
from extensions import db
from models.camera_detection import CameraDetection
from models.bus import Bus
import os, uuid

camera_bp = Blueprint("camera", __name__, url_prefix="/api/camera")

# ── Face Detection Endpoint ───────────────────────────────────────────────────
@camera_bp.route("/detect", methods=["POST"])
@jwt_required(optional=True)
def detect():
    """
    Accepts multipart/form-data with fields:
      - image: the image file
      - bus_id: (optional) the bus this camera is on
    Runs face_recognition and stores a CameraDetection record if a match found.
    """
    from ai.face_detector import detect_face

    bus_id   = request.form.get("bus_id", type=int)
    location = request.form.get("location")

    if "image" not in request.files:
        return jsonify({"error": "No image provided"}), 400

    image_file = request.files["image"]
    upload_dir = current_app.config.get("UPLOAD_FOLDER", "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    filename = f"{uuid.uuid4().hex}_{image_file.filename}"
    image_path = os.path.join(upload_dir, filename)
    image_file.save(image_path)

    result = detect_face(image_path)

    if result["matched"]:
        detection = CameraDetection(
            bus_id=bus_id,
            detected_person_type=result["person_type"],
            reference_id=result["reference_id"],
            location=location,
            alert_status="unresolved",
        )
        db.session.add(detection)
        db.session.commit()
        return jsonify({
            "matched":      True,
            "person_type":  result["person_type"],
            "reference_id": result["reference_id"],
            "detection_id": detection.detection_id,
        }), 200

    return jsonify({"matched": False}), 200

# ── Get All Detections ────────────────────────────────────────────────────────
@camera_bp.route("/detections", methods=["GET"])
@jwt_required()
def get_detections():
    detections = CameraDetection.query.order_by(
        CameraDetection.detection_time.desc()
    ).all()
    return jsonify([d.to_dict() for d in detections])
