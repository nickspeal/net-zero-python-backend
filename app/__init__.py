from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)


# Setup the app with the config.py file
app.config.from_object('app.config')

# Setup the database
db = SQLAlchemy(app)

# Import the views after db is setup
from app.views import users, campaigns, resources
app.register_blueprint(users.user_bp)
app.register_blueprint(campaigns.campaign_bp)
app.register_blueprint(resources.resources_bp)

# Setup the user login process
# from flask.ext.login import LoginManager
# from app.models import User

# login_manager = LoginManager()
# login_manager.init_app(app)
# login_manager.login_view = 'userbp.signin'


# @login_manager.user_loader
# def load_user(username):
#     return User.query.filter(User.username == username).first()

# from app import admin
