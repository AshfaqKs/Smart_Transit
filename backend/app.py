"""
SmartTransit — Main Application Entry Point
Flask + SQLAlchemy + JWT + SocketIO + Bcrypt
"""
import os
import sys
import io

# Force UTF-8 stdout on Windows to avoid UnicodeEncodeError with non-ASCII chars
if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Add backend directory to path so imports work cleanly
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS

from config import Config
from extensions import db, jwt, socketio, bcrypt

# ── Factory ───────────────────────────────────────────────────────────────────
def create_app(config_class=Config):
    app = Flask(__name__, static_folder="../web", static_url_path="/web")
    app.config.from_object(config_class)

    # Extensions
    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    socketio.init_app(app, cors_allowed_origins="*",
                      async_mode=Config.SOCKETIO_ASYNC_MODE)

    # Ensure upload folder exists
    os.makedirs(app.config.get("UPLOAD_FOLDER", "uploads"), exist_ok=True)

    # Register Blueprints
    from routes.auth   import auth_bp
    from routes.admin  import admin_bp
    from routes.driver import driver_bp
    from routes.police import police_bp
    from routes.user   import user_bp
    from routes.camera import camera_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(driver_bp)
    app.register_blueprint(police_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(camera_bp)

    # Import models so SQLAlchemy sees them before create_all
    from models import (Admin, User, BusDriver, Route, Bus, PoliceStation,
                        Criminal, MissingPerson, Complaint, Review, CameraDetection)

    with app.app_context():
        try:
            db.create_all()
            _seed_admin(app)
        except Exception as e:
            print(f"\n[WARNING] Database not available: {e}")
            print("   -> Make sure PostgreSQL is running and update backend/.env")
            print("   -> DB_URL: postgresql://postgres:YOUR_PASSWORD@localhost:5432/smarttransit_db\n")

    # ── Serve web frontend files ──────────────────────────────────────────────
    @app.route("/")
    def index():
        return send_from_directory("../web", "index.html")

    @app.route("/uploads/<path:filename>")
    def serve_uploads(filename):
        upload_dir = os.path.abspath(app.config.get("UPLOAD_FOLDER", "uploads"))
        return send_from_directory(upload_dir, filename)

    # ── JWT error handlers ────────────────────────────────────────────────────
    @jwt.unauthorized_loader
    def missing_token_callback(reason):
        return jsonify({"error": "Missing token", "reason": reason}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(reason):
        return jsonify({"error": "Invalid token", "reason": reason}), 422

    # ── Health check ──────────────────────────────────────────────────────────
    @app.route("/api/health")
    def health():
        return jsonify({"status": "ok", "app": "SmartTransit"})

    return app

# ── Seed default admin on first run ──────────────────────────────────────────
def _seed_admin(app):
    from models.admin import Admin
    from extensions import bcrypt, db
    with app.app_context():
        if not Admin.query.first():
            hashed = bcrypt.generate_password_hash("admin123").decode()
            admin = Admin(name="Super Admin", email="admin@smarttransit.com",
                          password=hashed, phone_number="0000000000")
            db.session.add(admin)
            db.session.commit()
            print("[SEED] Default admin created → admin@smarttransit.com / admin123")

# ── Entry Point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = create_app()
    print("\n[SmartTransit] Registered Routes:")
    for rule in sorted(app.url_map.iter_rules(), key=lambda x: x.rule):
        methods = ",".join(sorted(rule.methods - {"HEAD", "OPTIONS"}))
        print(f"  {methods:20s}  {rule.rule}")
    print("\n[SmartTransit] Running at http://127.0.0.1:5000\n")
    socketio.run(app, host="0.0.0.0", port=5000, debug=True, use_reloader=True)
