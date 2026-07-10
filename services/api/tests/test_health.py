from fastapi.testclient import TestClient

from app.main import app, create_app


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


def test_validation_error_returns_uniform_chinese_error():
    application = create_app()

    @application.get("/validation-probe")
    def validation_probe(count: int) -> dict[str, int]:
        return {"count": count}

    response = TestClient(application).get("/validation-probe?count=invalid")

    assert response.status_code == 422
    payload = response.json()
    assert set(payload) == {"error"}
    assert payload["error"]["code"] == "VALIDATION_ERROR"
    assert payload["error"]["message"] == "请求参数校验失败"
    assert payload["error"]["details"]["errors"]


def test_unhandled_exception_returns_safe_uniform_error():
    application = create_app()

    @application.get("/failure-probe")
    def failure_probe() -> None:
        raise RuntimeError("不应泄露的内部错误")

    response = TestClient(application, raise_server_exceptions=False).get(
        "/failure-probe"
    )

    assert response.status_code == 500
    assert response.headers["content-type"] == "application/json"
    assert response.json() == {
        "error": {
            "code": "INTERNAL_SERVER_ERROR",
            "message": "服务器内部错误",
            "details": {},
        }
    }
    assert "不应泄露的内部错误" not in response.text
