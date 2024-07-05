import json
import pytest
from flask import Flask
from flask.testing import FlaskClient
from app import create_app, db
from app.models import User, RequestLoan
from app.environment import TestingEnvironment
from datetime import datetime
from flask_jwt_extended import create_access_token


@pytest.fixture
def app():
    """Create and configure a test app instance."""
    app = create_app(config=TestingEnvironment)
    app.config['SECRET_KEY'] = 'test_secret_key'
    app.config['JWT_SECRET_KEY'] = 'test_jwt_secret_key'
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app: Flask) -> FlaskClient:
    """Create a test client for the app."""
    return app.test_client()

@pytest.fixture
def test_user(app: Flask) -> User:
    """Fixture for creating a test user."""
    user = User(
        email='testuser@example.com',
        password='testpass123', 
        full_name='Test User', 
        is_admin=True
    )
    db.session.add(user)
    db.session.commit()
    return user

def get_jwt_token(user: User) -> str:
    """Helper function to generate JWT token for the user."""
    return create_access_token(identity=user.id)

def test_post_request_loan(client: FlaskClient, test_user: User):
    """Test POST method for creating a request loan."""
    token = get_jwt_token(test_user)
    data = {
        'amount': 2000.837,
        'amortization_type': 'WEEKLY',
        'user_id': test_user.id, 
    }

    response = client.post(
        '/api/v1/loan/request',
        headers={'Authorization': f'Bearer {token}'},
        data=json.dumps(data),
        content_type='application/json'
    )

    print("response>>>>>>>>>>>>>", response.json) 
    assert response.status_code == 201
    response_data = response.json
    assert response_data['success'] == True
    assert response_data['data']['amount'] == str(data['amount'])
    assert response_data['data']['amortization_type'] == 'AmortizationTypeEnum.WEEKLY'

def test_get_request_loan(client: FlaskClient, test_user: User):
    """Test GET method for retrieving a request loan."""
    request_loan = RequestLoan(
        interest_rate=5.0,
        amortization_type='WEEKLY',
        amount=1000.0,
        approval=False,
        date_requested=datetime.now(),
        user_id=test_user.id
    )
    db.session.add(request_loan)
    db.session.commit()
    token = get_jwt_token(test_user)

    response = client.get(
        f'/api/v1/loan/request/{request_loan.id}',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 200
    data = response.json
    assert data['success'] == True
    assert data['data']['id'] == request_loan.id

def test_post_request_loan_with_existing(client: FlaskClient, test_user: User):
    """Test POST method when a user already has a pending or existing loan."""
    # Create a pending loan request for the user
    pending_loan = RequestLoan(
        interest_rate=5.0,
        amortization_type='WEEKLY',
        amount=1000.0,
        approval=False,
        date_requested=datetime.now(),
        user_id=test_user.id
    )
    db.session.add(pending_loan)
    db.session.commit()
    token = get_jwt_token(test_user)

    data = {
        'amount': 2000.0,
        'amortization_type': 'WEEKLY',
        'interest_rate': 5.0
    }

    response = client.post(
        '/api/v1/loan/request',
        headers={'Authorization': f'Bearer {token}'},
        data=json.dumps(data),
        content_type='application/json'
    )
    assert response.status_code == 208
    response_data = response.json
    assert response_data['success'] == False
    assert response_data['message'] == 'You have a pending loan request'

def test_put_request_loan_approve(client: FlaskClient, test_user: User):
    """Test PUT method for approving a loan request."""
    request_loan = RequestLoan(
        interest_rate=5.0,
        amortization_type='WEEKLY',
        amount=1000.0,
        approval=False,
        date_requested=datetime.now(),
        user_id=test_user.id
    )
    db.session.add(request_loan)
    db.session.commit()

    token = get_jwt_token(test_user)

    data = {
        'approval': 'True'  # Should be a string to match form data
    }

    response = client.put(
        f'/api/v1/loan/request/{request_loan.id}',
        headers={'Authorization': f'Bearer {token}'},
        data=json.dumps(data),
        content_type='application/json'
    )
    assert response.status_code == 200
    response_data = response.json
    assert response_data['success'] == True
    assert response_data['data']['request_loan']['approval'] == True
    assert response_data['data']['loan']['amount'] == str(request_loan.amount)  # Decimal as string

def test_put_request_loan_already_approved(client: FlaskClient, test_user: User):
    """Test PUT method for already approved loan request."""
    request_loan = RequestLoan(
        interest_rate=5.0,
        amortization_type='WEEKLY',
        amount=1000.0,
        approval=True,  # Already approved
        date_requested=datetime.now(),
        user_id=test_user.id
    )
    db.session.add(request_loan)
    db.session.commit()

    token = get_jwt_token(test_user)

    data = {
        'approval': 'True'
    }

    response = client.put(
        f'/api/v1/loan/request/{request_loan.id}',
        headers={'Authorization': f'Bearer {token}'},
        data=json.dumps(data),
        content_type='application/json'
    )
    assert response.status_code == 400
    response_data = response.json
    assert response_data['success'] == False
    assert response_data['error'] == 'Loan Request Already Approved'
