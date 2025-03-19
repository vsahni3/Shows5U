from datetime import datetime
from sqlalchemy.dialects.postgresql import insert  # PostgreSQL-specific import
from sqlalchemy import select, delete, and_
from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app.models import PopularRecommendation, UserRecommendation
from sqlalchemy.orm import load_only
from sqlalchemy import func

def upsert_popular_recommendations(content_type: str, entries: list):
    """
    Bulk inserts or updates popular recommendations for the given content type.

    :param content_type: The type of content ('anime', 'movie', 'series').
    :param entries: List of dictionaries containing keys "title", "image_url", and "url".
    """
    forbidden_genres = {'Hentai'}
    current_time = datetime.utcnow()
    try:

        values = [
            {
                "title": entry["title"],
                "image_url": entry["image_url"],
                "url": entry["url"],
                "content_type": content_type,
                "recommendation_count": 1,
                "genres": ", ".join(entry["genres"]),
                "last_recommended": current_time,
            }
            for entry in entries if entry['genres'] and len(set(entry['genres']).intersection(forbidden_genres)) == 0
        ]
        if not values:
            return

        stmt = (
            insert(PopularRecommendation)
            .values(values)
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


def get_top_n_popular_titles(content_type: str, n: int = 12):
    """
    Retrieves the top N most popular titles based on recommendation count, filtered by content type.

    :param content_type: The type of content to filter by (e.g., "anime", "movie", "series").
    :param n: Number of top titles to retrieve.
    :return: List of PopularRecommendation objects.
    """
    stmt = select(PopularRecommendation).where(
        PopularRecommendation.content_type == content_type
    ).order_by(
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

def upsert_user_recommendation(user_id: str, title: str, content_type: str, rating: float, url: str, image_url: str, genres: str, comment: str = None, seen: bool = None):
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
                genres=genres,
                content_type=content_type,
                comment=comment,
                image_url=image_url,
                url=url,
                seen=seen,
                rating=rating,
            )
            .on_conflict_do_update(
                index_elements=[UserRecommendation.user_id, func.lower(UserRecommendation.title), UserRecommendation.content_type],
                set_=update_values,
            )
        )
        db.session.execute(stmt)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        raise

def delete_user_recommendation(user_id: str, title: str, content_type: str):
    """
    Deletes a user recommendation based on user_id, title (case-insensitive), and content_type.
    """
    stmt = (
        delete(UserRecommendation)
        .where(
            UserRecommendation.user_id == user_id,
            func.lower(UserRecommendation.title) == title.lower(),
            UserRecommendation.content_type == content_type
        )
    )
    result = db.session.execute(stmt)
    db.session.commit()
    return result.rowcount

def get_user_recommendations(user_id: str, content_type: str = None, cols: tuple = tuple()):
    """
    Retrieves full row objects for all recommendations of a given user,
    but only loads the attributes specified in `cols`.

    :param user_id: ID of the user.
    :param cols: Tuple of columns to retrieve (default is all columns of UserRecommendation).
    :return: List of full ORM row objects with only the specified attributes loaded.
    """
    # if we select cols in starts we dont get ORM objects
    conditions = [UserRecommendation.user_id == user_id]
    if content_type:
        conditions.append(UserRecommendation.content_type == content_type)
    stmt = select(UserRecommendation).where(and_(*conditions)
)

    # If specific columns are requested, apply load_only to optimize query
    if cols:
        stmt = stmt.options(load_only(*cols))

    return db.session.execute(stmt).scalars().all()

