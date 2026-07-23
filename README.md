# AI Competitor Intelligence Workspace

中文暂定名：竞品智研台

## 项目定位

面向国内 AI 产品经理的竞品分析工作台。项目目标是把用户私有资料、公开竞品信息、RAG 检索和固定多 Agent 分析流程结合起来，生成有来源、有证据、有不确定性提示的中文结构化竞品分析报告。

当前仓库以 `PRD.md`、`TECH_SPEC.md`、`TASK_BREAKDOWN.md` 为核心依据推进开发；已实现能力与下一步缺口以 [当前项目状态记录](docs/superpowers/handoffs/2026-07-23-current-project-status.md) 为准。

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

V0.1、V0.2、V0.3 和 V0.4 的主流程已合并到 `main`；2026-07-22 又合并了全站“证据编辑部”前端重构。当前处于“补齐 V0.4 报告归档缺口、完成真实集成验证、准备 V1.0 展示与部署”的阶段，而不是从 V0.2 重新开始。

已完成的主流程：

### V0.1：用户与空间基础

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

### V0.2：文档管理

- 空间内 PDF、DOCX、TXT、Markdown 上传，20MB 限制与类型校验
- 文档列表、删除、处理状态与失败原因展示
- 文档索引入口及用户、空间隔离

### V0.3：私有知识库检索

- 文本解析、切分、DashScope embedding 与 `pgvector` 索引
- 按当前用户和当前空间严格过滤的 RAG 检索
- 前端检索表单、来源文档、chunk 与相似度展示

### V0.4：竞品分析与报告

- DeepSeek API Key 加密保存与仅返回脱敏提示的设置页
- 博查公开资料搜索、候选竞品发现和证据归属
- 0–3 个已知竞品、手动/自动候选确认、后台分析、轮询状态与失败重试
- 中文结构化报告、公开网页/私有知识库/模型推断三类证据、报告详情和 PDF/DOCX 导出

### 近期已完成的前端体验工作

- 首页、认证、应用壳、资料、检索、任务、报告和模型设置均已重构为“证据编辑部”视觉系统
- 已覆盖窄屏、深色主题、键盘焦点、可见标签、加载/空/错误状态与减少动态设置

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

当前仍待补齐：

- 真实浏览器 Cookie/CORS 联调、Docker/Alembic 迁移验证，以及用户明确授权后的真实外部 Provider 验证。
- V1.0 展示材料：架构图、截图、示例空间/文档/报告、部署说明和公开 Demo。

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

V0.1 Task 10 曾实际执行并通过：`npm.cmd run test`（7 个测试文件、32/32 tests）、`npm.cmd run check:routes`、`npm.cmd exec tsc -- --noEmit`、`npm.cmd run lint`、`npm.cmd run build`，以及 `npm.cmd audit --omit=dev`（0 vulnerabilities）。后端 `ruff check`、`ruff format --check` 与 `pytest` 也已通过，其中 Pytest 为 100/100。

前端重构合并后的本地验证记录为：`npm.cmd test`（24 个文件、95 个测试）、`npm.cmd run check:routes`、`npx.cmd tsc --noEmit`、`npm.cmd run lint` 与 `npm.cmd run build` 均通过。该记录只代表前端本地门禁；不替代后端、数据库、浏览器或真实第三方服务验证。

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

用户自己的 DeepSeek API Key 会加密保存在数据库中，不作为平台环境变量写入代码仓库；前端仅显示配置状态和脱敏提示。

## 开发顺序

开发执行顺序以 `TASK_BREAKDOWN.md` 为准：

1. V0.1：项目骨架与基础用户系统
2. V0.2：知识库与文档上传
3. V0.3：RAG 检索
4. V0.4：竞品分析任务与报告生成
5. V0.5：多 Agent 工作流优化与导出
6. V1.0：GitHub 可展示版本

报告归档闭环已完成：当前用户可按空间筛选、最新优先查看历史报告，并通过 `/app/reports` 进入报告中心和既有详情页。下一项工作是进行真实集成验证，再准备 V1.0 展示与部署；团队协作、付费、浏览器插件和移动端仍不在当前 MVP 范围。
