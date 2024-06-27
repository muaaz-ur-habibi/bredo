from flask import Flask

def createApp():
    from .views import views
    #from main.views import id as Id

    app = Flask(__name__)
    app.config["SECRET_KEY"] = "wowsosecret"

    app.register_blueprint(views, url_prefix="/")

    return app