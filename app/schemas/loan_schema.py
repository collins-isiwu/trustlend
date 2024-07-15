from marshmallow import validate, fields
from app.models import Loan, RequestLoan, LoanBalance, AmortizationRateEnum
from app.extensions import ma

class RequestLoanSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = RequestLoan
        load_instance = True

    interest_rate = fields.Float(dump_only=True, dump_default=RequestLoan.INTEREST_RATE)
    amount = fields.Decimal(required=True, validate=validate.Range(min=0.01))
    approval = fields.Boolean(dump_only=True)
    date_requested = fields.DateTime(dump_only=True)
    amortization_rate = fields.String(
        required=True, validate=validate.OneOf([e.value for e in AmortizationRateEnum])
    )
    user_id = fields.Integer(required=True, validate=validate.Range(min=1), load_only=True)

request_loan_schema = RequestLoanSchema()


class LoanSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Loan
        load_instance = True

    amount = fields.Decimal(required=True, validate=validate.Range(min=0.01))
    paid_off = fields.Boolean(dump_only=True)
    user_id = fields.Integer(required=True, validate=validate.Range(min=1), load_only=True)
    start_at = fields.DateTime(dump_only=True)
    request_loan_id = fields.Integer(required=True, validate=validate.Range(min=1), load_only=True)

loan_schema = LoanSchema()


class EditRequestLoanSchema(ma.SQLAlchemySchema):
    class Meta:
        model = RequestLoan
        load_instance = True

    approval = fields.Boolean(required=True)

edit_request_loan_schema = EditRequestLoanSchema()


class LoanBalanceSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = LoanBalance
        load_instance = True

    total_loan = fields.Decimal(dump_only=True, places=2)
    total_paid = fields.Decimal(dump_only=True, places=2)
    last_updated = fields.DateTime(dump_only=True)

loan_balance_schema = LoanBalanceSchema()