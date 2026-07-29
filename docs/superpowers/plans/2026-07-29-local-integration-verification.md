# 本地真实集成验证 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为当前 `main` 提供 Docker、Alembic、API 与真实浏览器 Cookie/CORS/退出闭环的可复现本地验证记录。

**Architecture:** 验证复用仓库已有的 Docker Compose、Alembic 与 FastAPI 健康端点，只读取状态和退出码。浏览器验证使用已有普通本地 Chrome 会话，不读取凭据或浏览器存储；所有证据汇总到一份 handoff，失败只记录原因，不直接改代码。

**Tech Stack:** Docker Compose、PostgreSQL、pgvector、Alembic、FastAPI、Next.js、Chrome、PowerShell。

---

## 文件结构

- Create: `docs/superpowers/handoffs/2026-07-29-local-integration-verification.md` — 命令、浏览器可见结果、阻塞项和明确的验证边界。
- Modify: 无业务代码、迁移、依赖或环境文件。

### Task 1: 验证 Docker 与数据库服务

**Files:**
- Create: `docs/superpowers/handoffs/2026-07-29-local-integration-verification.md`

- [x] **Step 1: 读取 Docker daemon 和 Compose 当前状态**

  从仓库根目录运行：

  ```powershell
  docker version --format '{{.Server.Version}}'
  docker compose ps
  ```

  预期：Docker daemon 可访问；若 `db` 已运行，记录其 health。若命令因权限或 daemon
  不可用失败，记录原始错误类别，停止 Task 1，不修改项目代码。

- [x] **Step 2: 仅在 db 未运行时启动现有服务**

  从仓库根目录运行：

  ```powershell
  docker compose up -d --wait db
  docker compose ps db
  ```

  预期：`db` 显示 healthy。不得运行 `docker compose down`、`down -v`、`rm`、`prune`
  或任何删除卷/容器的命令。

- [x] **Step 3: 记录数据库服务结论**

  在 handoff 中填写 Docker 命令、退出码、`db` 状态及是否执行了启动命令；不复制容器
  环境变量、数据库 URL 或 `.env` 内容。

### Task 2: 验证 Alembic 与 FastAPI 健康端点

**Files:**
- Create: `docs/superpowers/handoffs/2026-07-29-local-integration-verification.md`

- [x] **Step 1: 向当前迁移 head 升级**

  从 `services/api` 运行：

  ```powershell
  .\.venv\Scripts\python.exe -m alembic upgrade head
  ```

  预期：退出码 0。此命令只应用缺失迁移；不得使用 Alembic downgrade。

- [x] **Step 2: 读取当前迁移版本**

  从 `services/api` 运行：

  ```powershell
  .\.venv\Scripts\python.exe -m alembic current
  ```

  预期：输出当前 revision；将 revision 标识记入 handoff，不记录数据库连接信息。

- [x] **Step 3: 验证 API 健康端点**

  在 FastAPI 服务已运行时执行：

  ```powershell
  Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8000/api/v1/health
  ```

  预期：HTTP 200。若服务未运行，仅按 README 启动既有 uvicorn 命令；若无法启动，记录
  失败并停止，不改代码。

### Task 3: 验证普通 Chrome 的 Cookie/CORS 与退出闭环

**Files:**
- Create: `docs/superpowers/handoffs/2026-07-29-local-integration-verification.md`

- [x] **Step 1: 验证受保护应用页和跨域请求**

  在普通本地 Chrome 打开 `http://127.0.0.1:3000/app`，检查页面可用且开发者控制台没有
  CORS 或网络错误。再打开 `/app/spaces` 和 `/app/tasks`，只记录空态或可访问状态；不
  读取、复制或截图账户资料、Cookie 或业务内容。

- [x] **Step 2: 验证退出登录**

  点击产品 UI 的退出登录控制，确认可见地址进入 `/login`。不得使用 DevTools、脚本或
  Cookie 存储手动删除会话来替代该操作。

- [x] **Step 3: 验证退出后的受保护路由拦截**

  在同一 Chrome 直接打开 `http://127.0.0.1:3000/app`。

  预期：页面重定向或拒绝访问并回到 `/login`。若没有既有会话，暂停并请用户自行登录，
  不索取任何认证信息。

### Task 4: 汇总证据、核对边界并提交结果记录

**Files:**
- Create: `docs/superpowers/handoffs/2026-07-29-local-integration-verification.md`

- [x] **Step 1: 写入固定结果格式**

  handoff 使用如下章节并逐项填写实际结果：

  ```md
  ## Docker 与数据库
  ## Alembic 与 API
  ## 浏览器 Cookie/CORS 与退出
  ## 未验证边界
  ## 结论与后续
  ```

  每个通过项必须含命令/可见状态；失败项必须含实际阻塞；未验证边界必须继续列出真实
  Provider、部署、CI 和未执行的项目。

- [x] **Step 2: 自查记录与差异**

  从仓库根目录运行：

  ```powershell
  git diff --check main...HEAD
  git status --short --branch
  ```

  预期：代码、迁移、依赖和环境文件没有变化；仅有设计、计划和 handoff 文档。

- [x] **Step 3: 提交验证记录**

  ```powershell
  git add docs/superpowers/handoffs/2026-07-29-local-integration-verification.md
  git commit -m "docs: record local integration verification"
  ```

  预期：提交只包含验证记录；若验证被环境阻塞，仍如实提交阻塞证据，不把阻塞表述为通过。
