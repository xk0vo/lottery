from flask import Flask

def create_app():
    app = Flask(__name__)
    from . import auth, lottery
    app.register_blueprint(auth.bp)
    app.register_blueprint(lottery.bp)
    return app
