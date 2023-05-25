from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# initiate app
app = Flask(__name__)
app.config.from_object(Config)
# initiate database object
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import routes, models