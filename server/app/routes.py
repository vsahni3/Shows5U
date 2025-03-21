from flask import Blueprint, jsonify, request
from app.llm import generate
from app.validate_handler import validate_titles
from app.crud import *
from app.recommend import give_recommendations, store_embeddings
from time import time 

# Create a Blueprint
main_bp = Blueprint("main", __name__)

@main_bp.route("/respond", methods=["POST"])
def respond():
    first = time()
    data = request.get_json() 
    query = data['query']
    content_type = data['content_type']
    email = data['email']
    results = generate(query, content_type)
    print(results)
    second = time()
    print(second - first)   
    valid_results = validate_titles(content_type, results)
    third = time()
    print(third - second)

    recommended_results = give_recommendations(valid_results, email, content_type)
    fourth = time()
    print(fourth - third)
    upsert_popular_recommendations(content_type, recommended_results)

    return jsonify({"results": recommended_results})

@main_bp.route("/preference", methods=["POST"])
def add_preference():
    """
    API endpoint to add or update a user recommendation.
    """
    data = request.get_json()

    email = data["email"]
    title = data["title"]
    description = data.get("description")
    content_type = data["content_type"]
    image_url = data["image_url"]
    genres = data.get("genres")
    url = data["url"]
    rating = data.get("rating")
    comment = data.get("comment")  # Optional
    seen = data.get("seen", False)  # Optional
    if not rating:
        delete_user_recommendation(email, title, content_type)
    else:
        upsert_user_recommendation(user_id=email, title=title, genres=genres, content_type=content_type, rating=rating, comment=comment, seen=seen, url=url, image_url=image_url)
        
        # description_or_comment = comment if comment else description
        if description:
            description_or_comment = description
            store_embeddings([content_type], [title], [description_or_comment])

    return jsonify({"message": "User recommendation added/updated/deleted successfully"})

@main_bp.route("/trending", methods=["POST"])
def get_trending():
    """
    API endpoint to add or update a user recommendation.
    """
    data = request.get_json()

    content_type = data["content_type"]

    popular = get_top_n_popular_titles(content_type)
    popular_cleaned = [
    {
        "title": row.title,
        "image_url": row.image_url,
        "url": row.url,
    }
    for row in popular
    ]   

    return jsonify({"results": popular_cleaned})


@main_bp.route("/personal", methods=["POST"])
def get_user_preferences():
    data = request.get_json()
    
    email = data["email"]
    
    preferences = get_user_recommendations(email)
    preferences_cleaned = [
        {
            "title": row.title,
            "rating": row.rating,
            "content_type": row.content_type,
            "comment": row.comment,
            "seen": row.seen,
            "url": row.url,
            "image_url": row.image_url
        }
        for row in preferences
    ]
      

    return jsonify({"results": preferences_cleaned})