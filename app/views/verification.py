from flask import jsonify, Blueprint, request
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.constants import Status
from app.extensions import db
from app.models import User, Verification
from marshmallow import ValidationError
from utils import admin_required
from app.schemas import verification_schema

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
    

    @jwt_required()
    @admin_required
    def patch(self, user_id):
        """Verify Users. Admins only"""
        data = request.get_json()

        user = db.session.get(User, user_id)
        if user is None:
            return jsonify({
                'success': False,
                'status': Status.HTTP_404_NOT_FOUND,
                'error': None,
                'message': 'User intended to verify not found.',
            }), Status.HTTP_404_NOT_FOUND
        
        verification = Verification.query.filter_by(user_id=user_id).first()
        if not verification:
            return jsonify({
                'success': False,
                'status': Status.HTTP_404_NOT_FOUND,
                'error': None,
                'message': 'User has not requested for verification.'
            }), Status.HTTP_404_NOT_FOUND
        
        if data.get('is_verified') == False:
            return jsonify({
                'success': False,
                'status': Status.HTTP_400_BAD_REQUEST,
                'error': None,
                'message': 'Verification not approved!'
            }), Status.HTTP_400_BAD_REQUEST
        
        # check whether user is already verified
        if verification.is_verified:
            return jsonify({
                'success': False,
                'status': Status.HTTP_208_ALREADY_REPORTED,
                'error': None,
                'message': 'User already approved!'
            }), Status.HTTP_208_ALREADY_REPORTED
        
        # Approve verification
        verification.is_verified = data.get('is_verified')
        db.session.commit()

        # serialize verification data
        serialized_data = verification_schema.dump(verification)
        return jsonify({
            'success': True,
            'status': Status.HTTP_200_OK,
            'error': None,
            'Message': 'Verification Complete!',
            'data': serialized_data
        }), Status.HTTP_200_OK
        

# Register the class-based view with the blueprint
verify_view = VerificationView.as_view('verify_view')
verify.add_url_rule('', view_func=verify_view, methods=['GET', 'POST'])
verify.add_url_rule('/<int:user_id>', view_func=verify_view, methods=['PATCH'])


