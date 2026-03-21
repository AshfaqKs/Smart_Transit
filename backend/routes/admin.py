"""
Admin Routes — SmartTransit
Full CRUD for routes, driver approval, buses, complaints, users, reviews,
criminals, missing persons, and detection history.
All endpoints require JWT with role=admin.
"""
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt
from extensions import db
from models.route import Route
from models.route_point import RoutePoint
from models.bus_driver import BusDriver
from models.bus import Bus
from models.complaint import Complaint
from models.user import User
from models.review import Review
from models.app_review import AppReview
from models.police_station import PoliceStation
from models.criminal import Criminal
from models.missing_person import MissingPerson
from models.camera_detection import CameraDetection
from extensions import db, bcrypt
import os, uuid

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")

def _require_admin():
    claims = get_jwt()
    if claims.get("role") != "admin":
        return jsonify({"error": "Forbidden"}), 403
    return None

# ── Routes CRUD ──────────────────────────────────────────────────────────────
@admin_bp.route("/routes", methods=["GET"])
@jwt_required()
def get_routes():
    if (e := _require_admin()): return e
    return jsonify([r.to_dict() for r in Route.query.all()])

@admin_bp.route("/routes", methods=["POST"])
@jwt_required()
def create_route():
    if (e := _require_admin()): return e
    data = request.get_json()
    route = Route(
        route_name=data["route_name"],
        start_point=data["start_point"],
        end_point=data["end_point"]
    )
    db.session.add(route)
    db.session.commit()
    return jsonify(route.to_dict()), 201

@admin_bp.route("/routes/<int:id>", methods=["PUT"])
@jwt_required()
def update_route(id):
    if (e := _require_admin()): return e
    route = Route.query.get_or_404(id)
    data = request.get_json()
    for field in ["route_name", "start_point", "end_point"]:
        if field in data:
            setattr(route, field, data[field])
    db.session.commit()
    return jsonify(route.to_dict())

@admin_bp.route("/routes/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_route(id):
    if (e := _require_admin()): return e
    route = Route.query.get_or_404(id)
    db.session.delete(route)
    db.session.commit()
    return jsonify({"message": "Route deleted"})

# ── Route Points (Stops) ──────────────────────────────────────────────────────
@admin_bp.route("/routes/<int:route_id>/stops", methods=["GET"])
@jwt_required()
def get_route_stops(route_id):
    if (e := _require_admin()): return e
    Route.query.get_or_404(route_id)
    stops = RoutePoint.query.filter_by(route_id=route_id).order_by(RoutePoint.stop_order).all()
    return jsonify([s.to_dict() for s in stops])

@admin_bp.route("/routes/<int:route_id>/stops", methods=["POST"])
@jwt_required()
def add_route_stop(route_id):
    if (e := _require_admin()): return e
    Route.query.get_or_404(route_id)
    data = request.get_json()
    stop = RoutePoint(
        route_id=route_id,
        stop_name=data["stop_name"],
        stop_order=data["stop_order"]
    )
    db.session.add(stop)
    db.session.commit()
    return jsonify(stop.to_dict()), 201

@admin_bp.route("/routes/<int:route_id>/stops/<int:stop_id>", methods=["DELETE"])
@jwt_required()
def delete_route_stop(route_id, stop_id):
    if (e := _require_admin()): return e
    stop = RoutePoint.query.get_or_404(stop_id)
    if stop.route_id != route_id:
        return jsonify({"error": "Mismatch between route and stop"}), 400
    db.session.delete(stop)
    
    # Optional: Reorder remaining stops automatically here if needed
    
    db.session.commit()
    return jsonify({"message": "Stop deleted"})

# ── Drivers ──────────────────────────────────────────────────────────────────
@admin_bp.route("/drivers", methods=["GET"])
@jwt_required()
def get_drivers():
    if (e := _require_admin()): return e
    return jsonify([d.to_dict() for d in BusDriver.query.all()])

@admin_bp.route("/drivers/<int:id>/approve", methods=["PUT"])
@jwt_required()
def approve_driver(id):
    if (e := _require_admin()): return e
    driver = BusDriver.query.get_or_404(id)
    driver.approval_status = True
    db.session.commit()
    return jsonify({"message": "Driver approved", "driver": driver.to_dict()})

@admin_bp.route("/drivers/<int:id>/reject", methods=["PUT"])
@jwt_required()
def reject_driver(id):
    if (e := _require_admin()): return e
    driver = BusDriver.query.get_or_404(id)
    driver.approval_status = False
    db.session.commit()
    return jsonify({"message": "Driver rejected", "driver": driver.to_dict()})

@admin_bp.route("/drivers/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_driver(id):
    if (e := _require_admin()): return e
    driver = BusDriver.query.get_or_404(id)
    db.session.delete(driver)
    db.session.commit()
    return jsonify({"message": "Driver deleted"})

# ── Buses ─────────────────────────────────────────────────────────────────────
@admin_bp.route("/buses", methods=["GET"])
@jwt_required()
def get_buses():
    if (e := _require_admin()): return e
    return jsonify([b.to_dict() for b in Bus.query.all()])

@admin_bp.route("/buses", methods=["POST"])
@jwt_required()
def create_bus():
    if (e := _require_admin()): return e
    data = request.get_json()
    bus = Bus(
        bus_number = data["bus_number"],
        route_id   = data.get("route_id") or None,
        driver_id  = data.get("driver_id") or None,
        status     = data.get("status", "active"),
        current_location = data.get("current_location", ""),
    )
    db.session.add(bus)
    db.session.commit()
    return jsonify(bus.to_dict()), 201

@admin_bp.route("/buses/<int:id>", methods=["PUT"])
@jwt_required()
def update_bus(id):
    if (e := _require_admin()): return e
    bus  = Bus.query.get_or_404(id)
    data = request.get_json()
    for field in ["bus_number", "status", "current_location"]:
        if field in data:
            setattr(bus, field, data[field])
    # Allow null to unassign
    if "route_id"  in data: bus.route_id  = data["route_id"]  or None
    if "driver_id" in data: bus.driver_id = data["driver_id"] or None
    db.session.commit()
    return jsonify(bus.to_dict())

@admin_bp.route("/buses/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_bus(id):
    if (e := _require_admin()): return e
    bus = Bus.query.get_or_404(id)
    db.session.delete(bus)
    db.session.commit()
    return jsonify({"message": "Bus deleted"})

# ── Complaints ────────────────────────────────────────────────────────────────
@admin_bp.route("/complaints", methods=["GET"])
@jwt_required()
def get_complaints():
    if (e := _require_admin()): return e
    return jsonify([c.to_dict() for c in Complaint.query.all()])

@admin_bp.route("/complaints/<int:id>/reply", methods=["PUT"])
@jwt_required()
def reply_complaint(id):
    if (e := _require_admin()): return e
    complaint = Complaint.query.get_or_404(id)
    data = request.get_json()
    complaint.reply = data.get("reply")
    complaint.status = data.get("status", complaint.status)
    if "police_id" in data:
        complaint.police_id = data["police_id"] or None
    db.session.commit()
    return jsonify(complaint.to_dict())

# ── Users ─────────────────────────────────────────────────────────────────────
@admin_bp.route("/users", methods=["GET"])
@jwt_required()
def get_users():
    if (e := _require_admin()): return e
    return jsonify([u.to_dict() for u in User.query.all()])

# ── Police Stations ───────────────────────────────────────────────────────────
@admin_bp.route("/police", methods=["GET"])
@jwt_required()
def get_police():
    if (e := _require_admin()): return e
    return jsonify([p.to_dict() for p in PoliceStation.query.all()])

@admin_bp.route("/police", methods=["POST"])
@jwt_required()
def add_police():
    if (e := _require_admin()): return e
    data = request.get_json()
    # If a password is provided by the admin, hash it. Otherwise fallback.
    pwd = data.get("password") or "password123"
    hashed = bcrypt.generate_password_hash(pwd).decode()
    station = PoliceStation(
        station_name=data["station_name"],
        location=data.get("location", ""),
        contact_number=data.get("contact_number", ""),
        email=data["email"],
        password=hashed
    )
    db.session.add(station)
    db.session.commit()
    return jsonify(station.to_dict()), 201

# ── Reviews ───────────────────────────────────────────────────────────────────
@admin_bp.route("/reviews", methods=["GET"])
@jwt_required()
def get_reviews():
    if (e := _require_admin()): return e
    return jsonify([r.to_dict() for r in Review.query.all()])

@admin_bp.route("/app-reviews", methods=["GET"])
@jwt_required()
def get_app_reviews():
    if (e := _require_admin()): return e
    return jsonify([ar.to_dict() for ar in AppReview.query.all()])


# ── Helper: save uploaded photo ───────────────────────────────────────────────
def _save_photo(file_field_name="photo"):
    """Save an uploaded photo to the uploads folder. Returns filename or None."""
    f = request.files.get(file_field_name)
    if not f or f.filename == "":
        return None
    upload_dir = current_app.config.get("UPLOAD_FOLDER", "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    filename = f"{uuid.uuid4().hex}_{f.filename}"
    f.save(os.path.join(upload_dir, filename))
    return filename


# ── Criminals CRUD ────────────────────────────────────────────────────────────
@admin_bp.route("/criminals", methods=["GET"])
@jwt_required()
def get_criminals():
    if (e := _require_admin()): return e
    return jsonify([c.to_dict() for c in Criminal.query.all()])


@admin_bp.route("/criminals", methods=["POST"])
@jwt_required()
def add_criminal():
    if (e := _require_admin()): return e
    name       = request.form.get("name", "").strip()
    crime_type = request.form.get("crime_type", "").strip()
    description = request.form.get("description", "").strip()
    police_id  = request.form.get("police_id") or None

    if not name:
        return jsonify({"error": "name is required"}), 400

    photo_filename = _save_photo("photo")
    c = Criminal(
        name=name,
        crime_type=crime_type or None,
        description=description or None,
        photo=photo_filename,
        police_id=int(police_id) if police_id else None,
    )
    db.session.add(c)
    db.session.commit()
    return jsonify(c.to_dict()), 201


@admin_bp.route("/criminals/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_criminal(id):
    if (e := _require_admin()): return e
    c = Criminal.query.get_or_404(id)
    # Remove photo file if it exists
    if c.photo:
        upload_dir = current_app.config.get("UPLOAD_FOLDER", "uploads")
        path = os.path.join(upload_dir, c.photo)
        if os.path.isfile(path):
            os.remove(path)
    db.session.delete(c)
    db.session.commit()
    return jsonify({"message": "Criminal deleted"})


# ── Missing Persons CRUD ──────────────────────────────────────────────────────
@admin_bp.route("/missing-persons", methods=["GET"])
@jwt_required()
def get_missing_persons():
    if (e := _require_admin()): return e
    return jsonify([mp.to_dict() for mp in MissingPerson.query.all()])


@admin_bp.route("/missing-persons", methods=["POST"])
@jwt_required()
def add_missing_person():
    if (e := _require_admin()): return e
    name       = request.form.get("name", "").strip()
    age        = request.form.get("age") or None
    description = request.form.get("description", "").strip()
    police_id  = request.form.get("police_id") or None

    if not name:
        return jsonify({"error": "name is required"}), 400

    photo_filename = _save_photo("photo")
    mp = MissingPerson(
        name=name,
        age=int(age) if age else None,
        description=description or None,
        photo=photo_filename,
        police_id=int(police_id) if police_id else None,
    )
    db.session.add(mp)
    db.session.commit()
    return jsonify(mp.to_dict()), 201


@admin_bp.route("/missing-persons/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_missing_person(id):
    if (e := _require_admin()): return e
    mp = MissingPerson.query.get_or_404(id)
    if mp.photo:
        upload_dir = current_app.config.get("UPLOAD_FOLDER", "uploads")
        path = os.path.join(upload_dir, mp.photo)
        if os.path.isfile(path):
            os.remove(path)
    db.session.delete(mp)
    db.session.commit()
    return jsonify({"message": "Missing person deleted"})


# ── Detection History ─────────────────────────────────────────────────────────
@admin_bp.route("/detections", methods=["GET"])
@jwt_required()
def get_admin_detections():
    if (e := _require_admin()): return e
    detections = CameraDetection.query.order_by(
        CameraDetection.detection_time.desc()
    ).all()

    results = []
    for d in detections:
        row = d.to_dict()
        # Enrich with name/photo from the referenced record
        if d.detected_person_type == "criminal":
            ref = Criminal.query.get(d.reference_id)
            row["person_name"] = ref.name if ref else "Unknown"
            row["person_photo"] = ref.photo if ref else None
        elif d.detected_person_type == "missing_person":
            ref = MissingPerson.query.get(d.reference_id)
            row["person_name"] = ref.name if ref else "Unknown"
            row["person_photo"] = ref.photo if ref else None
        else:
            row["person_name"] = "Unknown"
            row["person_photo"] = None
        results.append(row)
    return jsonify(results)


@admin_bp.route("/detections/<int:id>/resolve", methods=["PUT"])
@jwt_required()
def resolve_detection(id):
    if (e := _require_admin()): return e
    detection = CameraDetection.query.get_or_404(id)
    detection.alert_status = "resolved"
    db.session.commit()
    return jsonify(detection.to_dict())

