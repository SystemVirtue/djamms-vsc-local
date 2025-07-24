
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_system_status():
    response = client.get("/system/status")
    assert response.status_code == 200
    data = response.json()
    assert "database" in data
    assert "redis" in data
    assert data["database"] == "ok"
    assert data["redis"] == "ok"

def test_get_connected_devices():
    response = client.get("/system/devices")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_update_device():
    updates = {"name": "Updated Device", "status": "online"}
    response = client.put("/system/devices/dev-1", json=updates)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "dev-1"
    assert data["updated"] == updates

def test_configure_device():
    config = {"volume": 80, "mode": "auto"}
    response = client.post("/system/devices/dev-1/config", json=config)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "dev-1"
    assert data["config"] == config
    assert data["status"] == "applied"
