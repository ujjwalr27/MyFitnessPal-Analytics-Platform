import pytest
from backend.app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_route(client):
    response = client.get('/')
    assert response.status_code == 200

def test_grafana_redirect(client):
    response = client.get('/grafana')
    assert response.status_code == 302  # Redirect status code 