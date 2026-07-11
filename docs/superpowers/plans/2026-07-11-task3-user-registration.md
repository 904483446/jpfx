# Task 3 User Registration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现 `POST /api/v1/auth/register`，使用 Argon2id 安全保存密码，并对重复邮箱和无效输入返回统一中文错误。

**Architecture:** FastAPI 路由只负责 HTTP 契约和依赖注入，Pydantic Schema 负责规范化与校验，服务层负责注册事务，安全模块封装 Argon2id。数据库唯一约束是并发注册的最终保护，业务异常处理器统一转换为公开错误结构。

**Tech Stack:** FastAPI、Pydantic v2、SQLAlchemy 2、PostgreSQL、pwdlib/Argon2id、pytest、Ruff

---

### Task 1: 密码哈希依赖与安全模块

**Files:**
- Modify: `services/api/pyproject.toml`
- Create: `services/api/app/core/security.py`
- Create: `services/api/tests/test_security.py`

- [ ] **Step 1: 添加运行依赖**

在 `[project].dependencies` 增加：

```toml
"pwdlib[argon2]>=0.3.0,<1.0.0",
"email-validator>=2.2.0,<3.0.0",
```

运行：

```powershell
cd services/api
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

预期：安装成功，`pip check` 无错误。

- [ ] **Step 2: 编写密码模块失败测试**

创建 `tests/test_security.py`：

```python
import importlib


def test_hash_password_uses_argon2_and_verifies_plain_password():
    security = importlib.import_module("app.core.security")

    encoded = security.hash_password("correct-password")

    assert encoded != "correct-password"
    assert encoded.startswith("$argon2")
    assert security.verify_password("correct-password", encoded) is True
    assert security.verify_password("wrong-password", encoded) is False
```

- [ ] **Step 3: 运行测试确认 RED**

```powershell
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider tests/test_security.py -q
```

预期：因 `app.core.security` 不存在而 FAIL。

- [ ] **Step 4: 实现最小安全模块**

创建 `app/core/security.py`：

```python
from pwdlib import PasswordHash


password_hash = PasswordHash.recommended()


def hash_password(plain_password: str) -> str:
    return password_hash.hash(plain_password)


def verify_password(plain_password: str, encoded_password: str) -> bool:
    return password_hash.verify(plain_password, encoded_password)
```

- [ ] **Step 5: 运行测试确认 GREEN**

```powershell
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider tests/test_security.py -q
```

预期：`1 passed`。

- [ ] **Step 6: 提交**

```powershell
git add services/api/pyproject.toml services/api/app/core/security.py services/api/tests/test_security.py
git commit -m "feat: add Argon2 password security"
```

---

### Task 2: 可复用业务异常

**Files:**
- Modify: `services/api/app/core/errors.py`
- Modify: `services/api/app/main.py`
- Create: `services/api/tests/test_app_errors.py`

- [ ] **Step 1: 编写业务异常失败测试**

创建 `tests/test_app_errors.py`：

```python
from fastapi.testclient import TestClient

from app.main import create_app


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
```

- [ ] **Step 2: 运行测试确认 RED**

```powershell
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider tests/test_app_errors.py -q
```

预期：导入 `AppError` 失败。

- [ ] **Step 3: 实现异常类型和处理器**

在 `app/core/errors.py` 增加：

```python
class AppError(Exception):
    def __init__(
        self,
        *,
        status_code: int,
        code: str,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details or {}


async def app_exception_handler(request: Request, exc: AppError) -> JSONResponse:
    return error_response(
        status_code=exc.status_code,
        code=exc.code,
        message=exc.message,
        details=exc.details,
    )
```

在 `create_app()` 中、通用 `Exception` 处理器之前注册：

```python
application.add_exception_handler(AppError, app_exception_handler)
```

- [ ] **Step 4: 运行测试确认 GREEN**

```powershell
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider tests/test_app_errors.py tests/test_health.py -q
```

预期：业务异常和现有错误测试全部通过。

- [ ] **Step 5: 提交**

```powershell
git add services/api/app/core/errors.py services/api/app/main.py services/api/tests/test_app_errors.py
git commit -m "feat: add reusable application errors"
```

---

### Task 3: 注册请求与响应 Schema

**Files:**
- Create: `services/api/app/schemas/__init__.py`
- Create: `services/api/app/schemas/auth.py`
- Create: `services/api/tests/test_auth_schemas.py`

- [ ] **Step 1: 编写 Schema 失败测试**

创建 `tests/test_auth_schemas.py`：

```python
import importlib

import pytest
from pydantic import ValidationError


def register_request_type():
    return importlib.import_module("app.schemas.auth").RegisterRequest


def test_register_request_normalizes_email_and_display_name():
    payload = register_request_type()(
        email="  User@Example.COM  ",
        password="valid-password",
        display_name="  示例用户  ",
    )

    assert str(payload.email) == "user@example.com"
    assert payload.display_name == "示例用户"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("email", ""),
        ("email", "not-an-email"),
        ("password", "short"),
        ("password", "x" * 129),
        ("display_name", "   "),
        ("display_name", "名" * 101),
    ],
)
def test_register_request_rejects_invalid_fields(field: str, value: str):
    data = {
        "email": "user@example.com",
        "password": "valid-password",
        "display_name": "示例用户",
    }
    data[field] = value

    with pytest.raises(ValidationError):
        register_request_type()(**data)
```

- [ ] **Step 2: 运行测试确认 RED**

```powershell
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider tests/test_auth_schemas.py -q
```

预期：`app.schemas.auth` 不存在。

- [ ] **Step 3: 实现 Schema**

创建 `app/schemas/auth.py`：

```python
from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    display_name: str = Field(min_length=1, max_length=100)

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value: Any) -> Any:
        if isinstance(value, str):
            return value.strip().lower()
        return value

    @field_validator("display_name", mode="before")
    @classmethod
    def normalize_display_name(cls, value: Any) -> Any:
        if isinstance(value, str):
            return value.strip()
        return value


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    display_name: str
    is_admin: bool
    created_at: datetime
    updated_at: datetime
```

创建空的 `app/schemas/__init__.py`。

- [ ] **Step 4: 运行测试确认 GREEN**

```powershell
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider tests/test_auth_schemas.py -q
```

预期：规范化测试和 6 个无效输入测试通过。

- [ ] **Step 5: 提交**

```powershell
git add services/api/app/schemas services/api/tests/test_auth_schemas.py
git commit -m "feat: define registration schemas"
```

---

### Task 4: 注册服务和并发唯一约束处理

**Files:**
- Create: `services/api/app/services/__init__.py`
- Create: `services/api/app/services/auth_service.py`
- Create: `services/api/tests/conftest.py`
- Create: `services/api/tests/test_auth_service.py`

- [ ] **Step 1: 创建隔离数据库 Fixture**

创建 `tests/conftest.py`：

```python
from collections.abc import Generator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.config import Settings


API_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def database_session() -> Generator[Session, None, None]:
    database_url = Settings().test_database_url
    assert database_url is not None
    configuration = Config(str(API_ROOT / "alembic.ini"))
    configuration.set_main_option("sqlalchemy.url", database_url)
    command.upgrade(configuration, "head")

    engine = create_engine(database_url)
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(
        bind=connection,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )
    try:
        yield session
    finally:
        session.close()
        if transaction.is_active:
            transaction.rollback()
        connection.close()
        engine.dispose()
```

- [ ] **Step 2: 编写服务层失败测试**

创建 `tests/test_auth_service.py`，使用现有测试数据库和事务回滚，覆盖：

```python
import importlib

from app.core.security import verify_password
from app.schemas.auth import RegisterRequest


def test_register_user_persists_normalized_user(database_session):
    register_user = importlib.import_module(
        "app.services.auth_service"
    ).register_user
    user = register_user(
        database_session,
        RegisterRequest(
            email="User@Example.com",
            password="valid-password",
            display_name="示例用户",
        ),
    )

    assert user.email == "user@example.com"
    assert user.password_hash != "valid-password"
    assert verify_password("valid-password", user.password_hash)
```

同文件增加：

```python
def test_register_user_rejects_existing_email(database_session):
    register_user = importlib.import_module(
        "app.services.auth_service"
    ).register_user
    payload = RegisterRequest(
        email="duplicate@example.com",
        password="valid-password",
        display_name="用户一",
    )
    register_user(database_session, payload)

    with pytest.raises(AppError) as captured:
        register_user(database_session, payload.model_copy(update={"display_name": "用户二"}))

    assert captured.value.status_code == 409
    assert captured.value.code == "EMAIL_ALREADY_REGISTERED"
```

同文件加入并发唯一约束测试辅助类型：

```python
class FakeDiagnostic:
    def __init__(self, constraint_name: str) -> None:
        self.constraint_name = constraint_name


class FakeDatabaseError(Exception):
    def __init__(self, constraint_name: str) -> None:
        self.diag = FakeDiagnostic(constraint_name)


def integrity_error(constraint_name: str) -> IntegrityError:
    return IntegrityError(
        "INSERT INTO users",
        {},
        FakeDatabaseError(constraint_name),
    )
```

使用以下两个测试验证竞争错误：

```python
from unittest.mock import create_autospec

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import AppError


def registration_payload() -> RegisterRequest:
    return RegisterRequest(
        email="race@example.com",
        password="valid-password",
        display_name="竞争测试用户",
    )


def test_register_user_converts_email_unique_race_to_app_error():
    register_user = importlib.import_module(
        "app.services.auth_service"
    ).register_user
    session = create_autospec(Session, instance=True)
    session.scalar.return_value = None
    session.commit.side_effect = integrity_error("uq_users_email")

    with pytest.raises(AppError) as captured:
        register_user(session, registration_payload())

    assert captured.value.status_code == 409
    assert captured.value.code == "EMAIL_ALREADY_REGISTERED"
    session.rollback.assert_called_once_with()


def test_register_user_reraises_unrelated_integrity_error():
    register_user = importlib.import_module(
        "app.services.auth_service"
    ).register_user
    session = create_autospec(Session, instance=True)
    session.scalar.return_value = None
    unexpected = integrity_error("other_constraint")
    session.commit.side_effect = unexpected

    with pytest.raises(IntegrityError) as captured:
        register_user(session, registration_payload())

    assert captured.value is unexpected
    session.rollback.assert_called_once_with()
```

- [ ] **Step 3: 运行测试确认 RED**

```powershell
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider tests/test_auth_service.py -q
```

预期：`app.services.auth_service` 不存在。

- [ ] **Step 4: 实现注册服务**

创建 `app/services/auth_service.py`：

```python
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.core.security import hash_password
from app.models import User
from app.schemas.auth import RegisterRequest


EMAIL_UNIQUE_CONSTRAINT = "uq_users_email"


def email_already_registered() -> AppError:
    return AppError(
        status_code=409,
        code="EMAIL_ALREADY_REGISTERED",
        message="该邮箱已注册",
    )


def integrity_constraint_name(exc: IntegrityError) -> str | None:
    diagnostic = getattr(exc.orig, "diag", None)
    return getattr(diagnostic, "constraint_name", None)


def register_user(database_session: Session, payload: RegisterRequest) -> User:
    email = str(payload.email)
    existing_user = database_session.scalar(select(User).where(User.email == email))
    if existing_user is not None:
        raise email_already_registered()

    user = User(
        email=email,
        password_hash=hash_password(payload.password),
        display_name=payload.display_name,
    )
    database_session.add(user)
    try:
        database_session.commit()
    except IntegrityError as exc:
        database_session.rollback()
        if integrity_constraint_name(exc) == EMAIL_UNIQUE_CONSTRAINT:
            raise email_already_registered() from exc
        raise

    database_session.refresh(user)
    return user
```

创建空的 `app/services/__init__.py`。

- [ ] **Step 5: 运行服务测试确认 GREEN**

```powershell
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider tests/test_auth_service.py -q
```

预期：正常注册、预查询重复、并发唯一约束和非目标约束测试全部通过。

- [ ] **Step 6: 提交**

```powershell
git add services/api/app/services services/api/tests/conftest.py services/api/tests/test_auth_service.py
git commit -m "feat: add user registration service"
```

---

### Task 5: 注册 API 集成

**Files:**
- Create: `services/api/app/api/v1/auth.py`
- Modify: `services/api/app/main.py`
- Create: `services/api/tests/test_auth_register.py`

- [ ] **Step 1: 创建真实数据库 API 测试夹具**

在 `test_auth_register.py` 中复用 `database_session`，并创建：

```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.main import app


@pytest.fixture
def client(database_session: Session):
    def override_database_session():
        yield database_session

    app.dependency_overrides[get_db_session] = override_database_session
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
```

`database_session` 的外层事务会在测试结束后回滚，即使注册服务内部调用 `commit()` 也不会污染测试库。

- [ ] **Step 2: 编写 API 失败测试**

成功路径：

```python
def test_register_returns_created_user_without_password(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "  ApiUser@Example.com  ",
            "password": "valid-password",
            "display_name": "  API 用户  ",
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["email"] == "apiuser@example.com"
    assert payload["display_name"] == "API 用户"
    assert payload["is_admin"] is False
    assert "password" not in payload
    assert "password_hash" not in payload
```

重复路径：

```python
def test_register_rejects_case_insensitive_duplicate(client):
    first = {
        "email": "duplicate@example.com",
        "password": "valid-password",
        "display_name": "用户一",
    }
    assert client.post("/api/v1/auth/register", json=first).status_code == 201

    second = {**first, "email": "  DUPLICATE@EXAMPLE.COM  ", "display_name": "用户二"}
    response = client.post("/api/v1/auth/register", json=second)

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "EMAIL_ALREADY_REGISTERED"
    assert response.json()["error"]["message"] == "该邮箱已注册"
```

参数化覆盖空/非法邮箱、短/超长密码、空/超长昵称，断言 422、`VALIDATION_ERROR` 和中文外层消息。

- [ ] **Step 3: 运行测试确认 RED**

```powershell
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider tests/test_auth_register.py -q
```

预期：注册路由返回 404。

- [ ] **Step 4: 实现路由并注册**

创建 `app/api/v1/auth.py`：

```python
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.schemas.auth import RegisterRequest, UserResponse
from app.services.auth_service import register_user


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    payload: RegisterRequest,
    database_session: Session = Depends(get_db_session),
) -> UserResponse:
    return UserResponse.model_validate(register_user(database_session, payload))
```

在 `create_app()` 中以 `settings.api_v1_prefix` 包含 `auth_router`。

- [ ] **Step 5: 运行 API 与全量测试确认 GREEN**

```powershell
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider tests/test_auth_register.py -q
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider -q
```

预期：注册测试通过，现有测试无回归。

- [ ] **Step 6: 提交**

```powershell
git add services/api/app/api/v1/auth.py services/api/app/main.py services/api/tests/test_auth_register.py
git commit -m "feat: add user registration endpoint"
```

---

### Task 6: 文档与最终质量门禁

**Files:**
- Modify: `README.md`

- [ ] **Step 1: 更新阶段状态**

将 README 当前阶段更新为 Task 3 已完成、下一步 Task 4；增加注册接口示例，但不加入登录或 Cookie 说明。

- [ ] **Step 2: 串行运行质量门禁**

先确认 `db-test` 健康，然后按顺序执行，避免迁移测试与 Alembic 漂移检查并发修改同一测试库：

```powershell
cd services/api
.\.venv\Scripts\python.exe -m ruff check --no-cache .
.\.venv\Scripts\python.exe -m ruff format --check --no-cache .
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider -q
.\.venv\Scripts\python.exe -m pip check
```

pytest 完成后再执行 Alembic `command.check()`。预期 Ruff、格式、测试、依赖和迁移漂移检查全部通过。

- [ ] **Step 3: 实际启动验证**

启动 Uvicorn，向 `/api/v1/auth/register` 发送唯一邮箱 `task3-smoke@example.com`，验证返回 201；随后连接开发数据库，按该邮箱删除人工验证记录并提交，避免污染开发库。清理前确认只匹配这一条记录。

- [ ] **Step 4: 提交文档**

```powershell
git add README.md
git commit -m "docs: record Task 3 completion"
```

- [ ] **Step 5: 推送功能分支**

```powershell
git push origin feat/v0.1-task3-register
```

预期：本地分支与远程分支同步，工作区干净；不自动合并到 `main`，等待最终审查。
