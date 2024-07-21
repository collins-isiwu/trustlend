from flask import jsonify, request, Blueprint
from flask.views import MethodView
from app.models import Repayment, User, Loan, LoanBalance
from app.extensions import db
from app.constants import Status
from app.utils import make_payment, verify_payment, update_loan_records
from app.schemas import repayment_schema
from flask_jwt_extended import get_jwt_identity, jwt_required

repayments = Blueprint('repayments', __name__)

class PaystackPaymentAPI(MethodView):

    @jwt_required()
    def post(self):
        """Make RePayment via Paystack API"""

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
        errors = repayment_schema.validate(data)
        if errors:
            return jsonify({
                'success': False,
                'status': Status.HTTP_400_BAD_REQUEST,
                'errors': errors,
                'message': 'Validation error with request data'
            }), Status.HTTP_400_BAD_REQUEST
        
        loan_balance = LoanBalance.query.filter_by(user_id=user_id).first()
        outstanding_balance = loan_balance.total_loan - loan_balance.total_paid 
        if outstanding_balance < 100.00:
            return jsonify({
                'success': False,
                'status': Status.HTTP_400_BAD_REQUEST,
                'error': None,
                'message': 'Your loans are cleared.'
            }), Status.HTTP_400_BAD_REQUEST
        
        repay_amount = data.get('repay_amount') 
        if repay_amount > outstanding_balance:
            return jsonify({
                'success': False,
                'status': Status.HTTP_400_BAD_REQUEST,
                'error': None,
                'message': 'You cannot pay more than you owe.'
            }), Status.HTTP_400_BAD_REQUEST    

        data['user_id'] = user_id
        load_data = repayment_schema.load(data)   
        db.session.add(load_data)
        db.session.commit()     

        repay = repayment_schema.dump(load_data)
        
        # call function
        payment_res = make_payment(user, repay)

        if payment_res.status_code == Status.HTTP_200_OK:

            return jsonify({
                'success': True,
                'status': Status.HTTP_200_OK,
                'error': None,
                'message': "Payment initialized successfully",
                'data': {
                    'checkout_url': payment_res.json(),
                    'repayment': repay
                }              
            }), Status.HTTP_200_OK
        
        db.session.rollback()   # Roll back on payment failure
        return jsonify({
            'success': False,
            'status': payment_res.status_code,
            'error': 'Payment failed!',
            'message': None,             
        }), payment_res.status_code 
        
paystack_payment = PaystackPaymentAPI.as_view('paystack_payment')
repayments.add_url_rule('', view_func=paystack_payment, methods=['POST']) 


class VerifyPaystackPayment(MethodView):
    """GET user verified payment to Paystack API"""

    @jwt_required()
    def get(self, reference):
        """Verify Paystack Payment"""
        user_id = get_jwt_identity()
        user = db.session.get(User, user_id)

        if user is None:
            return jsonify({
                'success': False,
                'status': Status.HTTP_404_NOT_FOUND,
                'error': 'User Not Found',
                'message': 'No user found with the given ID',
            }), Status.HTTP_404_NOT_FOUND
        
        
        payment_status = verify_payment(reference)
            
        if payment_status.status_code == 200:

            data = payment_status.json()

            if data['data']['status'] == 'success':

                # update loan records
                repay = Repayment.query.filter_by(id=reference).first()
                loan_balance = LoanBalance.query.filter_by(user_id=user_id).first()
                loans = Loan.query.filter_by(user_id=user_id, paid_off=False)

                # call function
                update_loan_records(repay, loans, loan_balance)
                return jsonify({
                    "success": True,
                    "status": Status.HTTP_200_OK,
                    "error": None,
                    "message": "Payment Verified!",
                    "data": data.get('data')
                }), Status.HTTP_200_OK
            
            return jsonify({
                'success': False,
                'status': Status.HTTP_402_PAYMENT_REQUIRED,
                'error': None,
                'message': 'Payment is yet to be made.',
                'data': data.get('data')
            }), Status.HTTP_402_PAYMENT_REQUIRED
        
        return jsonify({
            'success': False,
            'status': payment_status.status_code,
            'error': None,
            'message': None,
        }), payment_status.status_code

verify_paystack_payment = VerifyPaystackPayment.as_view('verify_paystack_payment')
repayments.add_url_rule('/<string:reference>', view_func=verify_paystack_payment, methods=['GET'])