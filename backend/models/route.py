"""
Route Model — SmartTransit
"""
from extensions import db

class Route(db.Model):
    __tablename__ = "routes"

    route_id   = db.Column(db.Integer, primary_key=True)
    route_name = db.Column(db.String(150), nullable=False)
    start_point = db.Column(db.String(200), nullable=False)
    end_point   = db.Column(db.String(200), nullable=False)

    buses = db.relationship("Bus", backref="route", lazy=True)

    def to_dict(self):
        return {
            "route_id":    self.route_id,
            "route_name":  self.route_name,
            "start_point": self.start_point,
            "end_point":   self.end_point,
            "stops":       [s.to_dict() for s in self.stops]
        }
