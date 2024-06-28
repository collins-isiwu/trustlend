from app.models.user import User
from marshmallow import fields, validate, validates, ValidationError, pre_load
from app.extensions import ma
from werkzeug.security import generate_password_hash

class UserRegisterSchema(ma.SQLAlchemySchema):
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
        password = data.get('password')
        # Check if password exists and have been hashed before
        if password and not password.startswith(('scrypt:')):
            data['password'] = generate_password_hash(password)
        return data

    @validates('email')
    def validate_email_unique(self, value):
        """Ensure email is unique."""
        existing_user = User.query.filter_by(email=value).first()
        if existing_user:
            raise ValidationError('Email already exists.')
        
    def update(self):
        pass

user_register_schema = UserRegisterSchema()


class UserLoginSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User

    email = fields.Email(required=True)
    password = fields.String(required=True, load_only=True)

user_login_schema = UserLoginSchema()



class UserUpdateSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User
        load_instance = True

    email = fields.Email(required=False)
    full_name = fields.String(required=False, validate=validate.Length(min=3, max=120))
    phone_number = fields.String(required=False)

    @validates('email')
    def validate_email_unique(self, value):
        """Ensure email is unique for updates if email is provided."""
        if value:
            existing_user = User.query.filter_by(email=value).first()
            if existing_user:
                raise ValidationError('Email already exists.')

user_update_schema = UserUpdateSchema()
