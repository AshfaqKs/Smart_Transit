"""
Auth Routes — SmartTransit
Handles login/register for all roles: admin, user, driver, police.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from extensions import db, bcrypt
from models.admin import Admin
from models.user import User
from models.bus_driver import BusDriver
from models.police_station import PoliceStation

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

# ── Helper ──────────────────────────────────────────────────────────────────
def _bad(msg, code=400):
    return jsonify({"error": msg}), code

def _token(identity, role):
    # Use simple string identity + additional_claims for role
    # (Flask-JWT-Extended 4.x serializes dict identities unreliably)
    token = create_access_token(
        identity=str(identity),
        additional_claims={"role": role}
    )
    return jsonify({"token": token, "role": role})

# ── Admin Login ──────────────────────────────────────────────────────────────
@auth_bp.route("/admin/login", methods=["POST"])
def admin_login():
    data = request.get_json()
    admin = Admin.query.filter_by(email=data.get("email")).first()
    if not admin or not bcrypt.check_password_hash(admin.password, data.get("password", "")):
        return _bad("Invalid credentials", 401)
    return _token(admin.admin_id, "admin")

# ── User Register / Login ────────────────────────────────────────────────────
@auth_bp.route("/user/register", methods=["POST"])
def user_register():
    data = request.get_json()
    if User.query.filter_by(email=data.get("email")).first():
        return _bad("Email already registered")
    hashed = bcrypt.generate_password_hash(data["password"]).decode()
    user = User(
        name=data.get("name"), email=data["email"],
        password=hashed, phone_number=data.get("phone_number"),
        address=data.get("address")
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User registered successfully", "user_id": user.user_id}), 201

@auth_bp.route("/user/login", methods=["POST"])
def user_login():
    data = request.get_json()
    user = User.query.filter_by(email=data.get("email")).first()
    if not user or not bcrypt.check_password_hash(user.password, data.get("password", "")):
        return _bad("Invalid credentials", 401)
    return _token(user.user_id, "user")

# ── Driver Register / Login ──────────────────────────────────────────────────
@auth_bp.route("/driver/register", methods=["POST"])
def driver_register():
    data = request.get_json()
    if BusDriver.query.filter_by(email=data.get("email")).first():
        return _bad("Email already registered")
    hashed = bcrypt.generate_password_hash(data["password"]).decode()
    driver = BusDriver(
        name=data.get("name"), email=data["email"],
        password=hashed, phone_number=data.get("phone_number"),
        license_number=data.get("license_number"),
        approval_status=None   # null = pending admin approval
    )
    db.session.add(driver)
    db.session.commit()
    return jsonify({"message": "Driver registered. Awaiting admin approval.", "driver_id": driver.driver_id}), 201

@auth_bp.route("/driver/login", methods=["POST"])
def driver_login():
    data = request.get_json()
    driver = BusDriver.query.filter_by(email=data.get("email")).first()
    if not driver or not bcrypt.check_password_hash(driver.password, data.get("password", "")):
        return _bad("Invalid credentials", 401)
    if driver.approval_status is not True:
        msg = "Account rejected by admin." if driver.approval_status is False else "Account pending admin approval."
        return _bad(msg, 403)
    return _token(driver.driver_id, "driver")

# ── Police Register / Login ──────────────────────────────────────────────────
@auth_bp.route("/police/register", methods=["POST"])
def police_register():
    data = request.get_json()
    if PoliceStation.query.filter_by(email=data.get("email")).first():
        return _bad("Email already registered")
    hashed = bcrypt.generate_password_hash(data["password"]).decode()
    station = PoliceStation(
        station_name   = data.get("station_name", "Unnamed Station"),
        location       = data.get("location", ""),
        contact_number = data.get("contact_number", data.get("phone_number", "")),
        email          = data["email"],
        password       = hashed,
    )
    db.session.add(station)
    db.session.commit()
    return jsonify({"message": "Police station registered successfully.", "police_id": station.police_id}), 201

@auth_bp.route("/police/login", methods=["POST"])
def police_login():
    data = request.get_json()
    station = PoliceStation.query.filter_by(email=data.get("email")).first()
    if not station or not bcrypt.check_password_hash(station.password, data.get("password", "")):
        return _bad("Invalid credentials", 401)
    return _token(station.police_id, "police")
