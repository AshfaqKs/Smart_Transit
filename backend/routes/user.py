"""
User Routes — SmartTransit
Profile, buses, routes, complaints, reviews, and public alerts.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from extensions import db
from models.user import User
from models.bus import Bus
from models.route import Route
from models.complaint import Complaint
from models.review import Review
from models.app_review import AppReview
from models.camera_detection import CameraDetection
from models.criminal import Criminal
from models.missing_person import MissingPerson

user_bp = Blueprint("user", __name__, url_prefix="/api/user")

def _get_user_id():
    claims = get_jwt()
    if claims.get("role") != "user":
        return None, (jsonify({"error": "Forbidden"}), 403)
    return int(get_jwt_identity()), None

# ── Profile ───────────────────────────────────────────────────────────────────
@user_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    user_id, err = _get_user_id()
    if err: return err
    return jsonify(User.query.get_or_404(user_id).to_dict())

@user_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    user_id, err = _get_user_id()
    if err: return err
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    for field in ["name", "phone_number", "address"]:
        if field in data:
            setattr(user, field, data[field])
    db.session.commit()
    return jsonify(user.to_dict())

# ── Buses ─────────────────────────────────────────────────────────────────────
@user_bp.route("/buses/nearest", methods=["GET"])
@jwt_required()
def get_nearest_buses():
    _get_user_id()
    buses = Bus.query.filter_by(status="active").all()
    return jsonify([b.to_dict() for b in buses])

# ── Routes ────────────────────────────────────────────────────────────────────
@user_bp.route("/routes", methods=["GET"])
@jwt_required()
def get_routes():
    _get_user_id()
    return jsonify([r.to_dict() for r in Route.query.all()])

# ── Complaints ────────────────────────────────────────────────────────────────
@user_bp.route("/complaints", methods=["POST"])
@jwt_required()
def file_complaint():
    user_id, err = _get_user_id()
    if err: return err
    data = request.get_json()
    try:
        complaint = Complaint(
            user_id=user_id,
            bus_id=data.get("bus_id"),
            police_id=data.get("police_id"),
            complaint_type=data.get("complaint_type"),
            description=data.get("description"),
        )
        db.session.add(complaint)
        db.session.commit()
        return jsonify(complaint.to_dict()), 201
    except Exception as e:
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@user_bp.route("/complaints", methods=["GET"])
@jwt_required()
def get_my_complaints():
    user_id, err = _get_user_id()
    if err: return err
    items = Complaint.query.filter_by(user_id=user_id).all()
    return jsonify([c.to_dict() for c in items])

# ── Reviews ───────────────────────────────────────────────────────────────────
@user_bp.route("/reviews", methods=["POST"])
@jwt_required()
def post_review():
    user_id, err = _get_user_id()
    if err: return err
    data = request.get_json()
    review = Review(
        user_id=user_id,
        bus_id=data["bus_id"],
        rating=data["rating"],
        comments=data.get("comments"),
    )
    db.session.add(review)
    db.session.commit()
    return jsonify(review.to_dict()), 201

# ── App Reviews ───────────────────────────────────────────────────────────────
@user_bp.route("/app-reviews", methods=["POST"])
@jwt_required()
def post_app_review():
    user_id, err = _get_user_id()
    if err: return err
    data = request.get_json()
    app_review = AppReview(
        user_id=user_id,
        rating=data["rating"],
        comments=data.get("comments"),
    )
    db.session.add(app_review)
    db.session.commit()
    return jsonify(app_review.to_dict()), 201

# ── Alerts (public — camera detections) ──────────────────────────────────────
@user_bp.route("/alerts", methods=["GET"])
@jwt_required()
def get_alerts():
    _get_user_id()
    detections = CameraDetection.query.order_by(
        CameraDetection.detection_time.desc()
    ).limit(30).all()
    return jsonify([d.to_dict() for d in detections])

# ── Safety Records (Criminals & Missing Persons) ──────────────────────────────
@user_bp.route("/criminals", methods=["GET"])
@jwt_required()
def get_criminals():
    _get_user_id()
    return jsonify([c.to_dict() for c in Criminal.query.all()])

@user_bp.route("/missing", methods=["GET"])
@jwt_required()
def get_missing():
    _get_user_id()
    return jsonify([m.to_dict() for m in MissingPerson.query.all()])
