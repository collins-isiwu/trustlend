from app.extensions import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    is_active = db.Column(db.Boolean(), default=True)
    is_admin = db.Column(db.Boolean(), default=False)
    active_loan = db.Column(db.Boolean(), default=False)
    phone_number = db.Column(db.String(20), nullable=True)
    date_joined = db.Column(db.DateTime, default=datetime.now())
    loans = db.relationship('Loan', backref='user', lazy=True)

    def __repr__(self) -> str:
        return f"User> {self.full_name}"