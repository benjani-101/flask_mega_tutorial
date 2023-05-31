from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

# initiate app
app = Flask(__name__)
app.config.from_object(Config)
# initiate database object
db = SQLAlchemy(app)
# initiate migration object that controls updates to database
migrate = Migrate(app, db)
# initiate LoginManager
login = LoginManager(app)
login.login_view = 'login'

from app import routes, models