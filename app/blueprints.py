from flask import Blueprint
from .views.user import auth
from .views.verification import verify


def register_blueprints(app):
    app.register_blueprint(auth, url_prefix='/api/v1/user')
    app.register_blueprint(verify, url_prefix='/api/v1/verification')