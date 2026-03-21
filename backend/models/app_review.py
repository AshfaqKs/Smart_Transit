from extensions import db
from datetime import datetime

class AppReview(db.Model):
    __tablename__ = "app_reviews"
    
    app_review_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    rating = db.Column(db.Integer, nullable=False) # 1-5
    comments = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    user = db.relationship("User", backref=db.backref("app_reviews", lazy=True, cascade="all, delete-orphan"))

    # Constraint to ensure rating is 1-5
    __table_args__ = (
        db.CheckConstraint('rating >= 1 AND rating <= 5', name='check_app_rating_range'),
    )

    def to_dict(self):
        return {
            "app_review_id": self.app_review_id,
            "user_id": self.user_id,
            "user_name": self.user.name if self.user else "Unknown User",
            "rating": self.rating,
            "comments": self.comments,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }
