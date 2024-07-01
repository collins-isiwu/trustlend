from flask import jsonify, Blueprint, request
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.constants.http_status_codes import Status
from app.extensions import db
from app.models import User, Verification
from marshmallow import ValidationError
from app.schemas.verification_schema import verification_schema

verify = Blueprint('verify', __name__)

class VerificationView(MethodView):

    @jwt_required()
    def get(self):
        """Get Verification Status"""
        user_id = get_jwt_identity()
        user = db.session.get(User, user_id)
        if user is None:
            return jsonify({
                'success': False,
                'status': Status.HTTP_404_NOT_FOUND,
                'error': 'User Not Found!',
                'message': 'No user found with the given ID',
            }), Status.HTTP_404_NOT_FOUND
        
        verification = Verification.query.filter_by(user_id=user_id).first()

        if verification is None:
            return jsonify({
                'success': False,
                'status': Status.HTTP_404_NOT_FOUND,
                'error': 'Verification Not Found',
                'message': 'Verification status not found.'
            }), Status.HTTP_404_NOT_FOUND

        return jsonify({
            'success': True,
            'status': Status.HTTP_200_OK,
            'error': None,
            'message': 'User is verified!' if verification.is_verified else 'User is not verified!',
        }), Status.HTTP_200_OK
    

    @jwt_required()
    def post(self):
        """Request Verification"""
        user_id = get_jwt_identity()
        user = db.session.get(User, user_id)
        if user is None:
            return jsonify({
                'success': False,
                'status': Status.HTTP_404_NOT_FOUND,
                'error': 'User Not Found!',
                'message': 'No user found with the given ID',
            }), Status.HTTP_404_NOT_FOUND
        
        if Verification.query.filter_by(user_id=user_id).first():
            return jsonify({
                'success': False,
                'status': Status.HTTP_400_BAD_REQUEST,
                'error': 'Bad request',
                'message': 'Verification request already exists.'
            }), Status.HTTP_400_BAD_REQUEST
        
        data = request.get_json()
        data['user_id'] = user_id   # Include user_id in the data

        try:
            verification_data = verification_schema.load(data)
        except ValidationError as err:
            return jsonify({
                'success': False,
                'status': Status.HTTP_409_CONFLICT,
                'error': err.messages,
                'message': 'User Input Error'
            }), Status.HTTP_409_CONFLICT

        db.session.add(verification_data)
        db.session.commit()

        # serialize data
        verification_data = verification_schema.dump(verification_data)

        return jsonify({
            'success': True,
            'status': Status.HTTP_201_CREATED,
            'error': None,
            'message': 'Verification request has been created',
            'data': verification_data
        }), Status.HTTP_201_CREATED
        

# Register the class-based view with the blueprint
verify_view = VerificationView.as_view('verify_view')
verify.add_url_rule('', view_func=verify_view, methods=['GET', 'POST'])


