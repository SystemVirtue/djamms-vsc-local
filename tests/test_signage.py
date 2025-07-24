
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_signage_content_list():
    response = client.get("/signage/content")
    assert response.status_code in (200, 403)  # RBAC may block non-admin

def test_signage_preview():
    response = client.get("/signage/preview")
    assert response.status_code in (200, 403)
