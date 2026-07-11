# Task 4 User Login and Logout Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现邮箱密码登录、7 天 JWT httpOnly Cookie 和幂等退出接口。

**Architecture:** Pydantic 负责登录输入规范化，服务层负责用户查询和 Argon2 密码验证，安全模块负责 JWT 签发，FastAPI 路由负责 Cookie 写入与清除。Task 4 不解析登录态，`get_current_user` 和 `/auth/me` 留给 Task 5。

**Tech Stack:** FastAPI、Pydantic v2、SQLAlchemy 2、PostgreSQL、pwdlib/Argon2id、PyJWT、pytest、Ruff

---

### Task 1: JWT 依赖与鉴权配置

**Files:**
- Modify: `services/api/pyproject.toml`
- Modify: `services/api/app/core/config.py`
- Modify: `.env.example`
- Create: `services/api/tests/test_config.py`

- [ ] **Step 1: 编写配置失败测试**

创建 `tests/test_config.py`：

```python
from app.core.config import Settings


def test_auth_settings_have_safe_development_defaults():
    settings = Settings(
        _env_file=None,
        jwt_secret="test-secret",
    )

    assert settings.jwt_secret == "test-secret"
    assert settings.access_token_expire_days == 7
    assert settings.auth_cookie_name == "access_token"
    assert settings.auth_cookie_secure is False
```

- [ ] **Step 2: 运行测试确认 RED**

运行：

```powershell
cd services/api
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider tests/test_config.py -q
```

预期：因 Settings 尚无鉴权字段而 FAIL。

- [ ] **Step 3: 增加依赖和配置**

在 `pyproject.toml` 运行依赖增加：

```toml
"PyJWT>=2.10.0,<3.0.0",
```

在 Settings 增加：

```python
jwt_secret: str | None = None
access_token_expire_days: int = 7
auth_cookie_name: str = "access_token"
auth_cookie_secure: bool = False
```

在 `.env.example` 的 Backend 部分明确加入：

```dotenv
JWT_SECRET=change-me
ACCESS_TOKEN_EXPIRE_DAYS=7
AUTH_COOKIE_NAME=access_token
AUTH_COOKIE_SECURE=false
```

- [ ] **Step 4: 安装依赖并验证 GREEN**

```powershell
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider tests/test_config.py -q
.\.venv\Scripts\python.exe -m pip check
```

预期：配置测试通过，`pip check` 输出 `No broken requirements found.`。

- [ ] **Step 5: 提交**

```powershell
git add .env.example services/api/pyproject.toml services/api/app/core/config.py services/api/tests/test_config.py
git commit -m "chore: configure JWT authentication"
```

---

### Task 2: JWT 签发函数

**Files:**
- Modify: `services/api/app/core/security.py`
- Create: `services/api/tests/test_tokens.py`

- [ ] **Step 1: 编写 JWT 失败测试**

创建 `tests/test_tokens.py`：

```python
from datetime import UTC, datetime, timedelta
from uuid import UUID

import jwt
import pytest

from app.core.config import Settings
from app.core.security import create_access_token


USER_ID = UUID("11111111-1111-1111-1111-111111111111")
NOW = datetime(2026, 7, 11, tzinfo=UTC)


def test_create_access_token_has_expected_claims():
    token = create_access_token(
        USER_ID,
        settings=Settings(
            _env_file=None,
            jwt_secret="test-secret",
            access_token_expire_days=7,
        ),
        now=NOW,
    )

    claims = jwt.decode(token, "test-secret", algorithms=["HS256"])
    assert claims["sub"] == str(USER_ID)
    assert datetime.fromtimestamp(claims["iat"], UTC) == NOW
    assert datetime.fromtimestamp(claims["exp"], UTC) == NOW + timedelta(days=7)


def test_create_access_token_requires_secret():
    with pytest.raises(RuntimeError, match="JWT_SECRET 未配置"):
        create_access_token(
            USER_ID,
            settings=Settings(_env_file=None, jwt_secret=None),
            now=NOW,
        )
```

- [ ] **Step 2: 运行测试确认 RED**

```powershell
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider tests/test_tokens.py -q
```

预期：因 `create_access_token` 不存在而在测试收集阶段失败。

- [ ] **Step 3: 实现最小 JWT 签发**

在 `app/core/security.py` 增加：

```python
from datetime import UTC, datetime, timedelta
from uuid import UUID

import jwt

from app.core.config import Settings, settings as app_settings


def create_access_token(
    user_id: UUID,
    *,
    settings: Settings = app_settings,
    now: datetime | None = None,
) -> str:
    if not settings.jwt_secret:
        raise RuntimeError("JWT_SECRET 未配置")
    issued_at = now or datetime.now(UTC)
    expires_at = issued_at + timedelta(days=settings.access_token_expire_days)
    return jwt.encode(
        {"sub": str(user_id), "iat": issued_at, "exp": expires_at},
        settings.jwt_secret,
        algorithm="HS256",
    )
```

- [ ] **Step 4: 运行测试确认 GREEN**

```powershell
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider tests/test_tokens.py tests/test_security.py -q
```

预期：JWT 与既有 Argon2 测试全部通过。

- [ ] **Step 5: 提交**

```powershell
git add services/api/app/core/security.py services/api/tests/test_tokens.py
git commit -m "feat: issue JWT access tokens"
```

---

### Task 3: 登录请求 Schema

**Files:**
- Modify: `services/api/app/schemas/auth.py`
- Create: `services/api/tests/test_login_schema.py`

- [ ] **Step 1: 编写 Schema 失败测试**

创建 `tests/test_login_schema.py`：

```python
import pytest
from pydantic import ValidationError

from app.schemas.auth import LoginRequest


def test_login_request_normalizes_email():
    payload = LoginRequest(
        email="  User@Example.COM  ",
        password="valid-password",
    )
    assert str(payload.email) == "user@example.com"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("email", ""),
        ("email", "not-an-email"),
        ("password", "short"),
        ("password", "x" * 129),
    ],
)
def test_login_request_rejects_invalid_fields(field: str, value: str):
    data = {"email": "user@example.com", "password": "valid-password"}
    data[field] = value
    with pytest.raises(ValidationError):
        LoginRequest(**data)
```

- [ ] **Step 2: 运行测试确认 RED**

```powershell
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider tests/test_login_schema.py -q
```

预期：因 `LoginRequest` 不存在而在测试收集阶段失败。

- [ ] **Step 3: 实现 Schema 并复用邮箱规范化逻辑**

在 `auth.py` 提取：

```python
def normalize_email(value: Any) -> Any:
    if isinstance(value, str):
        return value.strip().lower()
    return value
```

让 `RegisterRequest.normalize_email` 调用该函数，并新增：

```python
class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email_value(cls, value: Any) -> Any:
        return normalize_email(value)
```

- [ ] **Step 4: 运行测试确认 GREEN**

```powershell
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider tests/test_login_schema.py tests/test_auth_schemas.py -q
```

预期：登录 Schema 和既有注册 Schema 测试全部通过。

- [ ] **Step 5: 提交**

```powershell
git add services/api/app/schemas/auth.py services/api/tests/test_login_schema.py
git commit -m "feat: define login request schema"
```

---

### Task 4: 用户认证服务

**Files:**
- Modify: `services/api/app/services/auth_service.py`
- Create: `services/api/tests/test_authenticate_user.py`

- [ ] **Step 1: 编写真实数据库认证失败测试**

创建 `tests/test_authenticate_user.py`，使用现有 `database_session`：

```python
import pytest

from app.core.errors import AppError
from app.schemas.auth import LoginRequest, RegisterRequest
from app.services.auth_service import authenticate_user, register_user


def create_user(database_session):
    return register_user(
        database_session,
        RegisterRequest(
            email="login@example.com",
            password="correct-password",
            display_name="登录用户",
        ),
    )


def test_authenticate_user_accepts_correct_credentials(database_session):
    user = create_user(database_session)
    authenticated = authenticate_user(
        database_session,
        LoginRequest(
            email="  LOGIN@EXAMPLE.COM  ",
            password="correct-password",
        ),
    )
    assert authenticated.id == user.id


@pytest.mark.parametrize(
    ("email", "password"),
    [
        ("missing@example.com", "correct-password"),
        ("login@example.com", "wrong-password"),
    ],
)
def test_authenticate_user_hides_failure_reason(database_session, email, password):
    create_user(database_session)
    with pytest.raises(AppError) as captured:
        authenticate_user(
            database_session,
            LoginRequest(email=email, password=password),
        )
    assert captured.value.status_code == 401
    assert captured.value.code == "INVALID_CREDENTIALS"
    assert captured.value.message == "邮箱或密码错误"
```

- [ ] **Step 2: 运行测试确认 RED**

```powershell
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider tests/test_authenticate_user.py -q
```

预期：因 `authenticate_user` 不存在而在测试收集阶段失败。

- [ ] **Step 3: 实现最小认证服务**

在 `auth_service.py` 增加：

```python
from app.core.security import hash_password, verify_password
from app.schemas.auth import LoginRequest, RegisterRequest


def invalid_credentials() -> AppError:
    return AppError(
        status_code=401,
        code="INVALID_CREDENTIALS",
        message="邮箱或密码错误",
    )


def authenticate_user(database_session: Session, payload: LoginRequest) -> User:
    user = database_session.scalar(
        select(User).where(User.email == str(payload.email))
    )
    if user is None or not verify_password(payload.password, user.password_hash):
        raise invalid_credentials()
    return user
```

- [ ] **Step 4: 运行测试确认 GREEN**

```powershell
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider tests/test_authenticate_user.py tests/test_auth_service.py -q
```

预期：登录认证和注册服务测试全部通过。

- [ ] **Step 5: 提交**

```powershell
git add services/api/app/services/auth_service.py services/api/tests/test_authenticate_user.py
git commit -m "feat: authenticate users with passwords"
```

---

### Task 5: 登录与退出 API

**Files:**
- Modify: `services/api/app/api/v1/auth.py`
- Create: `services/api/tests/test_auth_login.py`
- Create: `services/api/tests/test_auth_logout.py`

- [ ] **Step 1: 编写登录 API 失败测试**

创建 `tests/test_auth_login.py`：

```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db_session
from app.main import app
from app.schemas.auth import RegisterRequest
from app.services.auth_service import register_user


@pytest.fixture
def client(database_session: Session, monkeypatch: pytest.MonkeyPatch):
    def override_database_session():
        yield database_session

    monkeypatch.setattr(settings, "jwt_secret", "test-secret")
    monkeypatch.setattr(settings, "auth_cookie_secure", False)
    app.dependency_overrides[get_db_session] = override_database_session
    register_user(
        database_session,
        RegisterRequest(
            email="login@example.com",
            password="correct-password",
            display_name="登录用户",
        ),
    )
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


def test_login_returns_user_and_http_only_cookie(client: TestClient):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "  LOGIN@EXAMPLE.COM  ",
            "password": "correct-password",
        },
    )

    assert response.status_code == 200
    assert response.json()["email"] == "login@example.com"
    assert "password_hash" not in response.text
    set_cookie = response.headers["set-cookie"]
    assert "access_token=" in set_cookie
    assert "HttpOnly" in set_cookie
    assert "SameSite=lax" in set_cookie
    assert "Path=/" in set_cookie
    assert "Max-Age=604800" in set_cookie
    assert "Secure" not in set_cookie


def test_login_sets_secure_cookie_when_configured(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(settings, "auth_cookie_secure", True)
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "login@example.com", "password": "correct-password"},
    )
    assert "Secure" in response.headers["set-cookie"]


@pytest.mark.parametrize(
    ("email", "password"),
    [
        ("missing@example.com", "correct-password"),
        ("login@example.com", "wrong-password"),
    ],
)
def test_login_hides_invalid_credential_reason(client, email, password):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == 401
    assert response.json() == {
        "error": {
            "code": "INVALID_CREDENTIALS",
            "message": "邮箱或密码错误",
            "details": {},
        }
    }


def test_login_rejects_invalid_payload(client: TestClient):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "not-an-email", "password": "short"},
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
    assert response.json()["error"]["message"] == "请求参数校验失败"
```

- [ ] **Step 2: 编写退出 API 失败测试**

创建 `tests/test_auth_logout.py`：

```python
import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app


@pytest.mark.parametrize("has_cookie", [False, True])
def test_logout_is_idempotent_and_clears_cookie(has_cookie: bool):
    client = TestClient(app)
    if has_cookie:
        client.cookies.set(settings.auth_cookie_name, "opaque-test-token")

    response = client.post("/api/v1/auth/logout")

    assert response.status_code == 204
    assert response.content == b""
    set_cookie = response.headers["set-cookie"]
    assert f"{settings.auth_cookie_name}=" in set_cookie
    assert "Max-Age=0" in set_cookie
    assert "Path=/" in set_cookie
```

- [ ] **Step 3: 运行测试确认 RED**

```powershell
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider tests/test_auth_login.py tests/test_auth_logout.py -q
```

预期：登录和退出路由均返回 404。

- [ ] **Step 4: 实现登录与退出路由**

在 `app/api/v1/auth.py` 增加：

```python
from fastapi import Response

from app.core.config import settings
from app.core.security import create_access_token
from app.schemas.auth import LoginRequest
from app.services.auth_service import authenticate_user


@router.post("/login", response_model=UserResponse)
def login(
    payload: LoginRequest,
    response: Response,
    database_session: Annotated[Session, Depends(get_db_session)],
) -> UserResponse:
    user = authenticate_user(database_session, payload)
    response.set_cookie(
        key=settings.auth_cookie_name,
        value=create_access_token(user.id),
        max_age=settings.access_token_expire_days * 24 * 60 * 60,
        httponly=True,
        secure=settings.auth_cookie_secure,
        samesite="lax",
        path="/",
    )
    return UserResponse.model_validate(user)


@router.post("/logout", status_code=204)
def logout(response: Response) -> None:
    response.delete_cookie(
        key=settings.auth_cookie_name,
        path="/",
        httponly=True,
        secure=settings.auth_cookie_secure,
        samesite="lax",
    )
```

- [ ] **Step 5: 运行 API 与全量测试确认 GREEN**

```powershell
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider tests/test_auth_login.py tests/test_auth_logout.py -q
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider -q
.\.venv\Scripts\python.exe -m ruff check --no-cache .
.\.venv\Scripts\python.exe -m ruff format --check --no-cache .
```

预期：登录退出测试通过，完整测试无回归，Ruff 和格式检查通过。

- [ ] **Step 6: 提交**

```powershell
git add services/api/app/api/v1/auth.py services/api/tests/test_auth_login.py services/api/tests/test_auth_logout.py
git commit -m "feat: add login and logout endpoints"
```

---

### Task 6: 文档与最终质量门禁

**Files:**
- Modify: `README.md`

- [ ] **Step 1: 更新 README**

将当前阶段更新为 Task 4 已完成、下一步 Task 5；记录登录和退出接口、Cookie 登录态及开发环境 `JWT_SECRET` 要求，不描述尚未实现的 `/auth/me` 或受保护接口。

- [ ] **Step 2: 串行运行最终门禁**

确认 `db-test` 健康，再依次执行：

```powershell
cd services/api
.\.venv\Scripts\python.exe -m ruff check --no-cache .
.\.venv\Scripts\python.exe -m ruff format --check --no-cache .
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider -q
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -c "from alembic import command; from alembic.config import Config; from app.core.config import Settings; c=Config('alembic.ini'); c.set_main_option('sqlalchemy.url', Settings().test_database_url); command.check(c)"
```

预期：全部命令退出码为 0，无测试失败、依赖冲突或迁移漂移。

- [ ] **Step 3: 真实 Uvicorn 冒烟验证**

在开发库创建唯一冒烟用户，启动 Uvicorn 后实际验证：

1. 登录返回 200 和 `Set-Cookie`。
2. Cookie 包含 HttpOnly、SameSite=Lax、Path=/、Max-Age。
3. 退出返回 204 并清除 Cookie。
4. 精确匹配唯一邮箱并删除冒烟用户，确认剩余 0 条。

不得在输出中打印 JWT Cookie 正文。

- [ ] **Step 4: 提交文档**

```powershell
git add README.md
git commit -m "docs: record Task 4 completion"
```

- [ ] **Step 5: 推送功能分支**

```powershell
git push -u origin feat/v0.1-task4-login
```

预期：工作区干净，本地与远程功能分支同步；不自动合并到 `main`。
