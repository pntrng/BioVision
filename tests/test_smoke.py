"""
Smoke tests for BioVision 3D API
Run with: pytest tests/test_smoke.py
"""
import pytest
import os
import json
import tempfile
from app import app, ADMIN_TOKEN, DATA_FILE

# Set test environment
os.environ['ADMIN_TOKEN'] = 'test-token-123'
os.environ['ENV'] = 'development'

@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def auth_headers():
    """Return headers with valid token"""
    return {'Authorization': 'Bearer test-token-123'}

def test_get_data_success(client):
    """Test GET /api/data returns 200"""
    response = client.get('/api/data')
    assert response.status_code == 200
    data = response.get_json()
    assert 'models' in data
    assert isinstance(data['models'], list)

def test_post_data_no_token(client):
    """Test POST /api/data without token returns 401"""
    response = client.post('/api/data',
                          json={'models': []},
                          content_type='application/json')
    assert response.status_code == 401
    data = response.get_json()
    assert 'error' in data

def test_post_data_invalid_token(client):
    """Test POST /api/data with invalid token returns 401"""
    response = client.post('/api/data',
                          json={'models': []},
                          headers={'Authorization': 'Bearer wrong-token'},
                          content_type='application/json')
    assert response.status_code == 401

def test_post_data_valid_token(client, auth_headers):
    """Test POST /api/data with valid token returns 200"""
    payload = {
        'models': [{
            'id': 'test_model',
            'grade': '10',
            'chapter': 'Test Chapter',
            'modelUid': 'test-uid',
            'items': []
        }]
    }
    response = client.post('/api/data',
                          json=payload,
                          headers=auth_headers,
                          content_type='application/json')
    assert response.status_code == 200
    data = response.get_json()
    assert data.get('status') == 'success'

def test_post_data_invalid_schema(client, auth_headers):
    """Test POST /api/data with invalid schema returns 400"""
    response = client.post('/api/data',
                          json={'invalid': 'data'},
                          headers=auth_headers,
                          content_type='application/json')
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data

def test_post_data_too_many_models(client, auth_headers):
    """Test POST /api/data with too many models returns 400"""
    payload = {'models': [{}] * 101}  # Exceeds MAX_MODELS
    response = client.post('/api/data',
                          json=payload,
                          headers=auth_headers,
                          content_type='application/json')
    assert response.status_code == 400

def test_security_headers(client):
    """Test security headers are present"""
    response = client.get('/')
    assert 'X-Content-Type-Options' in response.headers
    assert 'X-Frame-Options' in response.headers
    assert 'Content-Security-Policy' in response.headers

def test_admin_route_accessible(client):
    """Test /admin route is accessible"""
    response = client.get('/admin')
    assert response.status_code == 200

def test_guest_route_accessible(client):
    """Test / route is accessible"""
    response = client.get('/')
    assert response.status_code == 200
