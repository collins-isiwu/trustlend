from flask import Flask
from .environment import DevelopmentEnvironment
from .extensions import db, migrate, ma, jwt
from .blueprints import register_blueprints
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

def create_app(config=DevelopmentEnvironment):
    app = Flask(__name__)
    app.config.from_object(config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)
    jwt.init_app(app)

    # Initialize Flask-Admin
    admin = Admin(app, name='Trustlend Admin Panel', template_mode='bootstrap4')

    # Add model views
    from app.models import User, Loan  # Import your models

    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(Loan, db.session))

    # register blueprints
    register_blueprints(app)

    # Create database tables if they don't exist 
    with app.app_context():
        db.create_all()

    return app