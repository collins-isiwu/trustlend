from datetime import datetime
from flask import jsonify, request, Blueprint
from flask.views import MethodView
from app.models import Loan, RequestLoan, User, LoanBalance
from app.extensions import db
from decimal import Decimal
from utils.admin import admin_required
from app.constants.http_status_codes import Status
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.schemas import loan_schema, request_loan_schema, edit_request_loan_schema, loan_balance_schema

loans = Blueprint('loans', __name__)

class RequestLoanView(MethodView):

    @jwt_required()
    def get(self, request_loan_id):
        """Retrieve Request Loan by ID"""
        request_loan = db.session.get(RequestLoan, request_loan_id)
        if request_loan is None:
            return jsonify({
                'success': False,
                'status': Status.HTTP_404_NOT_FOUND,
                'error': 'Request Loan Not Found!',
                'message': 'No requested loan with the given ID'
            }), Status.HTTP_404_NOT_FOUND
        
        serialized_data = request_loan_schema.dump(request_loan)
        return jsonify({
            'success': True,
            'status': Status.HTTP_200_OK,
            'error': None,
            'message': 'Request Loan retrieved!',
            'data': serialized_data
        }), Status.HTTP_200_OK
    

    @jwt_required()
    def post(self):
        """Create RequestLoan"""
        user_id = get_jwt_identity()
        user = db.session.get(User, user_id)

        if user is None:
            return jsonify({
                'success': False,
                'status': Status.HTTP_404_NOT_FOUND,
                'error': 'User Not Found',
                'message': 'No user found with the given ID',
            }), Status.HTTP_404_NOT_FOUND
        
        # check whether user has a pending loan request
        pending_loan = RequestLoan.query.filter_by(user_id=user_id, approval=False).first()

        if pending_loan:
            return jsonify({
                'success': False,
                'status': Status.HTTP_400_BAD_REQUEST,
                'error': None,
                'message': 'You have a pending loan request'
            }), Status.HTTP_400_BAD_REQUEST
        
        data = request.get_json()
        data['user_id'] = user_id   # Insert the user_id data
        errors = request_loan_schema.validate(data)
        if errors:
            return jsonify({
                'success': False,
                'status': Status.HTTP_400_BAD_REQUEST,
                'errors': errors,
                'message': 'Validation error with request data'
            }), Status.HTTP_400_BAD_REQUEST
        
        # load and save to db
        loan_data = request_loan_schema.load(data)
        loan_data.interest_rate = RequestLoan.INTEREST_RATE
        db.session.add(loan_data)
        db.session.commit()

        # serialize data
        serialized_data = request_loan_schema.dump(loan_data)
        return jsonify({
            'success': True,
            'status': Status.HTTP_201_CREATED,
            'error': None,
            'Message': 'Loan request created!',
            'data': serialized_data
        }), Status.HTTP_201_CREATED
    

    @jwt_required()
    @admin_required
    def patch(self, request_loan_id):
        """Approve User Loan Request and Create Loan. Admin Only"""
        data = request.get_json()

        # Validate the input data
        errors = edit_request_loan_schema.validate(data)
        if errors:
            return jsonify({
                'success': False,
                'status': Status.HTTP_400_BAD_REQUEST,
                'errors': errors,
                'message': 'Validation error with request data'
            }), Status.HTTP_400_BAD_REQUEST
        
        # check wether admin approved the loan request
        if data.get('approval') == False:
            return jsonify({
                'success': False,
                'status': Status.HTTP_400_BAD_REQUEST,
                'error': None,
                'message': 'Loan request not approved!'
            }), Status.HTTP_400_BAD_REQUEST
        
        # Retrieve the loan request from the database
        request_loan = db.session.get(RequestLoan, request_loan_id)
        if request_loan is None:
            return jsonify({
                'success': False,
                'status': Status.HTTP_404_NOT_FOUND,
                'error': 'Request Loan Not Found!',
                'message': 'No Request loan with the given ID'
            }), Status.HTTP_404_NOT_FOUND
    
        # Check if the loan request has already been approved
        if request_loan.approval:
            return jsonify({
                'success': False,
                'status': Status.HTTP_400_BAD_REQUEST,
                'error': 'Loan Request Already Approved',
                'message': 'This loan request has already been approved'
            }), Status.HTTP_400_BAD_REQUEST

        try:
            # Begin transaction
            db.session.begin_nested()

            # approve the loan request
            load_data = edit_request_loan_schema.load(data, instance=request_loan, partial=True)
            db.session.add(load_data)

            # Create the loan and link it to the request
            loan = Loan(
                amount=request_loan.amount,
                user_id=request_loan.user_id,
                start_at=datetime.now(),
                request_loan_id=request_loan.id
            )
            db.session.add(loan)

            # Calculate interest
            interest = request_loan.amount * Decimal(RequestLoan.INTEREST_RATE)

            # Add loan to LoanBalance
            loan_balance = LoanBalance.query.filter_by(user_id=request_loan.user_id).first()
            if loan_balance:
                loan_balance.total_loan += request_loan.amount + interest
                loan_balance.last_updated = datetime.now()
            else:
                loan_balance = LoanBalance(
                    user_id=request_loan.user_id,
                    total_loan=request_loan.amount + interest,
                    total_paid=0.00,
                    last_updated=datetime.now()
                )
                db.session.add(loan_balance)

            # Update User model 
            user = db.session.get(User, request_loan.user_id)
            user.active_loan = True
            db.session.add(user)

            # Commit the transaction
            db.session.commit()

            # Serialize the loan data
            loan_data = loan_schema.dump(loan)
            request_loan_data = request_loan_schema.dump(request_loan)
            return jsonify({
                'success': True,
                'status': Status.HTTP_200_OK,
                'error': None,
                'Message': 'Loan Request Approved',
                'data': {
                    'request_loan': request_loan_data,
                    'loan': loan_data,
                }
            }), Status.HTTP_200_OK
        except Exception as e:
            db.session.rollback()   # Roll back the transaction on error
            return jsonify({
                'success': False,
                'status': Status.HTTP_500_INTERNAL_SERVER_ERROR,
                'error': str(e),
                'message': 'An error occurred while processing the request',
            }), Status.HTTP_500_INTERNAL_SERVER_ERROR
        
        finally:
            db.session.close()  # Close the session to free up resources

# Register the view
request_loan_view = RequestLoanView.as_view('request_loan_view')
loans.add_url_rule('request', view_func=request_loan_view, methods=['POST'])
loans.add_url_rule('request/<int:request_loan_id>', view_func=request_loan_view, methods=['GET', 'PATCH'])



class LoanView(MethodView):

    @jwt_required()
    def get(self, loan_id=None):
        if loan_id:
            user_id = get_jwt_identity()
            user = db.session.get(User, user_id)

            if user is None:
                return jsonify({
                    'success': False,
                    'status': Status.HTTP_404_NOT_FOUND,
                    'error': 'User Not Found',
                    'message': 'No user found with the given ID',
                }), Status.HTTP_404_NOT_FOUND

            # Ensure user accesses only their loan
            loan = Loan.query.filter_by(id=loan_id, user_id=user_id).first()

            if loan is None:
                return jsonify({
                    'success': False,
                    'status': Status.HTTP_404_NOT_FOUND,
                    'error': None,
                    'message': 'Loan not found or access denied.'
                }), Status.HTTP_404_NOT_FOUND
            
            # serialize data
            loan_data = loan_schema.dump(loan)
            return jsonify({
                'success': True,
                'status': Status.HTTP_200_OK,
                'error': None,
                'message': 'Loan Retrieved!',
                'data': loan_data
            })

        # list all the loans of a user with pagination
        else:
            user_id = get_jwt_identity()
            user = db.session.get(User, user_id)

            if user is None:
                return jsonify({
                    'success': False,
                    'status': Status.HTTP_404_NOT_FOUND,
                    'error': 'User Not Found',
                    'message': 'No user found with the given ID',
                }), Status.HTTP_404_NOT_FOUND
            
            # Get pagination parameters
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 5, type=int)

            # Paginate loans
            paginated_loans = Loan.query.filter_by(user_id=user_id).paginate(page=page, per_page=per_page, error_out=False)
            
            if not paginated_loans.items:
                return jsonify({
                    'success': False,
                    'status': Status.HTTP_404_NOT_FOUND,
                    'error': 'No Loans Found',
                    'message': 'No loans found for the given user ID',
                }), Status.HTTP_404_NOT_FOUND

            # Serialize loans
            serialized_data = loan_schema.dump(paginated_loans, many=True)
            return jsonify({
                'success': True,
                'status': Status.HTTP_200_OK,
                'error': None,
                'message': 'Loans retrieved!',
                'data': serialized_data, 
                'page_info': {
                    'total': paginated_loans.total,
                    'pages': paginated_loans.pages,
                    'current_page': paginated_loans.page,
                    'next_page': paginated_loans.next_num,
                    'prev_page': paginated_loans.prev_num,
                    'has_next': paginated_loans.has_next,
                    'has_prev': paginated_loans.has_prev,
                    'per_page': paginated_loans.per_page, 
                }
            }), Status.HTTP_200_OK

loan_view = LoanView.as_view('loan_view')
loans.add_url_rule('', view_func=loan_view, methods=['GET'])
loans.add_url_rule('/<int:loan_id>', view_func=loan_view, methods=['GET'])


class LoanBalanceAPI(MethodView):

    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        user = db.session.get(User, user_id)

        if user is None:
            return jsonify({
                'success': False,
                'status': Status.HTTP_404_NOT_FOUND,
                'error': 'User Not Found',
                'message': 'No user found with the given ID',
            }), Status.HTTP_404_NOT_FOUND    

        loan_balance = LoanBalance.query.filter_by(user_id=user_id).first() 

        # serialize
        loan_data = loan_balance_schema.dump(loan_balance)
        return jsonify({
            'success': True,
            'status': Status.HTTP_200_OK,
            'error': None,
            'message': 'Loan Balance Retrieved!',
            'data': loan_data
        }), Status.HTTP_200_OK
    
loan_balance_view = LoanBalanceAPI.as_view('loan_balance_view')
loans.add_url_rule('/balance', view_func=loan_balance_view, methods=['GET'])
