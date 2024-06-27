from flask import Flask
from .environment import DevelopmentEnvironment
from .extensions import db, migrate, ma, jwt
from .blueprints import register_blueprints



def create_app(config=DevelopmentEnvironment):
    app = Flask(__name__)
    app.config.from_object(config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)
    jwt.init_app(app)

    # register blueprints
    register_blueprints(app)

    # Create database tables if they don't exist 
    with app.app_context():
        db.create_all()

    return app