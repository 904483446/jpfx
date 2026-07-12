# Task 6：产品空间基础接口 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为当前登录用户提供产品空间列表、创建和详情接口，并在创建时原子生成默认知识库。

**Architecture:** 路由只注入 `get_current_user` 和同步数据库会话；Schema 负责输入规范化与公开输出；服务层始终以 `current_user.id` 过滤查询，并在单一事务中创建 `Space` 与 `KnowledgeBase`。跨用户、软删除和不存在空间都使用相同的 404。

**Tech Stack:** FastAPI、Pydantic v2、同步 SQLAlchemy 2、PostgreSQL、pytest、Ruff。

---

## 文件边界

- Create: `services/api/app/schemas/space.py` — 创建请求与公开空间响应。
- Create: `services/api/app/services/space_service.py` — 用户隔离查询和原子创建。
- Create: `services/api/app/api/v1/spaces.py` — 三个受保护 API 路由。
- Create: `services/api/tests/test_space_schemas.py` — Schema 规范化与校验。
- Create: `services/api/tests/test_space_service.py` — 服务层隔离、排序、事务。
- Create: `services/api/tests/test_spaces.py` — Cookie API 集成测试。
- Modify: `services/api/app/core/errors.py` — `space_not_found()` 统一业务错误。
- Modify: `services/api/app/main.py` — 注册 spaces router。
- Modify: `README.md` — 仅在所有验证通过后记录 Task 6 完成。

### Task 1：空间 Schema 与统一 404 错误

**Files:**

- Create: `services/api/app/schemas/space.py`
- Create: `services/api/tests/test_space_schemas.py`
- Modify: `services/api/app/core/errors.py`
- Modify: `services/api/tests/test_app_errors.py`

- [ ] **Step 1: 写失败测试**

```python
def test_space_create_normalizes_optional_fields_to_none():
    payload = SpaceCreateRequest(
        name="  企业知识库 Copilot  ",
        industry="  ",
        product_direction=" AI 知识库 ",
        description="  ",
    )
    assert payload.name == "企业知识库 Copilot"
    assert payload.industry is None
    assert payload.product_direction == "AI 知识库"
    assert payload.description is None


def test_space_not_found_has_fixed_public_contract():
    error = space_not_found()
    assert (error.status_code, error.code, error.message, error.details) == (
        404, "SPACE_NOT_FOUND", "产品空间不存在", {}
    )
```

另以 `pytest.mark.parametrize` 覆盖 `name="   "`、`name="x" * 201`、`industry="x" * 201` 与 `product_direction="x" * 201`，断言 `pydantic.ValidationError`。

- [ ] **Step 2: 验证 RED**

Run: `cd services/api; D:\Codex_project\jpfx\services\api\.venv\Scripts\python.exe -m pytest -p no:cacheprovider -q tests/test_space_schemas.py tests/test_app_errors.py`

Expected: FAIL，`app.schemas.space` 与 `space_not_found` 尚不存在。

- [ ] **Step 3: 实现最小 Schema 与错误工厂**

```python
# app/schemas/space.py
from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


def normalize_optional_text(value: Any) -> Any:
    return value.strip() or None if isinstance(value, str) else value


class SpaceCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    industry: str | None = Field(default=None, max_length=200)
    product_direction: str | None = Field(default=None, max_length=200)
    description: str | None = None

    @field_validator("name", mode="before")
    @classmethod
    def normalize_name(cls, value: Any) -> Any:
        return value.strip() if isinstance(value, str) else value

    @field_validator("industry", "product_direction", "description", mode="before")
    @classmethod
    def normalize_optional_fields(cls, value: Any) -> Any:
        return normalize_optional_text(value)


class SpaceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    industry: str | None
    product_direction: str | None
    description: str | None
    created_at: datetime
    updated_at: datetime
```

```python
# app/core/errors.py，追加
def space_not_found() -> AppError:
    return AppError(status_code=404, code="SPACE_NOT_FOUND", message="产品空间不存在")
```

- [ ] **Step 4: 验证 GREEN 并提交**

Run: `cd services/api; D:\Codex_project\jpfx\services\api\.venv\Scripts\python.exe -m pytest -p no:cacheprovider -q tests/test_space_schemas.py tests/test_app_errors.py`

Expected: PASS。

```powershell
git add services/api/app/schemas/space.py services/api/app/core/errors.py services/api/tests/test_space_schemas.py services/api/tests/test_app_errors.py
git commit -m "feat: define space API schemas"
```

### Task 2：隔离查询与原子空间创建服务

**Files:**

- Create: `services/api/app/services/space_service.py`
- Create: `services/api/tests/test_space_service.py`

- [ ] **Step 1: 写失败测试**

测试以真实 `database_session` 创建用户 A、B，并断言：A 创建的空间同时有唯一的 `KnowledgeBase(name="默认知识库")`；列表只含 A 的空间且按 `created_at.desc()`；A 获取 B 的空间、随机 UUID 和 `deleted_at` 非空空间时均抛出 `SPACE_NOT_FOUND`。另用 `monkeypatch.setattr(database_session, "commit", failing_commit)` 模拟提交抛出 `IntegrityError`，断言调用 `rollback()` 且重新查询不到空间。

- [ ] **Step 2: 验证 RED**

Run: `cd services/api; D:\Codex_project\jpfx\services\api\.venv\Scripts\python.exe -m pytest -p no:cacheprovider -q tests/test_space_service.py`

Expected: FAIL，`app.services.space_service` 尚不存在。

- [ ] **Step 3: 实现最小服务层**

```python
# app/services/space_service.py
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import space_not_found
from app.models import KnowledgeBase, Space, User
from app.schemas.space import SpaceCreateRequest

DEFAULT_KNOWLEDGE_BASE_NAME = "默认知识库"


def list_spaces(database_session: Session, user: User) -> list[Space]:
    return list(database_session.scalars(
        select(Space).where(Space.user_id == user.id, Space.deleted_at.is_(None)).order_by(Space.created_at.desc())
    ))


def get_space(database_session: Session, user: User, space_id: UUID) -> Space:
    space = database_session.scalar(select(Space).where(
        Space.id == space_id, Space.user_id == user.id, Space.deleted_at.is_(None)
    ))
    if space is None:
        raise space_not_found()
    return space


def create_space(database_session: Session, user: User, payload: SpaceCreateRequest) -> Space:
    space = Space(user_id=user.id, **payload.model_dump())
    database_session.add(space)
    try:
        database_session.flush()
        database_session.add(KnowledgeBase(user_id=user.id, space_id=space.id, name=DEFAULT_KNOWLEDGE_BASE_NAME))
        database_session.commit()
    except IntegrityError:
        database_session.rollback()
        raise
    database_session.refresh(space)
    return space
```

- [ ] **Step 4: 验证 GREEN 并提交**

Run: `cd services/api; D:\Codex_project\jpfx\services\api\.venv\Scripts\python.exe -m pytest -p no:cacheprovider -q tests/test_space_service.py`

Expected: PASS。

```powershell
git add services/api/app/services/space_service.py services/api/tests/test_space_service.py
git commit -m "feat: add isolated space service"
```

### Task 3：受保护的 spaces API

**Files:**

- Create: `services/api/app/api/v1/spaces.py`
- Create: `services/api/tests/test_spaces.py`
- Modify: `services/api/app/main.py`

- [ ] **Step 1: 写失败 API 测试**

测试 fixture 覆盖 `get_db_session`，预置用户并用 `create_access_token` 写入 `settings.auth_cookie_name`。覆盖：未认证的三个接口均为固定 401；`POST /api/v1/spaces` 返回 201 且没有 `user_id`/`deleted_at`；创建后 `GET /spaces` 可见；`GET /spaces/{id}` 可见；用户 A 读取 B 返回固定 404；非法 UUID 返回 422。

- [ ] **Step 2: 验证 RED**

Run: `cd services/api; D:\Codex_project\jpfx\services\api\.venv\Scripts\python.exe -m pytest -p no:cacheprovider -q tests/test_spaces.py`

Expected: FAIL 或 404，spaces router 尚未注册。

- [ ] **Step 3: 实现路由并注册**

```python
# app/api/v1/spaces.py
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db_session
from app.models import User
from app.schemas.space import SpaceCreateRequest, SpaceResponse
from app.services.space_service import create_space, get_space, list_spaces

router = APIRouter(prefix="/spaces", tags=["spaces"])

@router.get("", response_model=list[SpaceResponse])
def list_current_user_spaces(current_user: Annotated[User, Depends(get_current_user)], database_session: Annotated[Session, Depends(get_db_session)]) -> list[SpaceResponse]:
    return [SpaceResponse.model_validate(space) for space in list_spaces(database_session, current_user)]

@router.post("", response_model=SpaceResponse, status_code=status.HTTP_201_CREATED)
def create_current_user_space(payload: SpaceCreateRequest, current_user: Annotated[User, Depends(get_current_user)], database_session: Annotated[Session, Depends(get_db_session)]) -> SpaceResponse:
    return SpaceResponse.model_validate(create_space(database_session, current_user, payload))

@router.get("/{space_id}", response_model=SpaceResponse)
def get_current_user_space(space_id: UUID, current_user: Annotated[User, Depends(get_current_user)], database_session: Annotated[Session, Depends(get_db_session)]) -> SpaceResponse:
    return SpaceResponse.model_validate(get_space(database_session, current_user, space_id))
```

在 `app/main.py` 导入 `spaces_router`，并执行：

```python
application.include_router(spaces_router, prefix=settings.api_v1_prefix)
```

- [ ] **Step 4: 验证 GREEN 与认证回归，并提交**

Run: `cd services/api; D:\Codex_project\jpfx\services\api\.venv\Scripts\python.exe -m pytest -p no:cacheprovider -q tests/test_spaces.py tests/test_auth_me.py tests/test_auth_dependencies.py`

Expected: PASS。

```powershell
git add services/api/app/api/v1/spaces.py services/api/app/main.py services/api/tests/test_spaces.py
git commit -m "feat: add protected spaces API"
```

### Task 4：文档与完成验证

**Files:**

- Modify: `README.md`

- [ ] **Step 1: 运行串行质量门禁**

```powershell
cd services/api
D:\Codex_project\jpfx\services\api\.venv\Scripts\python.exe -m ruff check --no-cache .
D:\Codex_project\jpfx\services\api\.venv\Scripts\python.exe -m ruff format --check --no-cache .
D:\Codex_project\jpfx\services\api\.venv\Scripts\python.exe -m pytest -p no:cacheprovider -q
D:\Codex_project\jpfx\services\api\.venv\Scripts\python.exe -m pip check
```

Expected: 所有命令退出码 0；pytest 不与下一步 Alembic 并行。

- [ ] **Step 2: 串行运行 Alembic 检查并进行 Uvicorn 冒烟**

使用 `Settings().test_database_url` 调用 `alembic.command.check()`，预期输出 `ALEMBIC_CHECK=ok`。随后启动 Uvicorn，以唯一邮箱注册、登录、创建空间、读取空间、退出；断言退出后读取空间为固定 401。最后按精确邮箱删除唯一烟雾用户并停止服务。

- [ ] **Step 3: 更新 README、复跑门禁并提交**

将当前阶段更新为 Task 0–6 已完成，下一步 Task 7；增加“受鉴权保护的空间列表、创建、详情与默认知识库创建”说明。复跑 Task 4 Step 1 的四项命令。

```powershell
git add README.md
git commit -m "docs: record Task 6 completion"
```

## 验收清单

- [ ] 仅实现三个确认的 spaces 接口。
- [ ] 所有空间查询固定按当前用户 `id` 过滤，跨用户与不存在统一 404。
- [ ] 创建空间与默认知识库原子完成。
- [ ] 不暴露 `user_id`、`deleted_at` 或知识库详情。
- [ ] 无迁移、无前端、无 PATCH/DELETE、无后续产品功能。
