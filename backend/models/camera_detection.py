"""
CameraDetection Model — SmartTransit
"""
from extensions import db
from datetime import datetime

class CameraDetection(db.Model):
    __tablename__ = "camera_detections"

    detection_id        = db.Column(db.Integer, primary_key=True)
    bus_id              = db.Column(db.Integer, db.ForeignKey("buses.bus_id"), nullable=True)
    detected_person_type= db.Column(db.String(50))   # 'criminal' or 'missing_person'
    reference_id        = db.Column(db.Integer)       # criminal_id or missing_id
    detection_time      = db.Column(db.DateTime, default=datetime.utcnow)
    alert_status        = db.Column(db.String(50), default="unresolved")  # unresolved/resolved

    def to_dict(self):
        return {
            "detection_id":         self.detection_id,
            "bus_id":               self.bus_id,
            "detected_person_type": self.detected_person_type,
            "reference_id":         self.reference_id,
            "detection_time":       self.detection_time.isoformat() if self.detection_time else None,
            "alert_status":         self.alert_status,
        }
