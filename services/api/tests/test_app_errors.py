from app.main import create_app
from fastapi.testclient import TestClient


def test_app_error_returns_public_uniform_error():
    from app.core.errors import AppError

    application = create_app()

    @application.get("/business-error-probe")
    def business_error_probe() -> None:
        raise AppError(
            status_code=409,
            code="EMAIL_ALREADY_REGISTERED",
            message="该邮箱已注册",
        )

    response = TestClient(application, raise_server_exceptions=False).get(
        "/business-error-probe"
    )

    assert response.status_code == 409
    assert response.json() == {
        "error": {
            "code": "EMAIL_ALREADY_REGISTERED",
            "message": "该邮箱已注册",
            "details": {},
        }
    }
