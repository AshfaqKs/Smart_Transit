"""
SmartTransit — Configuration Module
Loads environment variables and configures Flask application settings.
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # ── Flask ──────────────────────────────────────────
    SECRET_KEY = os.getenv("SECRET_KEY", "changeme")

    # ── Database ───────────────────────────────────────
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:YOUR_PASSWORD@localhost:5432/smarttransit_db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ── JWT ────────────────────────────────────────────
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-changeme")
    JWT_ACCESS_TOKEN_EXPIRES = False  # tokens don't expire (adjust for production)

    # ── File Uploads ───────────────────────────────────
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB

    # ── SocketIO ───────────────────────────────────────
    SOCKETIO_ASYNC_MODE = "threading"
