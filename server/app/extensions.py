from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask import request

def get_email_or_ip():
    try:
        return request.get_json()['email']
    except Exception:
        return request.remote_addr
    
db = SQLAlchemy(engine_options={
    "pool_pre_ping": True,  # Double-check that connections are valid
    "pool_recycle": 1800
})
migrate = Migrate()
limiter = Limiter(
    key_func=get_email_or_ip,
    default_limits=[]
)