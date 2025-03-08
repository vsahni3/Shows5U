from datetime import datetime
from sqlalchemy import insert, select, delete
from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app.models import PopularRecommendation, UserRecommendation

def upsert_popular_recommendations(content_type: str, entries: list):
    """
    Inserts or updates popular recommendations based on the given content type and entries.

    :param content_type: The type of content ('anime', 'movie', 'series').
    :param entries: List of titles to insert or update.
    """
    current_time = datetime.utcnow()
    try:
        for entry in entries:
            title = entry['title']
            stmt = insert(PopularRecommendation).values(
                title=title,
                content_type=content_type,
                recommendation_count=1,
                last_recommended=current_time
            ).on_conflict_do_update(
                index_elements=['title', 'content_type'],
                set_=dict(
                    recommendation_count=PopularRecommendation.recommendation_count + 1,
                    last_recommended=current_time
                )
            )
            db.session.execute(stmt)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise

def get_top_n_popular_titles(n: int):
    """
    Retrieves the top N most popular titles based on recommendation count.

    :param n: Number of top titles to retrieve.
    :return: List of PopularRecommendation objects.
    """
    stmt = select(PopularRecommendation).order_by(
        PopularRecommendation.recommendation_count.desc()
    ).limit(n)
    return db.session.scalars(stmt).all()

def delete_old_recommendations(date_threshold: datetime):
    """
    Deletes records where last_recommended is older than the specified date.

    :param date_threshold: Datetime threshold; records older than this will be deleted.
    :return: Number of rows deleted.
    """
    stmt = delete(PopularRecommendation).where(
        PopularRecommendation.last_recommended < date_threshold
    )
    result = db.session.execute(stmt)
    db.session.commit()
    return result.rowcount

def upsert_user_recommendation(user_id: str, anime_title: str, content_type: str, comment: str = None, seen: bool = None, rating: float = None):
    """
    Inserts or updates a user recommendation. Updates comment, seen, and rating if the record exists.

    :param user_id: ID of the user.
    :param anime_title: Title of the anime/movie/series.
    :param content_type: Type of content ('anime', 'movie', 'series').
    :param comment: Optional comment from the user.
    :param seen: Boolean indicating if the user has seen it.
    :param rating: Optional rating given by the user.
    """
    try:
        stmt = insert(UserRecommendation).values(
            user_id=user_id,
            anime_title=anime_title,
            content_type=content_type,
            comment=comment,
            seen=seen,
            rating=rating
        ).on_conflict_do_update(
            index_elements=['user_id', 'anime_title', 'content_type'],
            set_={
                "comment": comment,
                "seen": seen,
                "rating": rating
            }
        )
        db.session.execute(stmt)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise


def get_user_recommendations(user_id: str):
    """
    Retrieves all recommendations for a given user.

    :param user_id: ID of the user.
    :return: List of UserRecommendation objects.
    """
    stmt = select(UserRecommendation).where(UserRecommendation.user_id == user_id)
    return db.session.scalars(stmt).all()