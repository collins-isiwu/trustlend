from app.extensions import db
from datetime import datetime
from enum import Enum

class AmortizationTypeEnum(Enum):
    DAILY = 'DAILY'
    WEEKLY = 'WEEKLY'
    MONTHLY = 'MONTHLY'
    YEARLY = 'YEARLY'

class RequestLoan(db.Model):
    __tablename__ = 'requestloans'

    INTEREST_RATE = 0.05    # constant interest rate of 5%

    id = db.Column(db.Integer, primary_key=True)
    interest_rate = db.Column(db.Float, nullable=False)
    amount = db.Column(db.Numeric(10, 3), nullable=False)
    approval = db.Column(db.Boolean(), default=False)
    date_requested = db.Column(db.DateTime(), default=datetime.now())
    amortization_type = db.Column(db.Enum(AmortizationTypeEnum), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self) -> str:
        return f"Requesting User > {self.approval}"

 
class Loan(db.Model):
    __tablename__ = 'loans'

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Numeric(10, 3), nullable=False)
    paid_off = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime(), default=datetime.now())
    request_loan_id = db.Column(db.Integer, db.ForeignKey('requestloans.id'), nullable=False)

    # Define a relationship to the User model
    user = db.relationship('User', back_populates='loans', lazy=True)
    request_loan = db.relationship('RequestLoan', backref=db.backref('loans', lazy=True))
    
    def __repr__(self) -> str:
        return f"Loan> {self.amount}"

    