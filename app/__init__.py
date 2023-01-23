from flask import Flask
import config
app = Flask(__name__)
app.config["SECRET_KEY"] = config.SECRET_KEY
app.config["DATABASE"] = config.DATABASE_NAME
app.config["DATABASE_HOST"] = config.DATABASE_HOST
app.config["DATABASE_PASSWORD"] = config.DATABASE_PASSWORD
app.config["DATABASE_USERNAME"] = config.DATABASE_USERNAME
from app import routes
