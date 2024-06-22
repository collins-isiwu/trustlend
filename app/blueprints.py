from flask import Blueprint
from .views.user import user


def register_blueprints(app):
    app.register_blueprint(user, url_prefix='api/v1/user')