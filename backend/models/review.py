"""
Review Model — SmartTransit
"""
from extensions import db
from sqlalchemy import CheckConstraint

class Review(db.Model):
    __tablename__ = "reviews"
    __table_args__ = (
        CheckConstraint("rating >= 1 AND rating <= 5", name="rating_range"),
    )

    review_id = db.Column(db.Integer, primary_key=True)
    user_id   = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    bus_id    = db.Column(db.Integer, db.ForeignKey("buses.bus_id"),  nullable=False)
    rating    = db.Column(db.Integer, nullable=False)
    comments  = db.Column(db.Text)

    def to_dict(self):
        return {
            "review_id": self.review_id,
            "user_id":   self.user_id,
            "bus_id":    self.bus_id,
            "rating":    self.rating,
            "comments":  self.comments,
        }
