from app.models.user import User
from marshmallow import fields, validate, validates, ValidationError, pre_load
from app.extensions import ma
from werkzeug.security import generate_password_hash

class UserSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User
        load_instance = True

    email = fields.Email(required=True)
    full_name = fields.String(required=True, validate=validate.Length(min=3, max=120))
    password = fields.String(required=True, load_only=True)
    phone_number = fields.String(required=False)

    @pre_load
    def hash_password(self, data, **kwargs):
        """Hash the password before saving to the database."""
        if 'password' in data:
            data['password'] = generate_password_hash(data['password'])
            return data

    @validates('email')
    def validate_email_unique(self, value):
        """Ensure email is unique."""
        existing_user = User.query.filter_by(email=value).first()
        if existing_user:
            raise ValidationError('Email already exists.')

user_schema = UserSchema()