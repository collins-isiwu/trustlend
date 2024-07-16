from flask import Flask
from .extensions import db, migrate, ma, jwt
from .blueprints import register_blueprints
from flask_admin import Admin
from utils import is_token_blacklisted
from flask_admin.contrib.sqla import ModelView
from app.models import User, Verification, Loan, RequestLoan, TokenBlacklist, LoanBalance

def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)
    jwt.init_app(app)

    # Ensure that the JWT configuration checks for blacklisted tokens
    @jwt.token_in_blocklist_loader
    def check_if_token_in_blacklist(jwt_header, jwt_payload):
        jti = jwt_payload['jti']
        return is_token_blacklisted(jti)

    # Initialize Flask-Admin
    admin = Admin(app, name='Trustlend Admin Panel', template_mode='bootstrap4')

    # Add model views to admin
    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(Verification, db.session))
    admin.add_view(ModelView(RequestLoan, db.session))
    admin.add_view(ModelView(Loan, db.session))
    admin.add_view(ModelView(TokenBlacklist, db.session))
    admin.add_view(ModelView(LoanBalance, db.session))


    # register blueprints
    register_blueprints(app)

    # Create database tables if they don't exist 
    with app.app_context():
        db.create_all()

    return app