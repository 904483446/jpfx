from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_check_returns_ok():
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_not_found_returns_uniform_error_shape():
    response = client.get("/api/v1/not-found")

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "NOT_FOUND",
            "message": "接口不存在",
            "details": {"path": "/api/v1/not-found"},
        }
    }
