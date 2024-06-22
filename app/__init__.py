from flask import Flask
from .environment import DevelopmentEnvironment
from .extensions import db
from .blueprints import register_blueprints


def create_app(config=DevelopmentEnvironment):
    app = Flask(__name__)
    app.config.from_object(config)

    # Initialize extensions
    db.init_app(app)

    # register blueprints
    register_blueprints(app)

    return app