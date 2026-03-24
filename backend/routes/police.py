"""
Police Routes — SmartTransit
Criminal/missing person CRUD, complaint actions, and alert queries.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from extensions import db
from models.criminal import Criminal
from models.missing_person import MissingPerson
from models.complaint import Complaint
from models.camera_detection import CameraDetection
from models.review import Review
import os, uuid
from flask import current_app

police_bp = Blueprint("police", __name__, url_prefix="/api/police")

def _get_police_id():
    claims = get_jwt()
    if claims.get("role") != "police":
        return None, (jsonify({"error": "Forbidden"}), 403)
    return int(get_jwt_identity()), None

def _save_photo(file):
    """Save uploaded photo and return relative path."""
    upload_dir = current_app.config.get("UPLOAD_FOLDER", "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    filename = f"{uuid.uuid4().hex}_{file.filename}"
    path = os.path.join(upload_dir, filename)
    file.save(path)
    return filename

# ── Criminals ─────────────────────────────────────────────────────────────────
@police_bp.route("/criminals", methods=["GET"])
@jwt_required()
def get_criminals():
    police_id, err = _get_police_id()
    if err: return err
    items = Criminal.query.filter_by(police_id=police_id).all()
    return jsonify([c.to_dict() for c in items])

@police_bp.route("/criminals", methods=["POST"])
@jwt_required()
def add_criminal():
    police_id, err = _get_police_id()
    if err: return err
    photo_path = None
    if "photo" in request.files:
        photo_path = _save_photo(request.files["photo"])
    data = request.form if request.form else (request.get_json() or {})
    criminal = Criminal(
        name=data.get("name"), crime_type=data.get("crime_type"),
        description=data.get("description"), photo=photo_path,
        police_id=police_id
    )
    db.session.add(criminal)
    db.session.commit()
    return jsonify(criminal.to_dict()), 201

@police_bp.route("/criminals/<int:id>", methods=["PUT"])
@jwt_required()
def update_criminal(id):
    police_id, err = _get_police_id()
    if err: return err
    criminal = Criminal.query.get_or_404(id)
    data = request.get_json()
    for field in ["name", "crime_type", "description"]:
        if field in data:
            setattr(criminal, field, data[field])
    db.session.commit()
    return jsonify(criminal.to_dict())

@police_bp.route("/criminals/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_criminal(id):
    police_id, err = _get_police_id()
    if err: return err
    criminal = Criminal.query.get_or_404(id)
    db.session.delete(criminal)
    db.session.commit()
    return jsonify({"message": "Criminal record deleted"})

# ── Missing Persons ───────────────────────────────────────────────────────────
@police_bp.route("/missing", methods=["GET"])
@jwt_required()
def get_missing():
    police_id, err = _get_police_id()
    if err: return err
    items = MissingPerson.query.filter_by(police_id=police_id).all()
    return jsonify([m.to_dict() for m in items])

@police_bp.route("/missing", methods=["POST"])
@jwt_required()
def add_missing():
    police_id, err = _get_police_id()
    if err: return err
    photo_path = None
    if "photo" in request.files:
        photo_path = _save_photo(request.files["photo"])
    data = request.form if request.form else (request.get_json() or {})
    mp = MissingPerson(
        name=data.get("name"), age=data.get("age"),
        description=data.get("description"), photo=photo_path,
        police_id=police_id
    )
    db.session.add(mp)
    db.session.commit()
    return jsonify(mp.to_dict()), 201

@police_bp.route("/missing/<int:id>", methods=["PUT"])
@jwt_required()
def update_missing(id):
    police_id, err = _get_police_id()
    if err: return err
    mp = MissingPerson.query.get_or_404(id)
    data = request.get_json()
    for field in ["name", "age", "description"]:
        if field in data:
            setattr(mp, field, data[field])
    db.session.commit()
    return jsonify(mp.to_dict())

@police_bp.route("/missing/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_missing(id):
    police_id, err = _get_police_id()
    if err: return err
    mp = MissingPerson.query.get_or_404(id)
    db.session.delete(mp)
    db.session.commit()
    return jsonify({"message": "Missing person record deleted"})

# ── Complaints ────────────────────────────────────────────────────────────────
@police_bp.route("/complaints", methods=["GET"])
@jwt_required()
def get_complaints():
    police_id, err = _get_police_id()
    if err: return err
    items = Complaint.query.filter_by(police_id=police_id).all()
    return jsonify([c.to_dict() for c in items])

@police_bp.route("/complaints/<int:id>/action", methods=["PUT"])
@jwt_required()
def action_complaint(id):
    police_id, err = _get_police_id()
    if err: return err
    complaint = Complaint.query.get_or_404(id)
    data = request.get_json()
    complaint.status = data.get("status", complaint.status)
    complaint.reply  = data.get("reply",  complaint.reply)
    db.session.commit()
    return jsonify(complaint.to_dict())

# ── Alerts ────────────────────────────────────────────────────────────────────
@police_bp.route("/alerts", methods=["GET"])
@jwt_required()
def get_alerts():
    police_id, err = _get_police_id()
    if err: return err
    detections = CameraDetection.query.order_by(
        CameraDetection.detection_time.desc()
    ).limit(50).all()
    return jsonify([d.to_dict() for d in detections])

@police_bp.route("/alerts/<int:id>/resolve", methods=["PUT"])
@jwt_required()
def resolve_alert(id):
    police_id, err = _get_police_id()
    if err: return err
    detection = CameraDetection.query.get_or_404(id)
    detection.alert_status = "resolved"
    db.session.commit()
    return jsonify(detection.to_dict())

# ── Reviews ───────────────────────────────────────────────────────────────────
@police_bp.route("/reviews", methods=["GET"])
@jwt_required()
def get_reviews():
    police_id, err = _get_police_id()
    if err: return err
    items = Review.query.order_by(Review.review_id.desc()).all()
    return jsonify([r.to_dict() for r in items])
