"""
PoliceStation Model — SmartTransit
"""
from extensions import db

class PoliceStation(db.Model):
    __tablename__ = "police_stations"

    police_id      = db.Column(db.Integer, primary_key=True)
    station_name   = db.Column(db.String(200), nullable=False)
    location       = db.Column(db.String(300))
    contact_number = db.Column(db.String(20))
    email          = db.Column(db.String(200), unique=True, nullable=False)
    password       = db.Column(db.String(255), nullable=False)

    criminals      = db.relationship("Criminal",      backref="police_station", lazy=True)
    missing_persons= db.relationship("MissingPerson", backref="police_station", lazy=True)
    complaints     = db.relationship("Complaint",     backref="police_station", lazy=True)

    def to_dict(self):
        return {
            "police_id":      self.police_id,
            "station_name":   self.station_name,
            "location":       self.location,
            "contact_number": self.contact_number,
            "email":          self.email,
        }
