"""
Driver Routes — SmartTransit
Profile management, live location update, schedule, and alert endpoints.
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from extensions import db
from models.bus_driver import BusDriver
from models.bus import Bus
from models.camera_detection import CameraDetection
from models.review import Review
from models.complaint import Complaint
from models.trip import Trip
from models.user import User
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

# ── Trips (History, Current, Future) ──────────────────────────────────────────
@driver_bp.route("/trips", methods=["GET"])
@jwt_required()
def get_trips():
    driver_id, err = _get_driver_id()
    if err: return err
    trips = Trip.query.filter_by(driver_id=driver_id).order_by(Trip.scheduled_time.desc()).all()
    # Filter into categories
    now = datetime.utcnow()
    history = [t.to_dict() for t in trips if t.status == 'completed']
    current = [t.to_dict() for t in trips if t.status == 'ongoing']
    future  = [t.to_dict() for t in trips if t.status == 'scheduled']
    
    return jsonify({
        "history": history,
        "current": current,
        "future":  future
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
    
    # Detections
    detections = CameraDetection.query.filter_by(bus_id=bus.bus_id).order_by(
        CameraDetection.detection_time.desc()
    ).all()
    
    # Complaints
    complaints = Complaint.query.filter_by(bus_id=bus.bus_id).order_by(
        Complaint.created_at.desc()
    ).all()
    
    alerts = []
    for d in detections:
        item = d.to_dict()
        item["type"] = "detection"
        alerts.append(item)
        
    for c in complaints:
        item = c.to_dict()
        item["type"] = "complaint"
        user = User.query.get(c.user_id)
        item["passenger_name"] = user.name if user else "Unknown"
        alerts.append(item)
        
    # Sort by time
    alerts.sort(key=lambda x: x.get("detection_time") or x.get("created_at"), reverse=True)
    
    return jsonify(alerts)

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
