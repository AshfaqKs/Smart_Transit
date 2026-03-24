"""
Extensions — shared Flask extension instances.
Imported here to avoid circular imports.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from flask_bcrypt import Bcrypt

from datetime import datetime, timedelta, timezone

db       = SQLAlchemy()
jwt      = JWTManager()
socketio = SocketIO()
bcrypt   = Bcrypt()

def get_ist_now():
    """Returns current time in India Standard Time (UTC+5:30) as a naive datetime"""
    return datetime.now(timezone(timedelta(hours=5, minutes=30))).replace(tzinfo=None)
