from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy(engine_options={
    "pool_pre_ping": True,  # Double-check that connections are valid
    "pool_recycle": 1800
})
migrate = Migrate()
