from datetime import datetime
from sqlalchemy.dialects.postgresql import insert  # PostgreSQL-specific import
from sqlalchemy import select, delete
from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app.models import PopularRecommendation, UserRecommendation

def upsert_popular_recommendations(content_type: str, entries: list):
    """
    Inserts or updates popular recommendations based on the given content type and entries.

    :param content_type: The type of content ('anime', 'movie', 'series').
    :param entries: List of results to insert or update.
    """
    current_time = datetime.utcnow()
    try:
        for entry in entries:
            title = entry["title"]
            stmt = (
                insert(PopularRecommendation)
                .values(
                    title=title,
                    content_type=content_type,
                    recommendation_count=1,
                    last_recommended=current_time,
                )
                .on_conflict_do_update(
                    index_elements=["title", "content_type"],
                    set_={
                        "recommendation_count": PopularRecommendation.recommendation_count + 1,
                        "last_recommended": current_time,
                    },
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

def upsert_user_recommendation(user_id: str, title: str, content_type: str, rating: float, comment: str = None, seen: bool = None):
    """
    Inserts or updates a user recommendation. Updates comment, seen, and rating if the record exists.

    :param user_id: ID of the user.
    :param title: Title of the anime/movie/series.
    :param content_type: Type of content ('anime', 'movie', 'series').
    :param comment: Optional comment from the user.
    :param seen: Boolean indicating if the user has seen it.
    :param rating: Optional rating given by the user.
    """
    try:

        update_values = {"comment": comment, "seen": seen, "rating": rating}
        update_values = {key: value for key, value in update_values.items() if value}

        stmt = (
            insert(UserRecommendation)
            .values(
                user_id=user_id,
                title=title,
                content_type=content_type,
                comment=comment,
                seen=seen,
                rating=rating,
            )
            .on_conflict_do_update(
                index_elements=["user_id", "title", "content_type"],
                set_=update_values,
            )
        )
        db.session.execute(stmt)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise

def get_user_recommendations(user_id: str, cols: tuple = (UserRecommendation,)):
    """
    Retrieves specified columns for all recommendations of a given user.

    :param user_id: ID of the user.
    :param cols: List of columns to retrieve (default is all).
    :return: List of results with specified columns.
    """

    stmt = select(*cols).where(UserRecommendation.user_id == user_id)
    return db.session.scalars(stmt).all()
