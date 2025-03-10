from flask import Blueprint, jsonify, request
from app.llm import generate
from app.validate_handler import validate_titles
from app.crud import *
from embed import store_embeddings
# Create a Blueprint
main_bp = Blueprint("main", __name__)

@main_bp.route("/respond", methods=["POST"])
def respond():
    data = request.get_json() 
    query = data['query']
    content_type = data['content_type']
    email = data['email']
    results = generate(query, content_type)
    valid_results = validate_titles(content_type, results)
    user_recommendations = get_user_recommendations(email)
    
    upsert_popular_recommendations(content_type, valid_results)
    return jsonify({"results": valid_results})

@main_bp.route("/add_recommendation", methods=["POST"])
def add_recommendation():
    """
    API endpoint to add or update a user recommendation.
    """
    data = request.get_json()
    
    email = data["email"]
    title = data["title"]
    description = data["description"]
    content_type = data["content_type"]
    comment = data.get("comment")  # Optional
    seen = data.get("seen")  # Optional
    rating = data.get("rating")  # Optional

    upsert_user_recommendation(email, anime_title, content_type, comment, seen, rating)
    
    description_or_comment = comment if comment else description
    store_embeddings([content_type], [title], [description_or_comment])

    return jsonify({"message": "User recommendation added/updated successfully"})
