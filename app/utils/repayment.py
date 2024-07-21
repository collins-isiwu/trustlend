from app.extensions import db
from decimal import Decimal


def update_loan_records(repay, loans, loan_balance):
    loan_balance.total_paid += Decimal(repay.repay_amount)
    db.session.commit()

    repay.is_approved = True
    db.session.commit()

    outstanding_balance = loan_balance.total_loan - loan_balance.total_paid 
    if outstanding_balance <= 100:
       
        for loan in loans:
            loan.paid_off = True
        db.session.commit()
