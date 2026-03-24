"""
Complaint Model -- SmartTransit
"""
from extensions import db, get_ist_now

class Complaint(db.Model):
    __tablename__ = "complaints"

    complaint_id              = db.Column(db.Integer, primary_key=True)
    user_id                   = db.Column(db.Integer, db.ForeignKey("users.user_id"),             nullable=False)
    bus_id                    = db.Column(db.Integer, db.ForeignKey("buses.bus_id"),              nullable=True)
    police_id                 = db.Column(db.Integer, db.ForeignKey("police_stations.police_id"), nullable=True)
    complaint_type            = db.Column(db.String(100))
    description               = db.Column(db.Text)
    bus_registration          = db.Column(db.String(50))     # reg number entered by passenger
    bus_location_at_complaint = db.Column(db.String(255))    # GPS / reverse-geocoded address at time of complaint
    photo                     = db.Column(db.String(255))    # optional photo attachment filename
    status                    = db.Column(db.String(50), default="pending")
    reply                     = db.Column(db.Text)
    created_at                = db.Column(db.DateTime, default=get_ist_now)

    def to_dict(self):
        return {
            "complaint_id":               self.complaint_id,
            "user_id":                    self.user_id,
            "passenger_name":             self.user.name if self.user else "Unknown",
            "bus_id":                     self.bus_id,
            "bus_registration":           self.bus_registration,
            "bus_location_at_complaint":  self.bus_location_at_complaint,
            "photo":                      self.photo,
            "police_id":                  self.police_id,
            "complaint_type":             self.complaint_type,
            "description":                self.description,
            "status":                     self.status,
            "reply":                      self.reply,
            "created_at":                 self.created_at.isoformat() if self.created_at else None,
        }
