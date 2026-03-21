"""
Extensions — shared Flask extension instances.
Imported here to avoid circular imports.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from flask_bcrypt import Bcrypt

db       = SQLAlchemy()
jwt      = JWTManager()
socketio = SocketIO()
bcrypt   = Bcrypt()
