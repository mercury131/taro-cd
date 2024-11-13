import json
import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_get_cards(client):
    response = client.get('/cards')
    assert response.status_code == 200
    assert len(json.loads(response.data)) == len(app.tarot_cards)

def test_draw_cards(client):
    response = client.post('/draw', data=json.dumps({'num_cards': 5}), content_type='application/json')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['num_cards'] == 5
    assert len(data['drawn_cards'].split(', ')) == 5
    assert data['reading'] in ['good', 'bad']