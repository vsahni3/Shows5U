import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables

class Config:
    SECRET_KEY = os.environ["SECRET_KEY"]
    SQLALCHEMY_DATABASE_URI = os.environ["DATABASE_URL"]
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 10,        # Max connections in the pool
        "max_overflow": 20,     # Allow extra connections if needed
        "pool_timeout": 30,     # Wait time before failing due to connection unavailability
        "pool_recycle": 1800,   # Close connections older than 30 minutes
        "pool_pre_ping": True   # Check connection health before using
    }
