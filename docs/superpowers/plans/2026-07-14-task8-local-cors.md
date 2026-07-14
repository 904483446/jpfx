# Task 8 Local CORS Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 允许本地 Next.js 前端安全地携带 httpOnly Cookie 调用 FastAPI 认证接口。

**Architecture:** 允许来源由 `Settings` 的非敏感逗号分隔配置项提供，默认只有 `http://127.0.0.1:3000`。应用工厂注册严格的 `CORSMiddleware`；应用级测试验证允许来源和未知来源，不修改认证路由或前端代理。

**Tech Stack:** FastAPI、Starlette CORSMiddleware、Pydantic Settings、pytest、FastAPI TestClient。

---

### Task 1：以 TDD 添加受限 CORS 配置

**Files:**

- Create: `services/api/tests/test_cors.py`
- Modify: `services/api/app/core/config.py`
- Modify: `services/api/app/main.py`

- [ ] **Step 1：写失败的应用级 CORS 测试**

创建 `services/api/tests/test_cors.py`，用 `monkeypatch` 将 `settings.cors_allowed_origins` 设为 `"http://127.0.0.1:3000"`，然后针对 `create_app()` 写入：

```python
from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import create_app


def test_allowed_origin_receives_credentialed_preflight_headers(monkeypatch):
    monkeypatch.setattr(settings, "cors_allowed_origins", "http://127.0.0.1:3000")
    client = TestClient(create_app())
    response = client.options(
        "/api/v1/auth/login",
        headers={
            "Origin": "http://127.0.0.1:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://127.0.0.1:3000"
    assert response.headers["access-control-allow-credentials"] == "true"
    assert "POST" in response.headers["access-control-allow-methods"]
    assert response.headers["access-control-allow-headers"] == "Content-Type"


def test_unknown_origin_does_not_receive_allow_origin_header(monkeypatch):
    monkeypatch.setattr(settings, "cors_allowed_origins", "http://127.0.0.1:3000")
    client = TestClient(create_app())
    response = client.options(
        "/api/v1/auth/login",
        headers={
            "Origin": "http://evil.example",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert "access-control-allow-origin" not in response.headers
```

- [ ] **Step 2：运行失败测试**

```powershell
cd services/api
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider -q tests/test_cors.py
```

预期：允许来源测试失败，因为当前应用未注册 CORS 中间件。

- [ ] **Step 3：添加最小配置与中间件**

在 `Settings` 添加：

```python
cors_allowed_origins: str = "http://127.0.0.1:3000"

@property
def cors_origins(self) -> list[str]:
    return [origin.strip() for origin in self.cors_allowed_origins.split(",") if origin.strip()]
```

在 `create_app()` 中、异常处理器和路由注册之前添加：

```python
from fastapi.middleware.cors import CORSMiddleware

application.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)
```

- [ ] **Step 4：运行通过测试与后端回归**

```powershell
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider -q tests/test_cors.py
.\.venv\Scripts\python.exe -m ruff check --no-cache .
.\.venv\Scripts\python.exe -m ruff format --check --no-cache .
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider -q
```

预期：CORS 测试和既有后端测试通过。

- [ ] **Step 5：提交最小 CORS 配置**

```powershell
git add services/api/app/core/config.py services/api/app/main.py services/api/tests/test_cors.py
git commit -m "feat: allow local credentialed frontend requests"
```

### Task 2：完整跨端验证与文档校准

**Files:**

- Modify: `README.md`

- [ ] **Step 1：更新环境变量示例说明**

README 说明 `CORS_ALLOWED_ORIGINS=http://127.0.0.1:3000` 是非敏感后端配置；生产环境必须替换为实际前端 HTTPS Origin，不能使用 `*`。

- [ ] **Step 2：运行完整回归验证**

```powershell
cd services/api
.\.venv\Scripts\python.exe -m ruff check --no-cache .
.\.venv\Scripts\python.exe -m ruff format --check --no-cache .
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider -q
.\.venv\Scripts\python.exe -m pip check

cd ..\..\apps\web
npm.cmd run test
npm.cmd run check:routes
npm.cmd exec tsc -- --noEmit
npm.cmd run lint
npm.cmd run build
npm.cmd audit --omit=dev
```

预期：所有自动化验证通过，生产依赖审计为 0 vulnerabilities。

- [ ] **Step 3：在已配置本地环境中运行浏览器烟雾验证**

启动后端与前端后，在浏览器验证注册跳转登录、登录进入 `/app`、刷新保持会话、无 Cookie 访问 `/app` 跳转登录；Network 不出现 `/spaces`，存储中没有 JWT。若本地服务、数据库或非敏感环境配置不可用，记录实际阻塞，不伪造通过结果。

- [ ] **Step 4：提交文档说明**

```powershell
git add README.md
git commit -m "docs: document local auth CORS setup"
```

## 计划自检

- CORS 允许来源、凭据、方法、请求头、未知来源拒绝和浏览器联调均有对应步骤。
- 计划不涉及 Cookie/JWT 内容、认证路由、前端代理、空间 API 或部署改造。
