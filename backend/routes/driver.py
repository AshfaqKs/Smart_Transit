"""
Driver Routes — SmartTransit
Profile management, live location update, schedule, and alert endpoints.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from extensions import db
from models.bus_driver import BusDriver
from models.bus import Bus
from models.camera_detection import CameraDetection
from models.complaint import Complaint
from models.review import Review
from models.criminal import Criminal
from models.missing_person import MissingPerson
from utils.geocoding import get_location_name

driver_bp = Blueprint("driver", __name__, url_prefix="/api/driver")

def _get_driver_id():
    claims = get_jwt()
    if claims.get("role") != "driver":
        return None, (jsonify({"error": "Forbidden"}), 403)
    return int(get_jwt_identity()), None

# ── Profile ───────────────────────────────────────────────────────────────────
@driver_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    driver_id, err = _get_driver_id()
    if err: return err
    driver = BusDriver.query.get_or_404(driver_id)
    return jsonify(driver.to_dict())

@driver_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    driver_id, err = _get_driver_id()
    if err: return err
    driver = BusDriver.query.get_or_404(driver_id)
    data = request.get_json()
    for field in ["name", "phone_number"]:
        if field in data:
            setattr(driver, field, data[field])
    db.session.commit()
    return jsonify(driver.to_dict())

# ── Live GPS Location ──────────────────────────────────────────────────────────
@driver_bp.route("/location", methods=["PUT"])
@jwt_required()
def update_location():
    driver_id, err = _get_driver_id()
    if err: return err
    data = request.get_json()
    bus = Bus.query.filter_by(driver_id=driver_id).first()
    if not bus:
        return jsonify({"error": "No bus assigned to this driver"}), 404
    new_location = data.get("location", bus.current_location)
    is_changed = new_location != bus.current_location
    is_missing_name = not bus.location_name

    if is_changed or is_missing_name:
        bus.current_location = new_location
        # Trigger reverse geocoding
        parts = new_location.split(",")
        if len(parts) == 2:
            name = get_location_name(parts[0].strip(), parts[1].strip())
            if name:
                bus.location_name = name
    db.session.commit()
    return jsonify({"message": "Location updated", "bus": bus.to_dict()})

# ── Schedule ──────────────────────────────────────────────────────────────────
@driver_bp.route("/schedule", methods=["GET"])
@jwt_required()
def get_schedule():
    driver_id, err = _get_driver_id()
    if err: return err
    bus = Bus.query.filter_by(driver_id=driver_id).first()
    if not bus:
        return jsonify({"schedule": None, "message": "No bus assigned"})
    return jsonify({
        "bus": bus.to_dict(),
        "route": bus.route.to_dict() if bus.route else None,
    })

# ── Alerts (criminal / missing detections on assigned bus) ────────────────────
@driver_bp.route("/alerts", methods=["GET"])
@jwt_required()
def get_alerts():
    driver_id, err = _get_driver_id()
    if err: return err
    bus = Bus.query.filter_by(driver_id=driver_id).first()
    if not bus:
        return jsonify([])
    detections = CameraDetection.query.filter_by(bus_id=bus.bus_id).order_by(
        CameraDetection.detection_time.desc()
    ).all()
    return jsonify([d.to_dict() for d in detections])

# ── Reviews ───────────────────────────────────────────────────────────────────
@driver_bp.route("/reviews", methods=["GET"])
@jwt_required()
def get_reviews():
    driver_id, err = _get_driver_id()
    if err: return err
    bus = Bus.query.filter_by(driver_id=driver_id).first()
"""
Driver Routes — SmartTransit
Profile management, live location update, schedule, and alert endpoints.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from extensions import db
from models.bus_driver import BusDriver
from models.bus import Bus
from models.camera_detection import CameraDetection
from models.complaint import Complaint
from models.review import Review
from models.criminal import Criminal
from models.missing_person import MissingPerson
from utils.geocoding import get_location_name

driver_bp = Blueprint("driver", __name__, url_prefix="/api/driver")

def _get_driver_id():
    claims = get_jwt()
    if claims.get("role") != "driver":
        return None, (jsonify({"error": "Forbidden"}), 403)
    return int(get_jwt_identity()), None

# ── Profile ───────────────────────────────────────────────────────────────────
@driver_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    driver_id, err = _get_driver_id()
    if err: return err
    driver = BusDriver.query.get_or_404(driver_id)
    return jsonify(driver.to_dict())

@driver_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    driver_id, err = _get_driver_id()
    if err: return err
    driver = BusDriver.query.get_or_404(driver_id)
    data = request.get_json()
    for field in ["name", "phone_number"]:
        if field in data:
            setattr(driver, field, data[field])
    db.session.commit()
    return jsonify(driver.to_dict())

# ── Live GPS Location ──────────────────────────────────────────────────────────
@driver_bp.route("/location", methods=["PUT"])
@jwt_required()
def update_location():
    driver_id, err = _get_driver_id()
    if err: return err
    data = request.get_json()
    bus = Bus.query.filter_by(driver_id=driver_id).first()
    if not bus:
        return jsonify({"error": "No bus assigned to this driver"}), 404
    new_location = data.get("location", bus.current_location)
    is_changed = new_location != bus.current_location
    is_missing_name = not bus.location_name

    if is_changed or is_missing_name:
        bus.current_location = new_location
        # Trigger reverse geocoding
        parts = new_location.split(",")
        if len(parts) == 2:
            name = get_location_name(parts[0].strip(), parts[1].strip())
            if name:
                bus.location_name = name
    db.session.commit()
    return jsonify({"message": "Location updated", "bus": bus.to_dict()})

# ── Schedule ──────────────────────────────────────────────────────────────────
@driver_bp.route("/schedule", methods=["GET"])
@jwt_required()
def get_schedule():
    driver_id, err = _get_driver_id()
    if err: return err
    bus = Bus.query.filter_by(driver_id=driver_id).first()
    if not bus:
        return jsonify({"schedule": None, "message": "No bus assigned"})
    return jsonify({
        "bus": bus.to_dict(),
        "route": bus.route.to_dict() if bus.route else None,
    })

# ── Alerts (criminal / missing detections on assigned bus) ────────────────────
@driver_bp.route("/alerts", methods=["GET"])
@jwt_required()
def get_alerts():
    driver_id, err = _get_driver_id()
    if err: return err
    bus = Bus.query.filter_by(driver_id=driver_id).first()
    if not bus:
        return jsonify([])
    detections = CameraDetection.query.filter_by(bus_id=bus.bus_id).order_by(
        CameraDetection.detection_time.desc()
    ).all()
    return jsonify([d.to_dict() for d in detections])

# ── Reviews ───────────────────────────────────────────────────────────────────
@driver_bp.route("/reviews", methods=["GET"])
@jwt_required()
def get_reviews():
    driver_id, err = _get_driver_id()
    if err: return err
    bus = Bus.query.filter_by(driver_id=driver_id).first()
    if not bus:
        return jsonify([])
    reviews = Review.query.filter_by(bus_id=bus.bus_id).order_by(Review.review_id.desc()).all()
    return jsonify([r.to_dict() for r in reviews])

# -- Complaints (for driver's bus) --------------------------------------------
@driver_bp.route("/complaints", methods=["GET"])
@jwt_required()
def get_driver_complaints():
    driver_id, err = _get_driver_id()
    if err: return err
    bus = Bus.query.filter_by(driver_id=driver_id).first()
    if not bus:
        return jsonify([])

    from sqlalchemy import or_
    complaints = Complaint.query.filter(
        or_(
            Complaint.bus_id == bus.bus_id,
            Complaint.bus_registration == bus.bus_number
        )
    ).order_by(Complaint.created_at.desc()).all()

    result = []
    for c in complaints:
        d = c.to_dict()
        if not d.get("bus_registration"):
            d["bus_registration"] = bus.bus_number
        result.append(d)
    return jsonify(result)
