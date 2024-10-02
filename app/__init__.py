from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_babel import Babel
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)
babel = Babel(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db, render_as_batch=True)
login_manager = LoginManager()
login_manager.init_app(app)
csrf = CSRFProtect(app)

from app import views, models
from .models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)