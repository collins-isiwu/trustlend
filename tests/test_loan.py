# test_loan_view.py
import pytest
from flask import Flask
from flask.testing import FlaskClient
from flask_jwt_extended import create_access_token, get_jwt_identity
from app import create_app, db
from app.models import User, Loan, RequestLoan
from app.environment import TestingEnvironment
from datetime import datetime


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
    )
    db.session.add(user)
    db.session.commit()
    return user

def get_jwt_token(user: User) -> str:
    """Helper function to generate JWT token for the user."""
    return create_access_token(identity=user.id)


def test_get_loan_by_id(client: FlaskClient, test_user: User):
    # get jwt token
    token = get_jwt_token(test_user)

    # Add a test loan to the database
    user = User.query.first()
    request_loan = RequestLoan(
        interest_rate=5.0,
        amortization_type='WEEKLY',
        amount=1000.0,
        approval=True,
        date_requested=datetime.now(),
        user_id=test_user.id
    )
    db.session.add(request_loan)
    db.session.commit()

    loan = Loan(amount=5000, user_id=user.id, request_loan_id=request_loan.id)
    db.session.add(loan)
    db.session.commit()

    response = client.get(
        f'/api/v1/loan/{loan.id}', 
        headers={'Authorization': f'Bearer {token}'}
    )
    json_data = response.get_json()

    assert response.status_code == 200
    assert json_data['success'] is True
    assert json_data['data']['id'] == loan.id


def test_get_nonexistent_loan(client: FlaskClient, test_user: User):
    # Get JWT Token
    token = get_jwt_token(test_user)

    response = client.get(
        '/api/v1/loan/999', 
        headers={'Authorization': f'Bearer {token}'}
    )
    json_data = response.get_json()

    assert response.status_code == 404
    assert json_data['success'] is False
    assert json_data['message'] == 'Loan with the ID does not exist.'


def test_get_loans_with_pagination(client: FlaskClient, test_user: User):
    # Get JWT Token
    token = get_jwt_token(test_user)

    user = User.query.first()

    request_loan = RequestLoan(
        interest_rate=5.0,
        amortization_type='WEEKLY',
        amount=86600.0,
        approval=True,
        date_requested=datetime.now(),
        user_id=test_user.id
    )
    db.session.add(request_loan)
    db.session.commit()

    # Add multiple loans to test pagination
    for i in range(10):
        loan = Loan(amount=5000 + i * 1000, user_id=user.id, request_loan_id=request_loan.id)
        db.session.add(loan)
    db.session.commit()

    response = client.get(
        '/api/v1/loan?page=1&per_page=5', 
        headers={'Authorization': f'Bearer {token}'}
    )
    json_data = response.get_json()

    assert response.status_code == 200
    assert json_data['success'] is True
    assert len(json_data['data']) == 5
    assert json_data['page_info']['current_page'] == 1
    assert json_data['page_info']['per_page'] == 5


def test_get_loans_no_user(client: FlaskClient):

    # Create a new user and do not create any loans for them
    new_user = User(full_name="nouser", email="nouser@example.com", password='testpassword')
    db.session.add(new_user)
    db.session.commit()

    access_token = create_access_token(identity=new_user.id)
    headers = {'Authorization': f'Bearer {access_token}'}

    response = client.get(
        '/api/v1/loan', 
        headers=headers
    )
    json_data = response.get_json()

    print('data>>>>>>>>>>>>>>>.', json_data)

    assert response.status_code == 404
    assert json_data['success'] is False
    assert json_data['message'] == 'No loans found for the given user ID'


def test_get_loans_no_auth(client: FlaskClient):
    response = client.get('/api/v1/loan')
    assert response.status_code == 401  # Unauthorized
