from app.extensions import db
from datetime import datetime
from .loan import Loan, LoanBalance

class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(300), nullable=False)
    is_active = db.Column(db.Boolean(), default=True)
    is_admin = db.Column(db.Boolean(), default=False)
    active_loan = db.Column(db.Boolean(), default=False)
    phone_number = db.Column(db.String(20), nullable=True)
    date_joined = db.Column(db.DateTime, default=datetime.now())
    
    loans = db.relationship('Loan', back_populates='user')
    loan_balance = db.relationship('LoanBalance', uselist=False, back_populates='user')

    def __repr__(self) -> str:
        return f"User> {self.email}"
    

class TokenBlacklist(db.Model):
    __tablename__ = 'tokenblacklists'

    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.now())

    def __repr__(self) -> str:
        return f'<TokenBlacklist {self.jti}'
    