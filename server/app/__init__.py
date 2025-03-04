from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from app.config import Config
from app.extensions import db, migrate
from app.models import UserRecommendation, PopularRecommendation
from app.routes import main_bp

def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "*"}})
    app.config.from_object(Config)
    app.register_blueprint(main_bp)
    # # Initialize database and migrations
    # db.init_app(app)
    # migrate.init_app(app, db)


    return app




