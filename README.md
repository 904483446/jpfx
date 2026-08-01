# JPFX｜竞品智研台

面向 AI 产品经理的私有竞品研究工作台：在一个受用户与产品空间隔离的流程中，沉淀资料、检索证据、完成竞品分析，并归档可导出的报告。

> 当前仓库用于展示已合并的本地实现；公开 Demo 尚未提供，生产部署与真实第三方服务联调均属后续验证范围。

## 产品流程

`产品空间 → 私有资料 / RAG → 竞品分析任务 → 证据与报告归档 → PDF / DOCX 导出`

```mermaid
flowchart LR
    Browser["Browser / Next.js"] -->|"credentials: include"| API["FastAPI"]
    API --> DB["Postgres + pgvector"]
    API --> Storage["storage"]
    API -. "optional user-configured providers" .-> Providers["optional user-configured providers"]
    API --> Exports["exports: PDF / DOCX"]
```

浏览器通过携带凭据的请求访问 FastAPI；服务端负责鉴权、空间隔离、资料与向量检索、任务和报告。外部模型、检索服务仅在用户或运行环境完成相应配置时才会被调用。

## 页面预览

登录页

![登录页](docs/assets/v1-showcase/login-v2.png)

工作台空状态

![工作台空状态](docs/assets/v1-showcase/dashboard-v2.png)

分析任务空队列

![分析任务空队列](docs/assets/v1-showcase/task-or-report-v2.png)

模型凭据设置

![模型凭据设置](docs/assets/v1-showcase/settings-v2.png)

以上均为本地开发环境真实页面截图；不代表外部 Provider 已发生真实调用，也不代表已提供公开线上 Demo。

为不创建演示业务数据，当前不展示产品空间详情页截图。

## 已合并能力

| 能力 | 已合并实现 |
| --- | --- |
| 身份与空间 | 注册、登录、登出、httpOnly Cookie 会话、当前用户校验，以及按用户归属的产品空间与默认知识库。 |
| 私有资料 | 空间内 PDF、DOCX、TXT、Markdown 上传、列表、删除、状态与失败原因展示。 |
| RAG 检索 | 文本解析与切分、`pgvector` 向量索引，以及按当前用户和产品空间过滤的检索结果与来源展示。 |
| 竞品分析 | 已知竞品输入、候选竞品确认、后台任务状态轮询与失败重试。 |
| Agent 运行记录 | 每轮分析固定记录证据收集、质量检查、模型分析与报告生成；任务页按轮次展示安全状态、时间与失败原因。 |
| 证据与报告 | 基于受限证据的结构化中文报告、报告详情、历史报告列表与按空间归档。 |
| 交付导出 | 报告 PDF / DOCX 导出，并附带可用的证据链接。 |
| 前端体验 | 首页、认证、应用壳、资料、检索、任务、报告与模型设置页面，以及加载、空态、错误和键盘焦点状态。 |

## 本地启动

仅使用仓库中的 [`.env.example`](.env.example) 作为环境变量说明；不要提交真实 `.env`、`apps/web/.env.local`、密钥、Cookie 或 Token。

1. 按 [`.env.example`](.env.example) 创建本地 `.env`。该文件为 Docker PostgreSQL + pgvector 与后端提供本地配置；不要展示或提交其中的真实值。按需配置变量名：`JWT_SECRET`、`DATABASE_URL`、`TEST_DATABASE_URL`、`CORS_ALLOWED_ORIGINS`、`AUTH_COOKIE_SECURE`。
2. 从仓库根目录启动本地 PostgreSQL + pgvector：

   ```powershell
   docker compose up -d --wait db
   ```

3. 等待 `db` 就绪后，在启动 FastAPI 前执行数据库迁移：

   ```powershell
   cd services/api
   ./.venv/Scripts/python.exe -m alembic upgrade head
   ```

4. 在 `apps/web/.env.local` 中设置以下非敏感本地地址：

   ```text
   NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000/api/v1
   ```

5. 可选能力仅在需要时配置对应变量：`DASHSCOPE_API_KEY`（RAG）、`BOCHA_API_KEY`（候选检索）、`API_KEY_ENCRYPTION_SECRET`（保存用户 DeepSeek Key 前）。
6. 分别启动后端和前端：

```powershell
# 终端 1：后端
cd services/api
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload

# 终端 2：前端
cd apps/web
npm.cmd ci
npm.cmd run dev
```

后端健康检查地址：`http://127.0.0.1:8000/api/v1/health`。

常用本地检查：

```powershell
# 从仓库根目录启动测试数据库，并等待其就绪，避免测试连接竞争
docker compose up -d --wait db-test

# 后端（services/api）
cd services/api
.\.venv\Scripts\python.exe -m ruff check --no-cache .
.\.venv\Scripts\python.exe -m ruff format --check --no-cache .
.\.venv\Scripts\python.exe -m pytest -q

# 前端（apps/web）
cd ../../apps/web
npm.cmd run test
npm.cmd run check:routes
npx.cmd tsc --noEmit
npm.cmd run lint
npm.cmd run build
```

## 已验证

- 后端 Ruff 与 190 项 pytest、前端 113 项 Vitest、路由检查、类型检查、lint 与生产构建均已在本地通过。
- 本地数据库已升级到 `20260729_0005 (head)`；FastAPI 健康端点返回 HTTP 200。
- 真实本地 Chrome 已验证 Cookie 会话、受保护页面、产品空间/任务入口、退出登录及退出后的 `/app` 拦截。
- 代码中已实现凭据携带、Cookie 会话、用户与产品空间过滤、PostgreSQL + pgvector 访问、资料存储路径隔离、报告归档与 PDF / DOCX 导出。
- 真实配置值不写入本仓库：用户配置的模型密钥只以加密或脱敏状态参与实现，前端不保存或返回该密钥。

## 未验证 / 后续工作

- Docker daemon 状态读取受当前本机权限限制；数据库迁移已通过 Alembic 直接连接的本地 PostgreSQL 验证。
- DashScope、DeepSeek、Bocha 等外部 Provider 的真实请求取决于用户或环境完成配置；当前不宣称已验证。
- 本仓库未提供公开 Demo；生产部署、视觉验收与公开展示材料属于后续工作。

## 技术边界

- 前端：Next.js、React、TypeScript、Tailwind CSS、shadcn/ui。
- 后端：FastAPI、Pydantic、SQLAlchemy、Alembic。
- 数据：PostgreSQL、pgvector 与受空间隔离的资料存储。
- 外部能力：模型、嵌入和检索 Provider 为可选配置，不包含任何真实凭据。

## 部署边界：Supabase Storage

- 本地开发在未配置 Supabase Storage 变量时继续使用本地资料目录；不要为本地开发复制、读取或提交 Railway 生产变量。
- 生产环境仅在 Railway 配置 `SUPABASE_URL`、`SUPABASE_SECRET_KEY` 与 `SUPABASE_STORAGE_BUCKET=jpfx-documents`。`SUPABASE_SECRET_KEY` 使用 Supabase 新版 `sb_secret_...`，只能保存在 Railway Variables，绝不暴露给浏览器、前端环境变量、日志或仓库。
- 在 Supabase Dashboard 创建私有（非 public）bucket `jpfx-documents`。对象访问由后端使用服务端凭据完成，浏览器不直接持有 bucket 的访问密钥。
- 真正上线前，按交接文档完成一次无敏感信息 TXT 的上传、刷新、重新部署、索引与删除验收；本仓库的本地测试不等同于真实 Supabase 或 Railway 验证。

## 项目文档

- [PRD.md](PRD.md)：产品范围与目标用户。
- [TECH_SPEC.md](TECH_SPEC.md)：技术设计与边界。
- [TASK_BREAKDOWN.md](TASK_BREAKDOWN.md)：版本任务与演进记录。
