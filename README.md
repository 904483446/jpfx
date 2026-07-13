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

V0.1 Task 0（项目初始化与文档对齐）至 Task 8（前端认证流程）已经完成；当前已接入真实注册、真实登录和 `/app` 当前用户校验。下一步是 Task 9：产品空间列表与创建。

已完成：

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
- `POST /api/v1/auth/login` 和 `POST /api/v1/auth/logout`
- 7 天有效的 JWT httpOnly Cookie 登录态
- 统一登录失败响应和幂等退出
- `GET /api/v1/auth/me` 与可复用的当前用户鉴权依赖
- 受鉴权保护的产品空间列表、创建、详情接口与默认知识库原子创建
- Next.js App Router 静态骨架、首页、登录页、注册页与应用壳路由
- 前端 API Client 基础层、环境变量示例、共享视觉组件与静态页面跳转
- 前端真实注册、登录表单及对应错误反馈
- `/app` 通过 `GET /api/v1/auth/me` 校验当前用户，并显示用户昵称与邮箱

Task 8 只覆盖真实注册、登录和 `/app` 当前用户校验；产品空间列表与创建留待 Task 9 实现。

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
Copy-Item .env.example .env.local
# 在 .env.local 中设置 NEXT_PUBLIC_API_BASE_URL，例如 http://127.0.0.1:8000/api/v1
npm.cmd install
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

登录与退出示例：

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

登录成功返回用户公开字段，并设置 7 天有效的 httpOnly Cookie；退出返回 HTTP 204 并清除该 Cookie。

## 环境变量

请参考 `.env.example` 创建本地 `.env`。不要把 `.env`、真实 API Key、数据库密码、JWT 密钥或加密密钥提交到仓库。

登录功能要求本地 `.env` 配置足够长且随机的 `JWT_SECRET`。生产环境还必须设置 `AUTH_COOKIE_SECURE=true`，确保登录 Cookie 只通过 HTTPS 发送。

用户自己的 DeepSeek API Key 未来会加密保存在数据库中，不作为平台环境变量写入代码仓库。

## 开发顺序

开发执行顺序以 `TASK_BREAKDOWN.md` 为准：

1. V0.1：项目骨架与基础用户系统
2. V0.2：知识库与文档上传
3. V0.3：RAG 检索
4. V0.4：竞品分析任务与报告生成
5. V0.5：多 Agent 工作流优化与导出
6. V1.0：GitHub 可展示版本

下一任务只执行 V0.1 Task 9（产品空间列表与创建），不提前实现文档上传、RAG、Agent、报告导出、团队协作或付费系统。
