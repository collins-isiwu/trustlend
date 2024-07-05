from app.views import auth, verify, loans

def register_blueprints(app):
    app.register_blueprint(auth, url_prefix='/api/v1/user')
    app.register_blueprint(verify, url_prefix='/api/v1/verification')
    app.register_blueprint(loans, url_prefix='/api/v1/loan')