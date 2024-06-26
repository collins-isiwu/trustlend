import pytest
from flask import Flask
from flask.testing import FlaskClient
from app import create_app, db
from app.models.user import User
from app.constants.http_status_codes import Status
from app.environment import TestingEnvironment


@pytest.fixture
def app():
    """Create and configure a test app instance."""
    app = create_app(config=TestingEnvironment)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app: Flask) -> FlaskClient:
    """A test client for the app"""
    return app.test_client()

def test_register_user(client: FlaskClient):
    """Test user registration endpoint"""
    # Define test data
    test_user_data = {
        'full_name': 'Test User',
        'email': 'test@example.com',
        'password': 'testpassword',
        'phone_number': '1234567890'
    }

    # Send POST request to register endpoint
    response = client.post('/api/v1/user/register', json=test_user_data)

    # Check response status code and content
    assert response.status_code == Status.HTTP_201_CREATED
    assert response.json['success'] is True
    assert response.json['data']['email'] == 'test@example.com'
    assert response.json['data']['full_name'] == 'Test User'
    assert 'password' not in response.json['data']

    # Check if user is created in the database
    created_user = User.query.filter_by(email='test@example.com').first()
    assert created_user is not None
    assert created_user.full_name == 'Test User'


def test_register_user_missing_data(client: FlaskClient):
    """Test user registration with missing data."""
    # Missing email field
    invalid_user_data = {
        'full_name': 'Test User',
        'password': 'testpassword'
    }

    response = client.post('/api/v1/user/register', json=invalid_user_data)
    assert response.status_code == Status.HTTP_400_BAD_REQUEST
    assert 'error' in response.json
    assert 'email' in response.json['error']

