import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_wtf import CSRFProtect

logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()

app = Flask(__name__)

# ✅ SECRET KEY FIX
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key_123")

app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# ✅ DATABASE URI FIX (LOCAL SQLITE)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "sqlite:///mediconnect.db"
)

app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

app.config["WTF_CSRF_ENABLED"] = True
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
csrf = CSRFProtect(app)

# ✅ INITIALIZE EXTENSIONS
db.init_app(app)
login_manager.init_app(app)

# ✅ LOGIN CONFIG
login_manager.login_view = "home"
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = "info"

# ✅ CREATE DATABASE TABLES
with app.app_context():
    import models
    db.create_all()
