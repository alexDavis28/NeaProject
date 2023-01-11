from flask import Flask

app = Flask(__name__)
app.config["SECRET_KEY"] = 'c6eb0afa8fc94a33904d5ac62eee6150'

from app import routes
