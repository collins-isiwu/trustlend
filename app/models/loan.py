from app.extensions import db
from datetime import datetime
from enum import Enum

class AmortizationRateEnum(Enum):
    DAILY = 'DAILY'
    WEEKLY = 'WEEKLY'
    MONTHLY = 'MONTHLY'
    YEARLY = 'YEARLY'

class RequestLoan(db.Model):
    __tablename__ = 'requestloans'

    INTEREST_RATE = 0.05    # constant interest rate of 5%

    id = db.Column(db.Integer, primary_key=True)
    interest_rate = db.Column(db.Float, nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    approval = db.Column(db.Boolean(), default=False)
    date_requested = db.Column(db.DateTime(), default=datetime.now())
    amortization_rate = db.Column(db.Enum(AmortizationRateEnum), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self) -> str:
        return f"Requesting User>> {self.approval}"

 
class Loan(db.Model):
    __tablename__ = 'loans'

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    paid_off = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start_at = db.Column(db.DateTime(), default=datetime.now())
    request_loan_id = db.Column(db.Integer, db.ForeignKey('requestloans.id'), nullable=False)

    # Define a relationship to the User model
    user = db.relationship('User', back_populates='loans', lazy=True)
    request_loan = db.relationship('RequestLoan', backref=db.backref('loans', lazy=True))
    
    def __repr__(self) -> str:
        return f"Loan>> {self.amount}"
    

class LoanBalance(db.Model):
    __tablename__ = 'loan_balance'

    id = db.Column(db.Integer, primary_key=True)
    total_loan = db.Column(db.Numeric(10, 2), default=0.00)
    loan_paid = db.Column(db.Numeric(10, 2), default=0.00)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    last_updated = db.Column(db.DateTime(), default=datetime.now(), onupdate=datetime.now())

    user = db.relationship('User', back_populates='loan_balance', uselist=False)

    def __repr__(self) -> str:
        return f"<LoanBalance id={self.id} user_id={self.user_id} total_loan={self.total_loan} loan_paid={self.loan_paid}>"
