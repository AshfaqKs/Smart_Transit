"""
CameraDetection Model — SmartTransit
"""
from extensions import db, get_ist_now

class CameraDetection(db.Model):
    __tablename__ = "camera_detections"

    detection_id        = db.Column(db.Integer, primary_key=True)
    bus_id              = db.Column(db.Integer, db.ForeignKey("buses.bus_id"), nullable=True)
    detected_person_type= db.Column(db.String(50))   # 'criminal' or 'missing_person'
    reference_id        = db.Column(db.Integer)       # criminal_id or missing_id
    detection_time      = db.Column(db.DateTime, default=get_ist_now)
    location            = db.Column(db.String(255))
    alert_status        = db.Column(db.String(50), default="unresolved")  # unresolved/resolved

    def to_dict(self):
        # Dynamically fetch name and bus info for the dict
        from models.criminal import Criminal
        from models.missing_person import MissingPerson
        from models.bus import Bus

        person_name = "Unknown"
        person_photo = None
        if self.detected_person_type == "criminal":
            c = Criminal.query.get(self.reference_id)
            if c:
                person_name = c.name
                person_photo = c.photo
        elif self.detected_person_type == "missing_person":
            mp = MissingPerson.query.get(self.reference_id)
            if mp:
                person_name = mp.name
                person_photo = mp.photo

        bus_reg = "—"
        bus_name = None
        if self.bus_id:
            b = Bus.query.get(self.bus_id)
            if b:
                bus_reg = b.bus_number
                bus_name = b.location_name

        # If location is coordinates, try to get a name
        loc_display = self.location or "—"
        if self.location and "," in self.location:
            from utils.geocoding import get_location_name
            parts = self.location.split(",")
            if len(parts) == 2:
                name = get_location_name(parts[0].strip(), parts[1].strip())
                if name:
                    loc_display = name

        return {
            "detection_id":         self.detection_id,
            "bus_id":               self.bus_id,
            "bus_registration":     bus_reg,
            "detected_person_type": self.detected_person_type,
            "reference_id":         self.reference_id,
            "person_name":          person_name,
            "person_photo":         person_photo,
            "location":             loc_display,
            "detection_time":       self.detection_time.isoformat() if self.detection_time else None,
            "alert_status":         self.alert_status,
        }
