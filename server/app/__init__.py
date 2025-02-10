from dotenv import load_dotenv
from flask import Flask
from app.config import Config
from app.extensions import db, migrate
from app.models import UserRecommendation, PopularRecommendation


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize database and migrations
    db.init_app(app)
    migrate.init_app(app, db)


    return app
