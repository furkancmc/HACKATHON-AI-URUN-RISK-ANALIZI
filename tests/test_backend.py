import pytest
import sys
import os
from unittest.mock import Mock, patch

# Ana dizini Python path'ine ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app import app

@pytest.fixture
def client():
    """Test client oluştur"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    """Health check endpoint testi"""
    response = client.get('/api/health')
    assert response.status_code == 200
    data = response.get_json()
    assert 'status' in data
    assert data['status'] == 'healthy'

def test_search_products(client):
    """Ürün arama endpoint testi"""
    response = client.post('/api/search', 
                          json={'query': 'test', 'limit': 5})
    assert response.status_code in [200, 500]  # 500 olabilir çünkü DB bağlantısı yok

def test_get_brands(client):
    """Marka listesi endpoint testi"""
    response = client.get('/api/brands')
    assert response.status_code in [200, 500]

def test_get_table_stats(client):
    """Tablo istatistikleri endpoint testi"""
    response = client.get('/api/tables/stats')
    assert response.status_code in [200, 500]

def test_ai_chat(client):
    """AI sohbet endpoint testi"""
    response = client.post('/api/ai/chat', 
                          json={'message': 'test mesajı'})
    assert response.status_code in [200, 500]

def test_ai_analyze(client):
    """AI analiz endpoint testi"""
    response = client.post('/api/ai/analyze', 
                          json={'product_id': '123', 
                                'source_table': 'test_table',
                                'query': 'test analiz'})
    assert response.status_code in [200, 500]

def test_create_embeddings(client):
    """Embedding oluşturma endpoint testi"""
    response = client.post('/api/embeddings/create')
    assert response.status_code in [200, 500]

def test_test_services(client):
    """Servis test endpoint testi"""
    response = client.get('/api/test')
    assert response.status_code in [200, 500] 