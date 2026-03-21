"""Quick validation script - tests blueprint registration without DB"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from config import Config
from extensions import db, jwt, socketio, bcrypt
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
jwt.init_app(app)
bcrypt.init_app(app)
CORS(app)
socketio.init_app(app, cors_allowed_origins="*")

from routes.auth   import auth_bp
from routes.admin  import admin_bp
from routes.driver import driver_bp
from routes.police import police_bp
from routes.user   import user_bp
from routes.camera import camera_bp

for bp in [auth_bp, admin_bp, driver_bp, police_bp, user_bp, camera_bp]:
    app.register_blueprint(bp)

print("=== ALL ROUTES REGISTERED ===")
for rule in sorted(app.url_map.iter_rules(), key=lambda x: x.rule):
    methods = ",".join(sorted(rule.methods - {"HEAD", "OPTIONS"}))
    print(f"  {methods:25s} {rule.rule}")
print("\nBlueprint registration: OK")
