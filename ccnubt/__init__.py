from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import redis

db = SQLAlchemy(use_native_unicode='utf8')
login_manager = LoginManager()
login_manager.login_view = "auth.login"
store = redis.StrictRedis()