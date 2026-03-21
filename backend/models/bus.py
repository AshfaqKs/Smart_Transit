"""
Bus Model — SmartTransit
"""
from extensions import db

class Bus(db.Model):
    __tablename__ = "buses"

    bus_id           = db.Column(db.Integer, primary_key=True)
    bus_number       = db.Column(db.String(30), unique=True, nullable=False)
    route_id         = db.Column(db.Integer, db.ForeignKey("routes.route_id"), nullable=True)
    driver_id        = db.Column(db.Integer, db.ForeignKey("bus_drivers.driver_id"), nullable=True)
    current_location = db.Column(db.String(300))
    location_name    = db.Column(db.String(500))
    status           = db.Column(db.String(50), default="active")  # active / inactive

    complaints  = db.relationship("Complaint", backref="bus", lazy=True)
    reviews     = db.relationship("Review",    backref="bus", lazy=True)
    detections  = db.relationship("CameraDetection", backref="bus", lazy=True)

    def to_dict(self):
        return {
            "bus_id":           self.bus_id,
            "bus_number":       self.bus_number,
            "route_id":         self.route_id,
            "driver_id":        self.driver_id,
            "current_location": self.current_location,
            "location_name":    self.location_name,
            "status":           self.status,
        }
