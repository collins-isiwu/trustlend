from flask import Blueprint, request, jsonify
from app.schemas.user_schema import user_register_schema, user_login_schema
from app.models.user import User
from app.extensions import db
from app.constants.http_status_codes import Status
from werkzeug.security import check_password_hash
from flask_jwt_extended import get_jwt_identity, jwt_required, create_access_token, create_refresh_token


auth = Blueprint('user', __name__)

@auth.post('/register')
def register():
    data = request.get_json()
    errors = user_register_schema.validate(data)

    if errors:
        return jsonify({
            'success': False,
            'status': Status.HTTP_409_CONFLICT,
            'error': errors,
            'message': 'Unable to register user',
        }), Status.HTTP_409_CONFLICT
    
    user = user_register_schema.load(data)
    db.session.add(user)
    db.session.commit()

    # Serialize the user object
    serialized_user = user_register_schema.dump(user)

    return jsonify({
        'success': True,
        'status': Status.HTTP_201_CREATED,
        'error': None,
        'message': 'User registered successfully',
        'data': serialized_user
    }), Status.HTTP_201_CREATED


@auth.post('/sign-in')
def signin():
    data = request.get_json()
    errors = user_login_schema.validate(data)

    if errors:
        return jsonify({
            'success': False,
            'status': Status.HTTP_400_BAD_REQUEST,
            'error': errors,
            'message': 'User input error',
        }), Status.HTTP_400_BAD_REQUEST
    
    email = data.get('email')
    password = data.get('password')
    
    user = User.query.filter_by(email=email).first()

    if user is None:
        return jsonify({
            'success': False,
            'status': Status.HTTP_401_UNAUTHORIZED,
            'error': 'Email Address Not Found!',
            'message': 'Email Address Not Found!',
        }), Status.HTTP_401_UNAUTHORIZED
    
    if check_password_hash(user.password, password):
        refresh = create_refresh_token(identity=user.id)
        access = create_access_token(identity=user.id)

        return jsonify({
            'success': True,
            'status': Status.HTTP_200_OK,
            'error': None,
            'message': 'Signin Successful',
            'data': {
                'refresh': refresh,
                'access': access
            }
        })
    else:
        return jsonify({
            'success': False,
            'status': Status.HTTP_401_UNAUTHORIZED,
            'error': 'Incorrect Password',
            'message': 'Incorrect Password',
        }), Status.HTTP_401_UNAUTHORIZED
    

@auth.post('/token/refresh')
@jwt_required(refresh=True)
def refresh_users_token():
    identity = get_jwt_identity()
    access = create_access_token(identity=identity)

    return jsonify({
        'success': True,
        'status': Status.HTTP_202_ACCEPTED,
        'error': None,
        'message': 'Access Token refreshed successfully',
        'data': {
            'access': access
        }
    }), Status.HTTP_202_ACCEPTED