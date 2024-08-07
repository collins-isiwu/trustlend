from flask import Blueprint, request, jsonify
from flask.views import MethodView
from app.schemas import user_register_schema, user_login_schema, user_update_schema, loan_balance_schema
from app.models import User, TokenBlacklist, LoanBalance
from app.extensions import db
from app.constants import Status
from werkzeug.security import check_password_hash
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required, create_access_token, create_refresh_token

auth = Blueprint('auth', __name__)

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

    # Create LoanBalance
    loan_balance = LoanBalance.query.filter_by(user_id=user.id).first()
    if loan_balance is None:
        loan_balance = LoanBalance(user_id=user.id)
        db.session.add(loan_balance)
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
        'status': Status.HTTP_200_OK,
        'error': None,
        'message': 'Access Token refreshed successfully',
        'data': {
            'access': access
        }
    }), Status.HTTP_200_OK


class UserView(MethodView):
    @jwt_required()
    def get(self):
        """Get user details"""
        user_id = get_jwt_identity()
        user = db.session.get(User, user_id)
        if user is None:
            return jsonify({
                'success': False,
                'status': Status.HTTP_404_NOT_FOUND,
                'error': 'User Not Found',
                'message': 'No user found with the given ID',
            }), Status.HTTP_404_NOT_FOUND
        
        # Query for loan balance
        loan_balance = LoanBalance.query.filter_by(user_id=user_id).first()

        user_data = user_register_schema.dump(user) 
        loan_data = loan_balance_schema.dump(loan_balance)
        return jsonify({
            'success': True,
            'status': Status.HTTP_200_OK,
            'error': None,
            'message': 'User fetched successfully',
            'data': {
                'user': user_data,
                'loan': loan_data
            }
        }), Status.HTTP_200_OK
    
    @jwt_required()
    def put(self):
        """Update user details"""
        user_id = get_jwt_identity()
        user = db.session.get(User, user_id)
        if user is None:
            return jsonify({
                'success': False,
                'status': Status.HTTP_404_NOT_FOUND,
                'error': 'User Not Found',
                'message': 'No user found with the given ID',
            }), Status.HTTP_404_NOT_FOUND
        
        data = request.get_json()
        errors = user_update_schema.validate(data)
        if errors:
            return jsonify({
                'success': False,
                'status': Status.HTTP_400_BAD_REQUEST,
                'error': errors,
                'message': 'Validation errors occurred'
            }), Status.HTTP_400_BAD_REQUEST

        user = user_update_schema.load(data, instance=user, partial=True)
        db.session.commit()

        updated_user_data = user_update_schema.dump(user)
        return jsonify({
            'success': True,
            'status': Status.HTTP_200_OK,
            'error': None,
            'message': 'User updated successfully',
            'data': updated_user_data
        }), Status.HTTP_200_OK

# Register the class-based view with the Blueprint
user_view = UserView.as_view('user_view')
auth.add_url_rule('/detail', view_func=user_view, methods=['GET', 'PUT'])


class LogoutView(MethodView):

    @jwt_required()
    def post(self): 
        """Logout user and invalidate the token"""

        # Get the unique identifier for the JWT
        jti = get_jwt()['jti']  
        token = TokenBlacklist(jti=jti)
        db.session.add(token)
        db.session.commit()

        return jsonify({
            'success': True,
            'Status': Status.HTTP_200_OK,
            'error': None,
            'message': 'Token has been revoked and user logged out.'
        }), Status.HTTP_200_OK
    
# Register the class-based view with the Blueprint
logout_view = LogoutView.as_view('logout_view')
auth.add_url_rule('/sign-out', view_func=logout_view, methods=['POST'])