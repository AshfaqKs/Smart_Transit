"""
Complaint Model — SmartTransit
"""
from extensions import db
from datetime import datetime

class Complaint(db.Model):
    __tablename__ = "complaints"

    complaint_id   = db.Column(db.Integer, primary_key=True)
    user_id        = db.Column(db.Integer, db.ForeignKey("users.user_id"),             nullable=False)
    bus_id         = db.Column(db.Integer, db.ForeignKey("buses.bus_id"),              nullable=True)
    police_id      = db.Column(db.Integer, db.ForeignKey("police_stations.police_id"), nullable=True)
    complaint_type = db.Column(db.String(100))
    description    = db.Column(db.Text)
    location_coords= db.Column(db.String(100))
    location_name  = db.Column(db.String(300))
    photo          = db.Column(db.String(300))
    other_details  = db.Column(db.Text)
    status         = db.Column(db.String(50), default="pending")  # pending / resolved / rejected
    reply          = db.Column(db.Text)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "complaint_id":   self.complaint_id,
            "user_id":        self.user_id,
            "bus_id":         self.bus_id,
            "police_id":      self.police_id,
            "complaint_type": self.complaint_type,
            "description":    self.description,
            "location_coords": self.location_coords,
            "location_name":  self.location_name,
            "photo":          self.photo,
            "other_details":  self.other_details,
            "status":         self.status,
            "reply":          self.reply,
            "created_at":     self.created_at.isoformat() if self.created_at else None,
        }
