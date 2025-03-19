from datetime import datetime
from app.extensions import db
from sqlalchemy import func

# ✅ Table 1: User-Specific Recommendations (Composite Primary Key + Unique Constraint)
class UserRecommendation(db.Model):
    __tablename__ = "user_recommendations"

    user_id = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    content_type = db.Column(db.String(50), nullable=False)
    comment = db.Column(db.String(255), nullable=True)
    genres = db.Column(db.String(255), nullable=True)
    seen = db.Column(db.Boolean, default=False)
    rating = db.Column(db.Float, nullable=False)  
    image_url = db.Column(db.String(500), nullable=False)  
    url = db.Column(db.String(500), nullable=False)
    
    __table_args__ = (
        db.PrimaryKeyConstraint("user_id", "title", "content_type", name="user_recommendations_pk"),  # Composite primary key
        db.UniqueConstraint("user_id", "title", "content_type", name="unique_user_recommendation"),  # Explicit unique constraint
        db.CheckConstraint(
            "content_type IN ('anime', 'movie', 'series')",
            name="check_content_type"
        ),
        db.Index(
            'user_recommendation_ci_idx',
            'user_id',
            func.lower(title),
            'content_type',
            unique=True
        )
    )

    def __repr__(self):
        return f"<UserRecommendation {self.user_id} -> {self.title}>"




# ✅ Table 2: Global Popular Recommendations (Composite Primary Key + Unique Constraint)
class PopularRecommendation(db.Model):
    __tablename__ = "popular_recommendations"

    title = db.Column(db.String(255), nullable=False)
    content_type = db.Column(db.String(50), nullable=False)
    
    recommendation_count = db.Column(db.Integer, default=1)
    genres = db.Column(db.String(255), nullable=False)
    last_recommended = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    image_url = db.Column(db.String(500), nullable=False)  
    url = db.Column(db.String(500), nullable=False)
    
    __table_args__ = (
        db.PrimaryKeyConstraint("title", "content_type", name="popular_recommendations_pk"),  # Composite primary key
        db.UniqueConstraint("title", "content_type", name="unique_popular_recommendation"),  # Explicit unique constraint
        db.CheckConstraint(
            "content_type IN ('anime', 'movie', 'series')",
            name="check_content_type"
        ),
    )

    def __repr__(self):
        return f"<PopularRecommendation {self.title} ({self.recommendation_count} recs)>"
