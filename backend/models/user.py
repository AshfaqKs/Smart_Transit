"""
User Model — SmartTransit
"""
from extensions import db

class User(db.Model):
    __tablename__ = "users"

    user_id      = db.Column(db.Integer, primary_key=True)
    name         = db.Column(db.String(120), nullable=False)
    email        = db.Column(db.String(200), unique=True, nullable=False)
    password     = db.Column(db.String(255), nullable=False)
    phone_number = db.Column(db.String(20))
    address      = db.Column(db.String(300))

    complaints   = db.relationship("Complaint", backref="user", lazy=True)
    reviews      = db.relationship("Review",    backref="user", lazy=True)

    def to_dict(self):
        return {
            "user_id":      self.user_id,
            "name":         self.name,
            "email":        self.email,
            "phone_number": self.phone_number,
            "address":      self.address,
        }
