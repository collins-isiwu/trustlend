import pytest
import json
from flask import Flask
from flask.testing import FlaskClient
from app import create_app, db
from app.models import User, Verification
from flask_jwt_extended import create_access_token
from app.environment import TestingEnvironment


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
def client(app):
    """A test client for the app"""
    return app.test_client()


def test_verification_get(client):
    # Create a user and add to the database
    user = User(email="testuser@example.com", password="hashedpassword", full_name='Test User')
    db.session.add(user)
    db.session.commit()

    # Generate access token
    access_token = create_access_token(identity=user.id)
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    # Test fetching verification status when no verification exists
    response = client.get('api/v1/verification', headers=headers)
    assert response.status_code == 404
    assert response.json['error'] == 'Verification Not Found'

    # Add a verification entry for the user
    verification = Verification(
        address="123 Main St",
        bvn="12345678901",
        user_id=user.id
    )
    db.session.add(verification)
    db.session.commit()

    # Test fetching verification status when verification exists
    response = client.get('api/v1/verification', headers=headers)
    assert response.status_code == 200
    assert response.json['message'] == 'User is not verified!'

def test_verification_post(client):
    # Create a user and add to the database
    user = User(email="testuser@example.com", password="hashedpassword", full_name='Test User',)
    db.session.add(user)
    db.session.commit()

    # Generate access token
    access_token = create_access_token(identity=user.id)
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    # Test posting verification data
    verification_data = {
        "address": "123 Main St",
        "bvn": "12345678901"
    }
    response = client.post('api/v1/verification', headers=headers, data=json.dumps(verification_data))
    assert response.status_code == 201
    assert response.json['message'] == 'Verification request has been created'

    # Test posting verification data again should fail
    response = client.post('api/v1/verification', headers=headers, data=json.dumps(verification_data))
    assert response.status_code == 400
    assert response.json['message'] == 'Verification request already exists.'

    # Test posting with incomplete data
    incomplete_data = {
        "address": "123 Main St"
    }
    response = client.post('api/v1/verification', headers=headers, data=json.dumps(incomplete_data))
    assert response.status_code == 400