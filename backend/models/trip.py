"""
Trip Model — SmartTransit
"""
from extensions import db
from datetime import datetime

class Trip(db.Model):
    __tablename__ = "trips"

    trip_id         = db.Column(db.Integer, primary_key=True)
    bus_id          = db.Column(db.Integer, db.ForeignKey("buses.bus_id", ondelete="CASCADE"), nullable=False)
    driver_id       = db.Column(db.Integer, db.ForeignKey("bus_drivers.driver_id", ondelete="CASCADE"), nullable=False)
    route_id        = db.Column(db.Integer, db.ForeignKey("routes.route_id", ondelete="CASCADE"), nullable=False)
    scheduled_time  = db.Column(db.DateTime, nullable=False)
    start_time      = db.Column(db.DateTime)
    end_time        = db.Column(db.DateTime)
    status          = db.Column(db.String(50), default="scheduled") # scheduled / ongoing / completed

    # Relationships
    bus    = db.relationship("Bus", backref=db.backref("trips", lazy=True))
    driver = db.relationship("BusDriver", backref=db.backref("trips", lazy=True))
    route  = db.relationship("Route", backref=db.backref("trips", lazy=True))

    def to_dict(self):
        return {
            "trip_id":        self.trip_id,
            "bus_id":         self.bus_id,
            "driver_id":      self.driver_id,
            "route_id":       self.route_id,
            "scheduled_time": self.scheduled_time.isoformat() if self.scheduled_time else None,
            "start_time":     self.start_time.isoformat() if self.start_time else None,
            "end_time":       self.end_time.isoformat() if self.end_time else None,
            "status":         self.status,
            "route_name":     self.route.route_name if self.route else "Unknown"
        }
