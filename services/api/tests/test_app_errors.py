from app.core.errors import unauthorized
from app.main import create_app
from fastapi.testclient import TestClient


def test_unauthorized_has_fixed_public_contract():
    error = unauthorized()

    assert error.status_code == 401
    assert error.code == "UNAUTHORIZED"
    assert error.message == "登录状态无效或已过期"
    assert error.details == {}


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
