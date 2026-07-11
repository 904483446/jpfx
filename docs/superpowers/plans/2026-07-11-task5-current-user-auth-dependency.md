# Task 5：当前用户与鉴权依赖 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 提供受 Cookie JWT 保护的 `GET /api/v1/auth/me`，并提供后续业务接口可复用、返回 ORM `User` 的 `get_current_user` 依赖。

**Architecture:** 在 `app.core.security` 集中复用 JWT 密钥配置校验；在 `app.core.errors` 提供唯一的 `unauthorized()` 业务异常工厂。`app.api.deps.get_current_user` 只读取 Cookie、严格按 HS256 解码、验证 UUID `sub` 并查询当前用户，不写 Cookie、不提交事务；`/auth/me` 只将该 ORM 实体序列化为现有 `UserResponse`。

**Tech Stack:** FastAPI、Pydantic v2、同步 SQLAlchemy 2、PyJWT、pytest、httpx TestClient、Ruff、Alembic、PostgreSQL + pgvector。

---

## 文件职责与变更边界

- `services/api/app/core/security.py`：抽取 JWT 密钥的统一运行时校验，供签发和解码路径共用。
- `services/api/app/core/errors.py`：提供固定公开响应的 `unauthorized()` 工厂。
- `services/api/app/api/deps.py`：实现只读的当前用户鉴权依赖。
- `services/api/app/api/v1/auth.py`：新增 `GET /auth/me`，复用依赖与 `UserResponse`。
- `services/api/tests/test_auth_dependencies.py`：以真实隔离 PostgreSQL 验证依赖的 Token、`sub`、用户存在性及可复用 probe 行为。
- `services/api/tests/test_auth_me.py`：验证 `/auth/me` 的 Cookie 会话契约、公开字段与所有无效身份态的统一 401 响应。
- `services/api/tests/test_tokens.py`、`services/api/tests/test_app_errors.py`：覆盖抽取后的密钥校验和未授权工厂。
- `README.md`：仅在功能、全量质量门禁和烟雾验证全部通过后，将当前阶段更新为 Task 5 已完成、下一步为 Task 6。

不新增迁移、不新增产品空间 API、不增加刷新 Token、黑名单、会话表、角色权限、管理员功能或前端代码。

### Task 1：固定未授权错误与共用 JWT 密钥校验

**Files:**

- Modify: `services/api/app/core/errors.py`
- Modify: `services/api/app/core/security.py`
- Modify: `services/api/tests/test_app_errors.py`
- Modify: `services/api/tests/test_tokens.py`

- [ ] **Step 1: 写出未授权工厂和解码侧密钥校验的失败测试**

```python
# services/api/tests/test_app_errors.py
from app.core.errors import unauthorized


def test_unauthorized_has_fixed_public_contract():
    error = unauthorized()

    assert error.status_code == 401
    assert error.code == "UNAUTHORIZED"
    assert error.message == "登录状态无效或已过期"
    assert error.details == {}
```

```python
# services/api/tests/test_tokens.py
from app.core.security import get_jwt_secret


def test_get_jwt_secret_returns_configured_secret():
    assert get_jwt_secret(Settings(_env_file=None, jwt_secret=TEST_SECRET)) == TEST_SECRET


@pytest.mark.parametrize(
    ("secret", "message"),
    [
        (None, "JWT_SECRET 未配置"),
        ("x" * 31, "JWT_SECRET 至少需要 32 字节"),
    ],
)
def test_get_jwt_secret_rejects_missing_or_weak_secret(secret: str | None, message: str):
    with pytest.raises(RuntimeError, match=message):
        get_jwt_secret(Settings(_env_file=None, jwt_secret=secret))
```

- [ ] **Step 2: 运行失败测试，确认新符号尚不存在**

Run: `cd services/api; .\.venv\Scripts\python.exe -m pytest -p no:cacheprovider -q tests/test_app_errors.py tests/test_tokens.py`

Expected: FAIL，导入 `unauthorized` 和 `get_jwt_secret` 时失败；现有 Token 测试不应被删除。

- [ ] **Step 3: 实现最小的共享工厂与密钥校验**

```python
# services/api/app/core/errors.py（追加在 AppError 后）
def unauthorized() -> AppError:
    return AppError(
        status_code=401,
        code="UNAUTHORIZED",
        message="登录状态无效或已过期",
    )
```

```python
# services/api/app/core/security.py（在 create_access_token 前新增）
def get_jwt_secret(settings: Settings = app_settings) -> str:
    if not settings.jwt_secret:
        raise RuntimeError("JWT_SECRET 未配置")
    if len(settings.jwt_secret.encode("utf-8")) < 32:
        raise RuntimeError("JWT_SECRET 至少需要 32 字节")
    return settings.jwt_secret


# create_access_token 内删除原有两段 if，改为：
secret = get_jwt_secret(settings)

# jwt.encode 的第二个参数改为：
secret,
```

- [ ] **Step 4: 运行定向测试，确认 GREEN**

Run: `cd services/api; .\.venv\Scripts\python.exe -m pytest -p no:cacheprovider -q tests/test_app_errors.py tests/test_tokens.py`

Expected: PASS；原有 `create_access_token` 的缺失/弱密钥测试仍通过，确保 Task 4 行为没有回归。

- [ ] **Step 5: 提交该独立阶段**

```powershell
git status --short --branch
git add services/api/app/core/errors.py services/api/app/core/security.py services/api/tests/test_app_errors.py services/api/tests/test_tokens.py
git commit -m "feat: add shared unauthorized auth primitives"
```

Expected: 仅上述四个文件进入提交，分支仍为 `feat/v0.1-task5-current-user`。

### Task 2：实现只读、可复用的当前用户依赖

**Files:**

- Create: `services/api/app/api/deps.py`
- Create: `services/api/tests/test_auth_dependencies.py`

- [ ] **Step 1: 写出依赖的失败测试，覆盖有效 Token 和无效身份态**

```python
# services/api/tests/test_auth_dependencies.py（关键辅助函数和断言）
from datetime import UTC, datetime, timedelta
from typing import Annotated
from uuid import UUID, uuid4

import jwt
import pytest
from app.api.deps import get_current_user
from app.core.config import settings
from app.db.session import get_db_session
from app.main import create_app
from app.models import User
from app.schemas.auth import RegisterRequest
from app.services.auth_service import register_user
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

TEST_SECRET = "test-secret-with-at-least-32-bytes"


def issue_token(claims: dict[str, object]) -> str:
    return jwt.encode(claims, TEST_SECRET, algorithm="HS256")


def valid_claims(user_id: UUID) -> dict[str, object]:
    now = datetime.now(UTC)
    return {"sub": str(user_id), "iat": now, "exp": now + timedelta(days=1)}


@pytest.fixture
def application(database_session: Session, monkeypatch: pytest.MonkeyPatch) -> FastAPI:
    monkeypatch.setattr(settings, "jwt_secret", TEST_SECRET)
    app = create_app()

    def override_database_session():
        yield database_session

    app.dependency_overrides[get_db_session] = override_database_session
    yield app
    app.dependency_overrides.clear()


def test_get_current_user_returns_database_user(application: FastAPI, database_session: Session):
    user = register_user(database_session, RegisterRequest(
        email="dependency@example.com", password="valid-password", display_name="依赖用户"
    ))

    @application.get("/protected-probe")
    def protected_probe(current_user: Annotated[User, Depends(get_current_user)]):
        return {"user_id": str(current_user.id)}

    response = TestClient(application).get(
        "/protected-probe",
        cookies={settings.auth_cookie_name: issue_token(valid_claims(user.id))},
    )

    assert response.status_code == 200
    assert response.json() == {"user_id": str(user.id)}
```

在同一文件增加参数化测试，向 `/protected-probe` 发送以下 Cookie 值：缺失 Cookie、`"not.a.jwt"`、使用另一密钥签发的 Token、已过期 Token、没有 `sub` 的 Token、`sub="not-a-uuid"` 的 Token、`sub=str(uuid4())` 的 Token。每个用例都必须断言完全相同的响应：

```python
{
    "error": {
        "code": "UNAUTHORIZED",
        "message": "登录状态无效或已过期",
        "details": {},
    }
}
```

另增加配置错误测试：使用 `monkeypatch.setattr(settings, "jwt_secret", "x" * 31)` 调用有效 Token 的 probe，断言 HTTP 500 `INTERNAL_SERVER_ERROR`，证明弱服务端密钥不会伪装为 401。

- [ ] **Step 2: 运行依赖测试，确认 RED**

Run: `cd services/api; .\.venv\Scripts\python.exe -m pytest -p no:cacheprovider -q tests/test_auth_dependencies.py`

Expected: FAIL，因 `app.api.deps` 尚不存在；不得为使测试通过而跳过无效 Token 用例。

- [ ] **Step 3: 实现最小的无副作用依赖**

```python
# services/api/app/api/deps.py
from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Cookie, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import unauthorized
from app.core.security import get_jwt_secret
from app.db.session import get_db_session
from app.models import User


def get_current_user(
    database_session: Annotated[Session, Depends(get_db_session)],
    access_token: Annotated[
        str | None,
        Cookie(alias=settings.auth_cookie_name),
    ] = None,
) -> User:
    if access_token is None:
        raise unauthorized()
    try:
        payload = jwt.decode(
            access_token,
            get_jwt_secret(),
            algorithms=["HS256"],
        )
        user_id = UUID(payload["sub"])
    except (jwt.PyJWTError, KeyError, TypeError, ValueError):
        raise unauthorized() from None
    user = database_session.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise unauthorized()
    return user
```

保持上述 FastAPI 依赖注入签名：`database_session` 为无默认值的 `Annotated[Session, Depends(get_db_session)]`，Cookie 参数带默认值且位于最后。保持解码调用中的 `algorithms=["HS256"]` 字面量；只捕获 Token/声明解析异常，不捕获 `get_jwt_secret()` 的 `RuntimeError`。不得调用 `commit()`、`refresh()`、`set_cookie()`、`delete_cookie()` 或记录 Token 内容。

- [ ] **Step 4: 运行依赖测试，确认 GREEN**

Run: `cd services/api; .\.venv\Scripts\python.exe -m pytest -p no:cacheprovider -q tests/test_auth_dependencies.py`

Expected: PASS；探针证明任意后续路由可依赖 `get_current_user`，且七类无效身份态具有相同 401 公开响应。

- [ ] **Step 5: 提交该独立阶段**

```powershell
git status --short --branch
git add services/api/app/api/deps.py services/api/tests/test_auth_dependencies.py
git commit -m "feat: add current user authentication dependency"
```

Expected: 仅依赖实现及其测试进入该提交。

### Task 3：暴露 `GET /api/v1/auth/me`

**Files:**

- Modify: `services/api/app/api/v1/auth.py`
- Create: `services/api/tests/test_auth_me.py`

- [ ] **Step 1: 写出 `/auth/me` 的失败 API 测试**

```python
# services/api/tests/test_auth_me.py（核心成功用例）
def test_me_returns_logged_in_user_without_sensitive_fields(client: TestClient):
    login_response = client.post(
        "/api/v1/auth/login",
        json={"email": "me@example.com", "password": "correct-password"},
    )
    assert login_response.status_code == 200

    response = client.get("/api/v1/auth/me")

    assert response.status_code == 200
    assert response.json()["email"] == "me@example.com"
    assert response.json()["display_name"] == "当前用户"
    assert response.json()["is_admin"] is False
    assert "password" not in response.text
    assert "password_hash" not in response.text
    assert "access_token" not in response.text
    assert "set-cookie" not in response.headers
```

复用 Task 4 的 `database_session` 覆盖和测试密钥模式创建 `client` fixture，并预置 `me@example.com`。在同一文件以参数化测试覆盖缺失 Cookie、篡改签名、过期 Token、缺失 `sub`、非 UUID `sub`、不存在用户，逐一断言状态码 401、响应体为 Task 2 的固定 `UNAUTHORIZED` JSON，且响应没有 `set-cookie`。

- [ ] **Step 2: 运行 API 测试，确认 RED**

Run: `cd services/api; .\.venv\Scripts\python.exe -m pytest -p no:cacheprovider -q tests/test_auth_me.py`

Expected: FAIL 或 404；`GET /api/v1/auth/me` 尚未注册。

- [ ] **Step 3: 注册最小路由并复用现有公开响应模型**

```python
# services/api/app/api/v1/auth.py（新增 import）
from app.api.deps import get_current_user
from app.models import User


# 在 logout 路由前新增
@router.get("/me", response_model=UserResponse)
def get_me(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserResponse:
    return UserResponse.model_validate(current_user)
```

不得在路由中解码 JWT、查询数据库、清 Cookie 或发放新 Token；保留登录、注册与退出的既有行为不变。

- [ ] **Step 4: 运行 `/auth/me` 与 Task 4 回归测试，确认 GREEN**

Run: `cd services/api; .\.venv\Scripts\python.exe -m pytest -p no:cacheprovider -q tests/test_auth_me.py tests/test_auth_login.py tests/test_auth_logout.py tests/test_authenticate_user.py`

Expected: PASS；`/auth/me` 只暴露 `UserResponse` 字段，登录和退出 Cookie 合约不回归。

- [ ] **Step 5: 提交该独立阶段**

```powershell
git status --short --branch
git add services/api/app/api/v1/auth.py services/api/tests/test_auth_me.py
git commit -m "feat: add current user endpoint"
```

Expected: 仅路由实现与其 API 测试进入该提交。

### Task 4：完成文档与串行质量门禁

**Files:**

- Modify: `README.md`

- [ ] **Step 1: 在全量验证之前，运行静态检查和测试（pytest 与 Alembic 不并行）**

```powershell
cd services/api
.\.venv\Scripts\python.exe -m ruff check --no-cache .
.\.venv\Scripts\python.exe -m ruff format --check --no-cache .
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider -q
.\.venv\Scripts\python.exe -m pip check
```

Expected: 四条命令均退出码 0。若 `db-test` 未运行，先只读执行 `docker compose ps db-test`；确认已停止后才执行 `docker compose up -d --wait db-test`，该 Docker 写操作如触发沙箱限制则请求授权。pytest 不得与下面 Alembic 检查并行。

- [ ] **Step 2: 串行运行 Alembic `command.check()`**

```powershell
cd services/api
@'
from alembic import command
from alembic.config import Config
from app.core.config import Settings

configuration = Config("alembic.ini")
configuration.set_main_option("sqlalchemy.url", Settings().test_database_url)
command.check(configuration)
print("ALEMBIC_CHECK=ok")
'@ | .\.venv\Scripts\python.exe -
```

Expected: 输出 `ALEMBIC_CHECK=ok`；不生成新的迁移文件。

- [ ] **Step 3: 进行真实 Uvicorn Cookie 会话烟雾验证并精确清理唯一用户**

在 PowerShell 中以后台隐藏窗口启动 `app.main:app`，使用唯一 UUID 后缀生成 `task5-smoke-<uuid>@example.com` 邮箱；通过 HTTP 注册、使用同一 `WebRequestSession` 登录、调用 `/api/v1/auth/me`、退出。断言登录后的 `/me` 邮箱正确，退出后同一会话调用 `/me` 为固定 401。最后从 `DATABASE_URL` 读取 Uvicorn 实际使用的开发库连接；若使用 SQLAlchemy 的 `postgresql+psycopg://` 方言前缀，转换为原生 psycopg 所需的 `postgresql://` 后，仅执行按该精确邮箱匹配的 `DELETE FROM users WHERE email = :email`。随后停止该 Uvicorn 进程。清理或停止失败时不得声称烟雾测试通过。

- [ ] **Step 4: 在全部验证通过后更新 README 当前阶段**

将 `README.md` 中“当前阶段”改为：Task 0–5 已完成；Task 5 包含 `/api/v1/auth/me` 与 Cookie JWT 的可复用当前用户依赖；下一步是 Task 6 的产品空间 API 并必须按当前用户 `id` 隔离查询。不得新增 Task 6 的实现说明或前端内容。

- [ ] **Step 5: 复跑 README 相关全量质量门禁并提交完成记录**

```powershell
cd services/api
.\.venv\Scripts\python.exe -m ruff check --no-cache .
.\.venv\Scripts\python.exe -m ruff format --check --no-cache .
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider -q
.\.venv\Scripts\python.exe -m pip check
cd ../..
git status --short --branch
git add README.md
git commit -m "docs: record Task 5 completion"
```

Expected: 所有质量门禁通过，且最终提交只包含 `README.md`；提交前确认没有 `.env` 或任何密钥文件被暂存。

## 实施后验收清单

- [ ] `GET /api/v1/auth/me` 成功时返回现有 `UserResponse` 的全部公开字段，绝不返回密码、密码哈希或 JWT。
- [ ] Cookie 名称严格使用 `settings.auth_cookie_name`；JWT 严格以 `algorithms=["HS256"]` 解码。
- [ ] 缺失、过期、篡改、格式异常、缺失/非法 `sub` 及用户不存在均返回完全相同的 401 `UNAUTHORIZED` 响应。
- [ ] 缺失或弱 `JWT_SECRET` 仍是明确的服务端配置错误，不被转换为 401。
- [ ] `get_current_user` 不写 Cookie、不写入数据库、不提交事务、不记录 Token；probe 证明其能供后续路由复用。
- [ ] pytest 与 Alembic 检查串行执行；最终完成 Ruff、格式、pytest、pip、Alembic 和真实 Uvicorn Cookie 会话验证。
