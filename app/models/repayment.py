from app.extensions import db
from .user import User
from .loan import Loan
from datetime import datetime

class Repayment(db.Model):
    """Paystack API Repayment Model"""
    __tablename__ = "repayments"

    id = db.Column(db.Integer, primary_key=True)
    repay_amount = db.Column(db.Numeric(10, 2))
    is_approved = db.Column(db.Boolean, default=False)
    email = db.Column(db.String(255), nullable=False)
    paid_at = db.Column(db.DateTime, default=datetime.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    user = db.relationship('User', backref=db.backref('repayments', lazy=True))
    loan = db.relationship('Loan', back_ref=db.backref('repayments', lazy=True))
    
    class Meta:
        ordering = ['-paid_at']

    def __repr__(self) -> str:
        return f"User>> {self.user.fullname} paid {self.repay_amount} for {self.loan.amount} loan"