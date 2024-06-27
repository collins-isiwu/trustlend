import pytest
from flask import Flask
from flask.testing import FlaskClient
from app import create_app, db
from app.models.user import User
from app.constants.http_status_codes import Status
from app.environment import TestingEnvironment
from werkzeug.security import check_password_hash


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
    """A test client for the app"""
    return app.test_client()


class TestUserRegistration:
    def test_register_user(self, client: FlaskClient):
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
        assert response.status_code == 201
        assert response.json['success'] is True
        assert response.json['data']['email'] == 'test@example.com'
        assert response.json['data']['full_name'] == 'Test User'
        assert 'password' not in response.json['data']

        # Check if user is created in the database
        created_user = User.query.filter_by(email='test@example.com').first()
        assert created_user is not None
        assert created_user.full_name == 'Test User'
        assert check_password_hash(created_user.password, test_user_data['password']) is True

    def test_register_user_missing_data(self, client: FlaskClient):
        """Test user registration with missing data."""
        # Missing email field
        invalid_user_data = {
            'full_name': 'Test User',
            'password': 'testpassword'
        }

        response = client.post('/api/v1/user/register', json=invalid_user_data)
        assert response.status_code == 409
        assert 'error' in response.json
        assert 'email' in response.json['error']


class TestUserLogin:
    def test_login_user(self, client: FlaskClient):
        """Test user login endpoint."""
        # First, register a user to test login
        register_data = {
            'full_name': 'Test User',
            'email': 'test@example.com',
            'password': 'testpassword',
            'phone_number': '1234567890'
        }
        client.post('/api/v1/user/register', json=register_data)

        # Define login data
        login_data = {
            'email': 'test@example.com',
            'password': 'testpassword'
        }

        # Send POST request to login endpoint
        response = client.post('/api/v1/user/sign-in', json=login_data)

        # Check response status code and content
        assert response.status_code == 200
        assert response.json['success'] is True
        assert 'access' in response.json['data']
        assert 'refresh' in response.json['data']

    def test_login_user_invalid_password(self, client: FlaskClient):
        """Test login with incorrect password."""
        # First, register a user to test login
        register_data = {
            'full_name': 'Test User',
            'email': 'test@example.com',
            'password': 'testpassword',
            'phone_number': '1234567890'
        }
        client.post('/api/v1/user/register', json=register_data)

        # Define invalid login data
        invalid_login_data = {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }

        # Send POST request to login endpoint
        response = client.post('/api/v1/user/sign-in', json=invalid_login_data)

        # Check response status code and content
        assert response.status_code == 401
        assert response.json['success'] is False
        assert 'error' in response.json
        assert response.json['error'] == 'Incorrect Password'
