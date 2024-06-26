from flask import Flask
from flask_login import LoginManager
from os import path
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
DB_NAME = 'chatbase.db'

def createApp():
    from .views import views
    #from main.views import id as Id

    app = Flask(__name__)
    app.config["SECRET_KEY"] = "wowsosecret"
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'

    app.register_blueprint(views, url_prefix="/")

    return app

def create_db(app):
    if not path.exists('website/'+DB_NAME):
        db.create_all(app=app)
        print("Database Created")