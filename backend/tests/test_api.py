import io
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    assert client.get('/api/health').json() == {'status': 'ok'}

def test_reject_non_csv():
    response = client.post('/api/datasets', files={'file': ('customers.txt', b'not csv', 'text/plain')})
    assert response.status_code == 400

def test_dashboard_empty_or_populated_shape():
    result = client.get('/api/dashboard')
    assert result.status_code == 200
    assert {'customers', 'clusters', 'distribution'} <= result.json().keys()
