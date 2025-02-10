from datetime import datetime
from app.extensions import db

# ✅ Table 1: User-Specific Recommendations (Composite Primary Key)
class UserRecommendation(db.Model):
    __tablename__ = "user_recommendations"

    user_id = db.Column(db.Integer, primary_key=True, nullable=False)
    anime_title = db.Column(db.String(255), primary_key=True, nullable=False)
    comment = db.Column(db.String(255), nullable=True)
    seen = db.Column(db.Boolean, default=False)
    rating = db.Column(db.Float, nullable=True)  # Nullable if not rated

    def __repr__(self):
        return f"<UserRecommendation {self.user_id} -> {self.anime_title}>"


# ✅ Table 2: Global Popular Recommendations
class PopularRecommendation(db.Model):
    __tablename__ = "popular_recommendations"

    anime_title = db.Column(db.String(255), primary_key=True)  # Unique title
    recommendation_count = db.Column(db.Integer, default=1)
    last_recommended = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<PopularRecommendation {self.anime_title} ({self.recommendation_count} recs)>"
