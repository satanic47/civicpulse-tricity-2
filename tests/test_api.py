import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "CivicPulse Tricity" in data["service"]
    assert "Gemma 4" in data["ai_engine"]["models"]

def test_homepage_render():
    response = client.get("/")
    assert response.status_code == 200
    assert "CivicPulse Tricity" in response.text
    assert "NagrikSetu AI" in response.text

def test_list_grievances():
    response = client.get("/api/v1/grievances")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 10

def test_create_grievance():
    payload = {
        "raw_input": "Dangerous pothole on Madhya Marg Sector 8 near DAV college",
        "channel": "WEB"
    }
    response = client.post("/api/v1/grievances", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["sector"] == "Sector 8"
    assert data["category"] == "Roads & Traffic"
    assert data["urgency_score"] >= 5

def test_get_hotspots():
    response = client.get("/api/v1/hotspots")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1

def test_get_sectors():
    response = client.get("/api/v1/sectors")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert "infrastructure_health_score" in data[0]

def test_get_policy_recommendations():
    response = client.get("/api/v1/recommendations")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert "priority_score" in data[0]

def test_upvote_grievance():
    # First get an existing ID
    list_res = client.get("/api/v1/grievances")
    first_id = list_res.json()[0]["id"]
    initial_upvotes = list_res.json()[0].get("upvotes", 1)

    upvote_res = client.post(f"/api/v1/grievances/{first_id}/upvote")
    assert upvote_res.status_code == 200
    assert upvote_res.json()["upvotes"] == initial_upvotes + 1

def test_whatsapp_webhook():
    response = client.post("/api/v1/webhook/whatsapp", data={"Body": "ਸੈਕਟਰ 20 ਵਿੱਚ ਕੂੜੇ ਦਾ ਢੇਰ ਲੱਗਿਆ ਹੋਇਆ ਹੈ"})
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_stats_endpoint():
    response = client.get("/api/v1/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_grievances" in data
    assert "by_category" in data
    assert "by_language" in data
