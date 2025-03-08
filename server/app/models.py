from datetime import datetime
from app.extensions import db

# ✅ Table 1: User-Specific Recommendations (Composite Primary Key)
class UserRecommendation(db.Model):
    __tablename__ = "user_recommendations"

    user_id = db.Column(db.String(255), primary_key=True, nullable=False)
    anime_title = db.Column(db.String(255), primary_key=True, nullable=False)
    content_type = db.Column(db.String(50), primary_key=True, nullable=False)
    comment = db.Column(db.String(255), nullable=True)
    description = db.Column(db.String(1023), nullable=False)
    seen = db.Column(db.Boolean, default=False)
    rating = db.Column(db.Float, nullable=True)  # Nullable if not rated
    
    __table_args__ = (
        db.CheckConstraint(
            "content_type IN ('anime', 'movie', 'series')",
            name="check_content_type"
        ),
    )

    def __repr__(self):
        return f"<UserRecommendation {self.user_id} -> {self.anime_title}>"




# ✅ Table 2: Global Popular Recommendations
class PopularRecommendation(db.Model):
    __tablename__ = "popular_recommendations"

    title = db.Column(db.String(255), primary_key=True)  # Unique title
    content_type = db.Column(db.String(50), nullable=False, primary_key=True)
    recommendation_count = db.Column(db.Integer, default=1)
    last_recommended = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    
    __table_args__ = (
        db.CheckConstraint(
            "content_type IN ('anime', 'movie', 'series')",
            name="check_content_type"
        ),
    )

    def __repr__(self):
        return f"<PopularRecommendation {self.anime_title} ({self.recommendation_count} recs)>"
