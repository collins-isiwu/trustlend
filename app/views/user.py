from flask import Blueprint, request, jsonify
from app.schemas.user_schema import user_schema
from app.models.user import User
from app.extensions import db
from app.constants.http_status_codes import Status

auth = Blueprint('user', __name__)

@auth.post('/register')
def register():
    data = request.get_json()
    errors = user_schema.validate(data)

    if errors:
        return jsonify({
            'success': False,
            'status': Status.HTTP_400_BAD_REQUEST,
            'error': errors,
            'message': 'Unable to register user',
        }), Status.HTTP_400_BAD_REQUEST
    
    user = user_schema.load(data)
    db.session.add(user)
    db.session.commit()

    # Serialize the user object
    serialized_user = user_schema.dump(user)

    return jsonify({
        'success': True,
        'status': Status.HTTP_201_CREATED,
        'error': None,
        'message': 'User registered successfully',
        'data': serialized_user
    }), Status.HTTP_201_CREATED