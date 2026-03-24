"""
Admin Model — SmartTransit
"""
from extensions import db, get_ist_now

class Admin(db.Model):
    __tablename__ = "admins"

    admin_id     = db.Column(db.Integer, primary_key=True)
    name         = db.Column(db.String(120), nullable=False)
    email        = db.Column(db.String(200), unique=True, nullable=False)
    password     = db.Column(db.String(255), nullable=False)  # hashed
    phone_number = db.Column(db.String(20))
    created_at   = db.Column(db.DateTime, default=get_ist_now)

    def to_dict(self):
        return {
            "admin_id":     self.admin_id,
            "name":         self.name,
            "email":        self.email,
            "phone_number": self.phone_number,
            "registration_date": self.created_at.isoformat() if self.created_at else None,
        }
