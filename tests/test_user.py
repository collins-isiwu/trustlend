import pytest
from flask import Flask
from flask.testing import FlaskClient
from app import create_app, db
from app.models.user import User
from app.environment import TestingEnvironment
from werkzeug.security import check_password_hash
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
    """A test client for the app"""
    return app.test_client()

@pytest.fixture
def user(app: Flask) -> User:
    """Create a test user for UserViewTest."""
    user = User(
        full_name='Test User',
        email='test@example.com',
        password='testpassword',
        phone_number='1234567890'
    )
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def access_token(user: User) -> str:
    """Create a JWT access token for the test user."""
    access_token = create_access_token(identity=user.id)
    return access_token

@pytest.fixture
def auth_headers(access_token):
    """Create authorization headers with JWT token for UserViewTest."""
    return {'Authorization': f'Bearer {access_token}'}


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


class TestTokenRefresh:
    def test_token_refresh(self, client: FlaskClient):
        """Test the /token/refresh endpoint."""
        # Register a user first
        register_data = {
            'full_name': 'Test User',
            'email': 'test@example.com',
            'password': 'testpassword',
            'phone_number': '1234567890'
        }
        response = client.post('/api/v1/user/register', json=register_data)
        assert response.status_code == 201

        # Log in to get the refresh token
        login_data = {
            'email': 'test@example.com',
            'password': 'testpassword'
        }
        response = client.post('/api/v1/user/sign-in', json=login_data)
        assert response.status_code == 200
        refresh_token = response.json['data']['refresh']

        # Request a new access token using the refresh token
        headers = {'Authorization': f'Bearer {refresh_token}'}
        response = client.post('/api/v1/user/token/refresh', headers=headers)

        # Verify the response
        assert response.status_code == 200
        assert response.json['success'] is True
        assert 'access' in response.json['data']
        assert response.json['message'] == 'Access Token refreshed successfully'


class TestUserView:
    def test_get_user_details(self, client: FlaskClient, user: User, auth_headers: dict):
        """Test retrieving user details."""
        response = client.get('/api/v1/user/detail', headers=auth_headers)
        
        assert response.status_code == 200
        assert response.json['success'] is True
        assert response.json['data']['email'] == user.email
        assert response.json['data']['full_name'] == user.full_name
    
    def test_update_user_details(self, client: FlaskClient, user: User, auth_headers: dict):
        """Test updating user details."""
        update_data = {
            'full_name': 'Updated User',
            'phone_number': '0987654321'
        }
        
        response = client.put('/api/v1/user/detail', json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        assert response.json['success'] is True
        assert response.json['data']['full_name'] == 'Updated User'
        assert response.json['data']['phone_number'] == '0987654321'
        
        # Verify changes in the database
        updated_user = db.session.get(User, user.id)
        assert updated_user.full_name == 'Updated User'
        assert updated_user.phone_number == '0987654321'
    

class TestLogoutView:
    def test_logout(self, client: FlaskClient, auth_headers: dict):
        """Test logout and token invalidation."""
        response = client.post('/api/v1/user/sign-out', headers=auth_headers)

        assert response.status_code == 200
        assert response.json['success'] is True
        assert response.json['message'] == 'Token has been revoked and user logged out.'

    def test_access_with_revoked_token(self, client: FlaskClient, auth_headers: dict):
        """Test accessing endpoint with revoked token."""
        # Revoke the token by logging out
        client.post('/api/v1/user/sign-out', headers=auth_headers)

        # Attempt to access a protected endpoint with the same token
        response = client.get('/api/v1/user/detail', headers=auth_headers)

        assert response.status_code == 401
        assert response.json['msg'] == 'Token has been revoked'
