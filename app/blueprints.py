from flask import Blueprint
from .views.user import auth


def register_blueprints(app):
    app.register_blueprint(auth, url_prefix='/api/v1/user')