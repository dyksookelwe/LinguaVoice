from fastapi.testclient import TestClient

from app.main import app


def test_index_page_is_served():
    response = TestClient(app).get("/")
    assert response.status_code == 200
    assert "LinguaVoice" in response.text