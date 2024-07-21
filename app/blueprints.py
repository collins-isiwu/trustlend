from app.views import auth, verify, loans, repayments
from .swagger import swagger_ui_blueprint, swagger_blueprint, SWAGGER_URL

def register_blueprints(app):
    app.register_blueprint(auth, url_prefix='/api/v1/user')
    app.register_blueprint(verify, url_prefix='/api/v1/verification')
    app.register_blueprint(loans, url_prefix='/api/v1/loan')
    app.register_blueprint(repayments, url_prefix='/api/v1/repayment')
    app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)
    app.register_blueprint(swagger_blueprint)