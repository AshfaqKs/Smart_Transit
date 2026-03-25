"""
BusDriver Model — SmartTransit
"""
from extensions import db

class BusDriver(db.Model):
    __tablename__ = "bus_drivers"

    driver_id       = db.Column(db.Integer, primary_key=True)
    name            = db.Column(db.String(120), nullable=False)
    email           = db.Column(db.String(200), unique=True, nullable=False)
    password        = db.Column(db.String(255), nullable=False)
    phone_number    = db.Column(db.String(20))
    license_number  = db.Column(db.String(50), unique=True, nullable=False)
    approval_status = db.Column(db.Boolean, default=False)

    buses = db.relationship("Bus", backref="driver", lazy=True)

    def to_dict(self):
        return {
            "driver_id":       self.driver_id,
            "name":            self.name,
            "email":           self.email,
            "phone_number":    self.phone_number,
            "license_number":  self.license_number,
            "approval_status": self.approval_status,
        }
