from extensions import db

class RoutePoint(db.Model):
    __tablename__ = "route_points"
    
    stop_id = db.Column(db.Integer, primary_key=True)
    route_id = db.Column(db.Integer, db.ForeignKey("routes.route_id", ondelete="CASCADE"), nullable=False)
    stop_name = db.Column(db.String(100), nullable=False)
    stop_order = db.Column(db.Integer, nullable=False)
    
    # Relationship
    route = db.relationship("Route", backref=db.backref("stops", lazy=True, cascade="all, delete-orphan", order_by="RoutePoint.stop_order"))

    def to_dict(self):
        return {
            "stop_id": self.stop_id,
            "route_id": self.route_id,
            "stop_name": self.stop_name,
            "stop_order": self.stop_order
        }
