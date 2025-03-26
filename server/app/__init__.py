from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from app.config import Config
from app.extensions import db, migrate, limiter
from app.routes import main_bp


def create_app():
    app = Flask(__name__)
    limiter.init_app(app)
    CORS(app, support_credentials=True, resources={r"/*": {"origins": "*"}})
    app.config.from_object(Config)
    app.register_blueprint(main_bp)
    # Initialize database and migrations
    db.init_app(app)
    migrate.init_app(app, db)
    
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()



    return app




