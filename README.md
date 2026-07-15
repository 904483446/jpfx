# AI Competitor Intelligence Workspace

中文暂定名：竞品智研台

## 项目定位

面向国内 AI 产品经理的竞品分析工作台。项目目标是把用户私有资料、公开竞品信息、RAG 检索和固定多 Agent 分析流程结合起来，生成有来源、有证据、有不确定性提示的中文结构化竞品分析报告。

当前仓库以 `PRD.md`、`TECH_SPEC.md`、`TASK_BREAKDOWN.md` 为核心依据推进开发，功能范围和执行顺序以这些文档为准。

## 技术栈方向

- 前端：Next.js + React + TypeScript + Tailwind CSS + shadcn/ui
- 后端：FastAPI + Pydantic + SQLAlchemy + Alembic
- 数据库：PostgreSQL + pgvector
- 本地数据库：Docker PostgreSQL + pgvector
- 线上数据与文件存储：Supabase PostgreSQL + Supabase Storage
- 后端部署：Render
- 前端部署：Vercel
- 默认聊天模型：DeepSeek，用户自行配置 API Key
- 默认 embedding：通义 DashScope `text-embedding-v4`
- 默认搜索：博查 AI Search API

## 当前阶段

V0.1 Task 0（项目初始化与文档对齐）至 Task 10（文档与验证收尾）已经完成；当前已接入真实注册、真实登录、`/app` 当前用户校验、空间列表和弹窗创建。

已完成：

已有基础能力（在 Task 8 开始前已实现；其中后端 API 仅作参考）：

- 核心文档与前后端目录入口
- FastAPI 应用入口和 `/api/v1` 统一前缀
- `GET /api/v1/health` 健康检查
- 统一中文错误响应
- 后端自动化测试
- Docker PostgreSQL + pgvector 开发库和隔离测试库
- SQLAlchemy 同步会话、基础模型与 Alembic 首次迁移
- `users`、`spaces`、`knowledge_bases` 基础表及数据库级隔离约束
- `POST /api/v1/auth/register` 用户注册接口
- 邮箱与昵称规范化、Argon2id 密码哈希及重复邮箱保护
- 注册请求、服务层、数据库约束和 API 集成自动化测试
- 已有后端 API：`POST /api/v1/auth/login` 和 `POST /api/v1/auth/logout`
- 7 天有效的 JWT httpOnly Cookie 登录态
- 统一登录失败响应和幂等退出
- `GET /api/v1/auth/me` 与可复用的当前用户鉴权依赖
- 受鉴权保护的产品空间列表、创建、详情接口与默认知识库原子创建
- Next.js App Router 静态骨架、首页、登录页、注册页与应用壳路由
- 前端 API Client 基础层、环境变量示例、共享视觉组件与静态页面跳转
- Task 8 前端：真实注册、登录表单及对应错误反馈
- Task 8 前端：`/app` 通过 `GET /api/v1/auth/me` 校验当前用户，并显示用户昵称与邮箱
- Task 9 前端：`/app` 展示当前用户自己的产品空间列表，支持加载、空列表和错误重试状态
- Task 9 前端：以弹窗创建名称必填、行业/产品方向/描述选填的产品空间；成功后进入空间详情占位页
- Task 10：收敛非敏感环境变量示例、更新项目状态说明，并完成前后端自动化验证记录

空间详情页当前仅为占位页，不加载空间详情数据。后端已有 `POST /api/v1/auth/logout` 和创建空间时原子创建默认知识库的能力；前端退出流程和默认知识库展示均未实现，且 Task 10 不新增这些功能。

## 目录结构

```text
jpfx/
  PRD.md
  TECH_SPEC.md
  TASK_BREAKDOWN.md
  README.md
  .env.example
  apps/
    web/
  services/
    api/
```

后续任务会继续补齐：

- `services/api`：FastAPI 应用、API 路由、数据库模型、服务层、测试和迁移。
- `apps/web`：Next.js App Router 页面、组件、API Client 和类型定义。

## 本地开发要求

后续正式进入代码开发时需要准备：

- Node.js，用于前端 Next.js 项目
- `npm.cmd`，作为 Windows 环境下的前端包管理命令
- Python，用于 FastAPI 后端
- Docker，用于本地 PostgreSQL + pgvector
- PostgreSQL + pgvector，用于业务数据和向量检索

### 后端测试与启动

```powershell
cd services/api
.\.venv\Scripts\python.exe -m ruff check --no-cache .
.\.venv\Scripts\python.exe -m ruff format --check --no-cache .
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

启动后访问 `http://127.0.0.1:8000/api/v1/health`，预期返回 `{"status":"ok"}`。

### 前端启动与检查

```powershell
cd apps/web
# 创建 apps/web/.env.local，并仅设置 NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000/api/v1
npm.cmd ci
npm.cmd run dev
```

前端检查命令：

```powershell
npm.cmd run test
npm.cmd run check:routes
npm.cmd exec tsc -- --noEmit
npm.cmd run lint
npm.cmd run build
```

Task 10 已实际执行并通过：`npm.cmd run test`（7 个测试文件、32/32 tests）、`npm.cmd run check:routes`、`npm.cmd exec tsc -- --noEmit`、`npm.cmd run lint`、`npm.cmd run build`，以及 `npm.cmd audit --omit=dev`（0 vulnerabilities）。后端 `ruff check`、`ruff format --check` 与 `pytest` 也已通过，其中 Pytest 为 100/100。

### 浏览器烟雾验证

Task 10 未重跑浏览器烟雾验证；浏览器联调只在本地前后端服务已由用户配置并启动时执行。自动化测试不能替代真实 Cookie 会话与凭据型 CORS 的浏览器验证。

在用户已配置本地环境后，可分别执行以下命令：

```powershell
# 终端 1
cd services/api
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload

# 终端 2
cd apps/web
npm.cmd run dev
```

打开 `http://127.0.0.1:3000/register`，完成注册后登录；验收 `/app` 显示当前用户昵称和邮箱、刷新后仍能通过当前用户校验、无登录态访问 `/app` 跳转 `/login`。同时在浏览器网络面板确认该流程不发起 `/spaces` 请求，并在存储面板确认前端未写入 JWT。

注册用户示例：

```powershell
$body = @{
  email = "user@example.com"
  password = "valid-password"
  display_name = "示例用户"
} | ConvertTo-Json

Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:8000/api/v1/auth/register" `
  -ContentType "application/json" `
  -Body $body
```

成功时接口返回 HTTP 201 和用户公开字段，不返回密码或密码哈希。

已有后端登录与退出 API 示例（非 Task 8 前端范围）：

```powershell
$loginBody = @{
  email = "user@example.com"
  password = "valid-password"
} | ConvertTo-Json

$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:8000/api/v1/auth/login" `
  -ContentType "application/json" `
  -Body $loginBody `
  -WebSession $session

Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:8000/api/v1/auth/logout" `
  -WebSession $session
```

已有后端 API 的登录成功响应会设置 7 天有效的 httpOnly Cookie；已有后端退出 API 返回 HTTP 204 并清除该 Cookie。前端退出流程不在 Task 8 范围内。

## 环境变量

请参考 `.env.example` 创建本地 `.env`。不要把 `.env`、真实 API Key、数据库密码、JWT 密钥或加密密钥提交到仓库。

登录功能要求本地 `.env` 配置足够长且随机的 `JWT_SECRET`。生产环境还必须设置 `AUTH_COOKIE_SECURE=true`，确保登录 Cookie 只通过 HTTPS 发送。

### 本地登录 CORS 配置

后端通过 `CORS_ALLOWED_ORIGINS` 控制允许携带登录 Cookie 的前端来源。它不是敏感信息；未设置时，本地开发默认允许 `http://127.0.0.1:3000`。如需同时使用多个本地前端地址，可用英文逗号分隔，例如 `http://127.0.0.1:3000,http://localhost:3000`。

生产环境必须将该变量设置为实际部署的 HTTPS 前端 Origin（协议、域名和端口需与浏览器请求一致）。不得使用 `*`：携带 Cookie 的 CORS 请求不允许通配符来源，服务会拒绝此配置。

用户自己的 DeepSeek API Key 未来会加密保存在数据库中，不作为平台环境变量写入代码仓库。

## 开发顺序

开发执行顺序以 `TASK_BREAKDOWN.md` 为准：

1. V0.1：项目骨架与基础用户系统
2. V0.2：知识库与文档上传
3. V0.3：RAG 检索
4. V0.4：竞品分析任务与报告生成
5. V0.5：多 Agent 工作流优化与导出
6. V1.0：GitHub 可展示版本

V0.2 从空间内文档上传、文档列表和文档状态管理开始。空间详情数据加载、空间编辑删除、前端退出登录、默认知识库展示、RAG、竞品分析、报告导出、团队协作和付费系统仍未实现，后续任务不得提前进入 V0.2+ 范围。
