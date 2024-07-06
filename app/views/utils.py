from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from app.extensions import db
from app.models import User, TokenBlacklist
from app.constants.http_status_codes import Status

def admin_required(fn):
    @wraps(fn)
    def decorated_function(*args, **kwargs):
        # Get the identity of the current user
        current_user_id = get_jwt_identity()

        # Fetch user from the database
        user = db.session.get(User, current_user_id)

        if user is None:
            return jsonify({
                'success': False,
                'status': Status.HTTP_401_UNAUTHORIZED,
                'error': None,
                'message': 'User not found. Please log in again.'
            }), Status.HTTP_401_UNAUTHORIZED
        
        if not user.is_admin:
            return jsonify({
                'success': False,
                'status': Status.HTTP_403_FORBIDDEN,
                'error': None,
                'message': 'Admin access required.'
            }), Status.HTTP_403_FORBIDDEN
        
        return fn(*args, **kwargs)
    
    return decorated_function


def is_token_blacklisted(jti):
    result = db.session.query(TokenBlacklist.id).filter_by(jti=jti).scalar() is not None
    print('result>>>>>>>>>>>', result)
    return result