import pytest
from flask import Flask
from flask.testing import FlaskClient
from flask_jwt_extended import create_access_token
from app import create_app, db
from app.models import User, LoanBalance, Repayment, Loan
from app.environment import TestingEnvironment
from unittest.mock import MagicMock, patch


@pytest.fixture
def app():
    """Create and configure a test app instance."""
    app = create_app(TestingEnvironment)
    app.config['SECRET_KEY'] = 'test_secret_key'  
    app.config['JWT_SECRET_KEY'] = 'test_jwt_secret_key'
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app: Flask) -> FlaskClient:
    return app.test_client()

@pytest.fixture
def headers(app: Flask):
    user = User(
        email='testuser@example.com',
        password='testpass123', 
        full_name='Test User', 
        is_admin=True
    )
    db.session.add(user)
    db.session.commit()

    access_token = create_access_token(identity=user.id)
    return {
        'Authorization': f'Bearer {access_token}',
    }


def test_verify_payment_failure(client: FlaskClient, headers):
    user = User.query.first()
    loan_balance = LoanBalance(total_loan=10000, total_paid=5000, user_id=user.id)
    db.session.add(loan_balance)
    db.session.commit()

    repayment = Repayment(repay_amount=1000.00, user_id=user.id)
    db.session.add(repayment)
    db.session.commit()

    data = {
        "reference": repayment.id
    }


def test_verify_payment_user_not_found(client: FlaskClient, headers):
    db.session.query(User).delete()  # Remove all users

    data = {
        "reference": 12345
    }

    response = client.get('/api/v1/repayment/12345', headers=headers)
    json_data = response.get_json()

    assert response.status_code == 404
    assert json_data['success'] is False
    assert json_data['message'] == 'No user found with the given ID'
