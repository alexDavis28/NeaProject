from flask import Flask
import config
from flask_wtf.csrf import CSRFProtect
from flask_mysqldb import MySQL

app = Flask(__name__)
csrf = CSRFProtect(app)
db = MySQL(app)
app.config["SECRET_KEY"] = config.SECRET_KEY
app.config["MYSQL_DB"] = config.DATABASE_NAME
app.config["MYSQL_HOST"] = config.DATABASE_HOST
app.config["MYSQL_PASSWORD"] = config.DATABASE_PASSWORD
app.config["MYSQL_USER"] = config.DATABASE_USERNAME
from app import routes
