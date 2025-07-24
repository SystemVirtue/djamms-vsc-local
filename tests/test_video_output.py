import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_video_output_state():
    response = client.get("/video-output/state")
    assert response.status_code == 200
    data = response.json()
    assert "is_live" in data
    assert "is_recording" in data

def test_start_stop_video_output():
    # Start
    response = client.post("/video-output/start")
    assert response.status_code == 200
    # Stop
    response = client.post("/video-output/stop")
    assert response.status_code == 200
