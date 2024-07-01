from marshmallow import fields, validate, validates, ValidationError
from app.extensions import ma, db
from app.models import Verification, User

class VerificationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Verification
        load_instance = True
        fields = ['address', 'is_verified', 'date_verified', 'bvn', 'user_id']

    address = fields.String(required=True, validate=validate.Length(max=300))
    bvn = fields.String(required=True, validate=validate.Length(equal=11))
    date_verified = fields.DateTime(dump_only=True)
    is_verified = fields.Boolean(dump_only=True)
    user_id = fields.Integer(required=True, validate=validate.Range(min=1), load_only=True,)

    @validates('user_id')
    def validate_user_id(self, value):
        user = db.session.get(User, value)
        if user is None:
            raise ValidationError('Invalid user_id. User does not exist.')
verification_schema = VerificationSchema()
