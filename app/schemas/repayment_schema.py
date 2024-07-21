from marshmallow import validate, fields
from app.models import Repayment
from app.extensions import ma

class RepaymentSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Repayment
        load_instance = True
        
    id = fields.Integer(dump_only=True)
    repay_amount = fields.Decimal(required=True, places=2, validate=validate.Range(min=0.01))
    user_id = fields.Integer(validate=validate.Range(min=1), load_only=True)

repayment_schema = RepaymentSchema()