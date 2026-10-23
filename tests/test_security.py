import pytest
import io
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_security_headers_present():
    response = client.get("/")
    assert response.status_code == 200
    headers = response.headers
    assert headers.get("X-Content-Type-Options") == "nosniff"
    assert headers.get("X-Frame-Options") == "SAMEORIGIN"
    assert headers.get("X-XSS-Protection") == "1; mode=block"
    assert "max-age=31536000" in headers.get("Strict-Transport-Security", "")
    assert "default-src" in headers.get("Content-Security-Policy", "")

def test_input_sanitization_xss():
    payload = {
        "raw_input": "<script>alert('XSS')</script> Pothole in Sector 22 Market",
        "channel": "WEB"
    }
    response = client.post("/api/v1/grievances", json=payload)
    assert response.status_code == 200
    data = response.json()
    # The script tag should be escaped
    assert "<script>" not in data["raw_input"]
    assert "&lt;script&gt;" in data["raw_input"]

def test_audio_upload_unsupported_format():
    fake_file = io.BytesIO(b"malicious script payload")
    response = client.post(
        "/api/v1/voice/upload",
        files={"file": ("malicious.exe", fake_file, "application/octet-stream")}
    )
    assert response.status_code == 400
    assert "Unsupported file format" in response.json()["detail"]

def test_empty_input_rejected():
    payload = {
        "raw_input": "   ",
        "channel": "WEB"
    }
    response = client.post("/api/v1/grievances", json=payload)
    assert response.status_code == 400

def test_invalid_status_rejected():
    list_res = client.get("/api/v1/grievances")
    first_id = list_res.json()[0]["id"]
    response = client.patch(f"/api/v1/grievances/{first_id}/status", json={"status": "HACKED_STATE"})
    assert response.status_code == 400
    assert "Invalid status" in response.json()["detail"]
