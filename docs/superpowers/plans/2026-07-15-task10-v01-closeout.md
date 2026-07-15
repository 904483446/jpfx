# V0.1 Task 10 收尾 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在不新增产品功能的前提下，完成 V0.1 的环境示例、README、验证记录与 V0.2 入口说明。

**Architecture:** 变更仅限根目录 `.env.example`、`README.md` 和一份 Task 10 收尾记录。前端在隔离 worktree 中使用已安装的锁定依赖；后端始终从 worktree 源码目录运行，并复用根目录现有虚拟环境解释器。验证结果必须逐项记录，不能把未执行或失败的检查写为通过。

**Tech Stack:** Next.js、TypeScript、Vitest、ESLint、FastAPI、Ruff、Pytest、npm、Python。

---

## 文件结构

| 文件 | 责任 |
| --- | --- |
| `.env.example` | 当前 V0.1 实际使用的变量、用途注释和非敏感占位值。 |
| `README.md` | 当前已交付能力、可复现验证方式、范围边界和 V0.2 起点。 |
| `docs/superpowers/handoffs/2026-07-15-task10-v01-closeout.md` | 实际验证结果、验证边界、未完成事项与下一任务入口。 |

### Task 1：建立完整验证基线

**Files:**
- Modify: 无文件。

- [ ] **Step 1：确认前端单元测试基线**

在 `D:\Codex_project\jpfx\.worktrees\feat-v0.1-task10-v01-closeout\apps\web` 运行：

```powershell
npm.cmd run test
```

预期：Vitest 以退出码 0 完成，当前基线为 7 个测试文件、32 个测试通过。若数量变化，记录实际数量；若失败且为应用回归，停止后续文档宣称并先调查原因。

- [ ] **Step 2：运行其余前端静态与发布检查**

在同一目录运行：

```powershell
npm.cmd run check:routes
npm.cmd exec tsc -- --noEmit
npm.cmd run lint
npm.cmd run build
npm.cmd audit --omit=dev
```

预期：前四条命令均以退出码 0 完成，审计输出 `found 0 vulnerabilities`。任何失败均保存命令和失败摘要，不能在 README 或收尾记录中标记为已通过。

- [ ] **Step 3：运行后端静态与单元检查**

在 `D:\Codex_project\jpfx\.worktrees\feat-v0.1-task10-v01-closeout\services\api` 运行：

```powershell
D:\Codex_project\jpfx\services\api\.venv\Scripts\python.exe -m ruff check --no-cache .
D:\Codex_project\jpfx\services\api\.venv\Scripts\python.exe -m ruff format --check --no-cache .
D:\Codex_project\jpfx\services\api\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
```

预期：命令以退出码 0 完成。若需要数据库或本地服务的测试因环境缺失无法运行，记录实际错误与环境限制；不读取、创建或修改任何真实环境文件来绕过限制。

### Task 2：收敛 `.env.example` 到当前 V0.1 配置

**Files:**
- Modify: `.env.example`

- [ ] **Step 1：替换为当前配置代码实际读取的安全模板**

将 `.env.example` 更新为以下内容：

```dotenv
# Frontend (place in apps/web/.env.local when starting the web app)
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000/api/v1

# Backend authentication and credentialed CORS
JWT_SECRET=replace-with-a-random-secret-of-at-least-32-bytes
ACCESS_TOKEN_EXPIRE_DAYS=7
AUTH_COOKIE_NAME=access_token
AUTH_COOKIE_SECURE=false
CORS_ALLOWED_ORIGINS=http://127.0.0.1:3000

# Local PostgreSQL used by docker-compose.yml
POSTGRES_DB=jpfx
TEST_POSTGRES_DB=jpfx_test
POSTGRES_USER=jpfx
POSTGRES_PASSWORD=change-me-before-local-use
POSTGRES_PORT=5432
TEST_POSTGRES_PORT=5433
DATABASE_URL=postgresql+psycopg://jpfx:change-me-before-local-use@127.0.0.1:5432/jpfx
TEST_DATABASE_URL=postgresql+psycopg://jpfx:change-me-before-local-use@127.0.0.1:5433/jpfx_test
```

此模板只覆盖 `services/api/app/core/config.py` 当前读取的认证、Cookie、CORS 与数据库变量，并保留 Docker Compose 所需的 PostgreSQL 变量。删除未被当前 V0.1 代码读取的 `API_KEY_ENCRYPTION_SECRET`、Supabase、Bocha、DashScope 与本地存储变量。

- [ ] **Step 2：验证模板安全性和配置对齐**

在 worktree 根目录运行：

```powershell
git diff --check -- .env.example
rg -n "CORS_ALLOWED_ORIGINS|JWT_SECRET|DATABASE_URL|TEST_DATABASE_URL" .env.example services/api/app/core/config.py
```

预期：没有空白错误；四个变量名同时出现在示例和当前设置定义中；命令不接触真实 `.env` 文件。

- [ ] **Step 3：提交环境示例**

```powershell
git add .env.example
git commit -m "docs: align V0.1 environment example"
```

### Task 3：更新 README 的真实 V0.1 状态

**Files:**
- Modify: `README.md`

- [ ] **Step 1：更新当前阶段和能力清单**

将当前阶段更新为 Task 0–10 已完成，说明 Task 10 是文档与验证收尾。保留准确的已交付能力：注册、登录、`/app` 当前用户校验、当前用户自己的空间列表、弹窗创建空间、创建后跳转至不加载数据的详情占位页。

README 必须区分既有后端能力与本次前端范围：后端已有 logout API 和创建空间时默认知识库的原子创建，但前端没有退出流程，Task 10 也不新增默认知识库展示。

- [ ] **Step 2：更新安装与验证说明**

将前端依赖安装命令改为 `npm.cmd ci`，列出 Task 1 的前端检查命令。后端命令使用根目录既有 `.venv` 的解释器，但必须从 Task 10 worktree 的 `services/api` 目录运行。把验证结果更新为本次实际执行结果，不沿用旧测试数量或旧浏览器结论。

- [ ] **Step 3：确认 README 没有提前进入 V0.2**

运行：

```powershell
rg -n "Task 10|V0\.2|退出|默认知识库|文档上传|RAG" README.md
git diff --check -- README.md
```

预期：README 将 V0.2 定义为空间内文档上传、文档列表与状态管理的起点；不声称 Task 10 实现退出登录、默认知识库展示或任何 V0.2 功能；没有空白错误。

- [ ] **Step 4：提交 README**

```powershell
git add README.md
git commit -m "docs: record V0.1 closeout status"
```

### Task 4：创建可复现的收尾记录

**Files:**
- Create: `docs/superpowers/handoffs/2026-07-15-task10-v01-closeout.md`

- [ ] **Step 1：记录分支、验证结果和边界**

创建收尾记录，包含以下固定章节：

```markdown
# V0.1 Task 10 收尾记录

## 分支与基线

- 分支：`feat/v0.1-task10-v01-closeout`
- 基线：PR #6 合并后的 `main`

## 已执行验证

记录每条前端和后端命令的完整结论：通过时写退出码与测试数量或关键成功输出；未执行或失败时写命令、失败摘要和阻塞原因。

## 验证边界

- 只有实际成功的检查可以标记为通过。
- 需要真实本地环境、数据库或服务的浏览器联调，未执行时明确标记为未执行。

## 保持未实现

- 前端退出登录、默认知识库展示、空间编辑删除。
- V0.2 的文档上传、文档列表与文档状态管理。
- RAG、竞品分析、报告、模型设置与其他 V0.2+ 能力。

## 下一任务入口

V0.2 从当前用户空间内的文档上传、文档列表和文档状态管理开始；必须基于最新 `main` 创建新的独立 worktree。
```

不得写入真实环境配置、Cookie、Token、账户信息或未经执行的成功结论。

- [ ] **Step 2：对收尾记录做完整性检查**

运行：

```powershell
rg -n "TBD|TODO|待定|未确认" docs/superpowers/handoffs/2026-07-15-task10-v01-closeout.md
git diff --check -- docs/superpowers/handoffs/2026-07-15-task10-v01-closeout.md
```

预期：第一条命令无匹配，第二条命令无空白错误。

- [ ] **Step 3：提交收尾记录**

```powershell
git add docs/superpowers/handoffs/2026-07-15-task10-v01-closeout.md
git commit -m "docs: add V0.1 closeout handoff"
```

### Task 5：最终回归与交付前范围检查

**Files:**
- Modify: 仅在验证结果变化时更新 `README.md` 或收尾记录。

- [ ] **Step 1：重跑全部检查**

重跑 Task 1 的前端六条命令和后端三条命令。

预期：所有声明已通过的检查再次以退出码 0 完成。若产生新的失败，先更新收尾记录中的真实结论，再停止交付与提交。

- [ ] **Step 2：检查差异范围与提交状态**

在 Task 10 worktree 根目录运行：

```powershell
git diff --check origin/main...HEAD
git diff --name-only origin/main...HEAD
git status --short --branch
```

预期：变更仅涉及 `.env.example`、`README.md`、Task 10 设计文档、实施计划和收尾记录；工作区没有未提交改动。

- [ ] **Step 3：提交最终验证记录（仅当内容发生变化）**

若最终回归导致 README 或收尾记录的结果变化，运行：

```powershell
git add README.md docs/superpowers/handoffs/2026-07-15-task10-v01-closeout.md
git commit -m "docs: finalize V0.1 closeout verification"
```

若没有变化，不创建空提交。

## 计划自检

- 设计中的环境示例、README、验证和收尾记录均有独立任务。
- 没有读取、输出、提交或修改真实 `.env`、`.env.local`、密钥、Cookie 或 Token 的步骤。
- 没有退出登录、默认知识库展示或 V0.2+ 应用功能代码。
- 最终范围检查防止将 `node_modules`、真实环境文件或无关 worktree 文件纳入提交。
