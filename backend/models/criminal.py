"""
Criminal Model — SmartTransit
"""
from extensions import db

class Criminal(db.Model):
    __tablename__ = "criminals"

    criminal_id = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(150), nullable=False)
    crime_type  = db.Column(db.String(100))
    description = db.Column(db.Text)
    photo       = db.Column(db.String(300))   # file path / URL
    police_id   = db.Column(db.Integer, db.ForeignKey("police_stations.police_id"), nullable=True)

    def to_dict(self):
        return {
            "criminal_id": self.criminal_id,
            "name":        self.name,
            "crime_type":  self.crime_type,
            "description": self.description,
            "photo":       self.photo,
            "police_id":   self.police_id,
        }
