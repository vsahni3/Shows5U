from flask import Blueprint, jsonify, request
from app.llm import generate
from app.validate_handler import validate_titles
# Create a Blueprint
main_bp = Blueprint("main", __name__)

@main_bp.route("/respond", methods=["POST"])
def respond():
    data = request.get_json() 
    query = data['query']
    content_type = data['content_type']
    results = generate(query, content_type)
    valid_results = validate_titles(content_type, results)
    print(valid_results)
    return jsonify({"results": valid_results})

