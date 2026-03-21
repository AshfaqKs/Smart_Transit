"""
MissingPerson Model — SmartTransit
"""
from extensions import db

class MissingPerson(db.Model):
    __tablename__ = "missing_persons"

    missing_id  = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(150), nullable=False)
    age         = db.Column(db.Integer)
    description = db.Column(db.Text)
    photo       = db.Column(db.String(300))
    police_id   = db.Column(db.Integer, db.ForeignKey("police_stations.police_id"), nullable=True)

    def to_dict(self):
        return {
            "missing_id":  self.missing_id,
            "name":        self.name,
            "age":         self.age,
            "description": self.description,
            "photo":       self.photo,
            "police_id":   self.police_id,
        }
