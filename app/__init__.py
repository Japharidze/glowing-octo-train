from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Globals
db = SQLAlchemy()

def init_app():
    """Initialize the core app"""
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object('config.Config')

    # Plugins
    db.init_app(app)

    # Run the BOT
    # Here

    with app.app_context():
        from . import routes

        return app