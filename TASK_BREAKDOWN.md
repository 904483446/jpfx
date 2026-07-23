# TASK_BREAKDOWN.md：AI 产品经理竞品分析平台开发拆解

## Summary

`TASK_BREAKDOWN.md` 采用“全版本路线图 + V0.1 细化任务”的结构。V0.1 写到可直接执行，V0.2-V1.0 保持验收级任务，避免后续实现细节变化导致整份任务文档频繁重写。V0.2–V0.4 的实际实施方案见 `docs/superpowers/plans/`；当前交付状态见 `docs/superpowers/handoffs/2026-07-23-current-project-status.md`。

默认执行原则：

- TDD 优先，核心后端模块先写测试再实现。
- 本地开发使用 Docker PostgreSQL + pgvector，线上使用 Supabase。
- 前端包管理器使用 `npm.cmd`。
- 第一阶段不写业务大而全，先完成用户系统、项目骨架、数据库连接和 Dashboard 雏形。
- 当前文档只做开发拆解，不直接实现代码。

## 文档结构

`TASK_BREAKDOWN.md` 包含以下章节：

- 开发原则
- 环境与工具默认选择
- 版本总览
- V0.1 详细任务
- V0.2-V1.0 路线图任务
- 测试与验收标准
- 暂不做事项
- 后续文档依赖关系

## 开发原则

- 每个版本必须能独立验收。
- 每个任务必须能对应到 `PRD.md` 或 `TECH_SPEC.md`。
- 用户隔离、鉴权、API Key 加密、RAG 空间隔离必须有测试。
- 后端核心逻辑优先 TDD。
- 前端页面先保证流程完整，再做视觉打磨。
- 不在 V0.1 引入 Redis、Worker、大规模爬虫、付费系统、团队权限。
- 不把密钥、Token、数据库密码、API Key 写入代码仓库。
- 如果 Docker、PostgreSQL、外部 API 无法实际运行，必须明确标注验证缺口。

## 环境与工具默认选择

- 前端：Next.js + React + TypeScript + Tailwind CSS + shadcn/ui
- 前端命令：`npm.cmd`
- 后端：FastAPI + Pydantic + SQLAlchemy + Alembic
- 本地数据库：Docker PostgreSQL + pgvector
- 线上数据库：Supabase PostgreSQL + pgvector
- 文件存储：本地 storage 开发，Supabase Storage 部署
- 默认聊天模型：DeepSeek，用户自行配置 API Key
- 默认 embedding：通义 DashScope `text-embedding-v4`
- 默认搜索：博查 AI Search API
- 后端部署：Render
- 前端部署：Vercel

## 版本总览

| 版本 | 状态 | 目标 | 核心交付 |
| --- | --- | --- | --- |
| V0.1 | 已完成 | 项目骨架与基础用户系统 | 前后端骨架、数据库迁移、注册登录、Dashboard、产品空间 |
| V0.2 | 已完成 | 知识库与文档上传 | 默认知识库、文档上传、文档列表、状态管理 |
| V0.3 | 已完成 | RAG 检索 | 文档解析、切分、embedding、pgvector 检索 |
| V0.4 | 主流程完成，报告列表待补 | 竞品分析任务与报告生成 | DeepSeek、博查搜索、半自动竞品补充、固定分析流水线、报告详情与导出 |
| V0.5 | 未开始；部分能力已提前交付 | 多 Agent 工作流优化与导出 | 待补 Agent 运行记录与质量检查；失败重试、证据列表、PDF/Word 已在 V0.4 提前交付 |
| V1.0 | 未开始 | GitHub 可展示版本 | README、截图、示例数据、示例报告、部署说明、公开 Demo |

## V0.1：项目骨架与基础用户系统

目标：建立正式前后端项目结构，完成用户注册、登录、退出、当前用户和 Dashboard 基础访问保护。

### Task 0：项目初始化与文档对齐

交付：

- 检查 `PRD.md` 和 `TECH_SPEC.md` 是否存在。
- 创建根目录基础文件：`.env.example`、`README.md` 初稿。
- 创建目录结构：`apps/web`、`services/api`。
- 记录本地开发要求：Node、Python、Docker、PostgreSQL、pgvector。

建议文件：

- `README.md`
- `.env.example`
- `apps/web/`
- `services/api/`

测试与检查：

- 确认 `PRD.md`、`TECH_SPEC.md`、`TASK_BREAKDOWN.md` 都存在。
- 确认 README 初稿说明项目用途和启动方向。

验收：

- 目录结构符合 `TECH_SPEC.md`。
- README 初稿能说明项目用途、技术栈和后续启动方式。

### Task 1：后端 FastAPI 骨架

交付：

- 创建 `services/api` 后端项目。
- 配置 FastAPI 应用入口。
- 配置统一 API 前缀 `/api/v1`。
- 配置健康检查接口。
- 配置统一错误结构。

统一错误结构：

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "中文错误信息",
    "details": {}
  }
}
```

建议文件：

- `services/api/pyproject.toml`
- `services/api/app/main.py`
- `services/api/app/core/config.py`
- `services/api/app/core/errors.py`
- `services/api/app/api/v1/health.py`
- `services/api/tests/test_health.py`

测试：

- 健康检查返回成功。
- 不存在接口返回统一中文错误。

验收：

- 本地可启动 FastAPI。
- 访问健康检查接口成功。
- 错误响应符合 `TECH_SPEC.md`。

### Task 2：数据库与迁移基础

交付：

- 配置 SQLAlchemy。
- 配置 Alembic。
- 配置 Docker PostgreSQL + pgvector。
- 创建第一批表：`users`、`spaces`、`knowledge_bases`。
- 本地环境使用 `.env`，仓库只提交 `.env.example`。

建议文件：

- `docker-compose.yml`
- `services/api/alembic.ini`
- `services/api/alembic/`
- `services/api/app/db/session.py`
- `services/api/app/models/user.py`
- `services/api/app/models/space.py`
- `services/api/app/models/knowledge_base.py`
- `services/api/tests/test_database.py`

测试：

- 数据库连接成功。
- Alembic migration 可执行。
- `users` 表字段符合 PRD。
- `spaces` 表包含 `user_id`。
- `knowledge_bases` 表包含 `user_id` 和 `space_id`。

验收：

- 本地数据库可通过迁移创建基础表。
- 迁移可以在空数据库上从零执行。

### Task 3：用户注册

交付：

- 实现 `POST /api/v1/auth/register`。
- 字段：`email`、`password`、`display_name`。
- 密码哈希保存。
- 邮箱唯一。
- 注册后创建用户记录。

建议文件：

- `services/api/app/api/v1/auth.py`
- `services/api/app/schemas/auth.py`
- `services/api/app/services/auth_service.py`
- `services/api/app/core/security.py`
- `services/api/tests/test_auth_register.py`

测试：

- 成功注册用户。
- 重复邮箱返回中文错误。
- 数据库不保存明文密码。
- 返回结果不包含 `password_hash`。
- 邮箱为空、密码为空时返回中文校验错误。

验收：

- 用户可注册。
- 安全规则满足 PRD。

### Task 4：用户登录与退出

交付：

- 实现 `POST /api/v1/auth/login`。
- 实现 `POST /api/v1/auth/logout`。
- 登录成功后设置 httpOnly Cookie。
- 密码错误返回统一中文错误。

建议文件：

- `services/api/app/api/v1/auth.py`
- `services/api/app/services/auth_service.py`
- `services/api/app/core/security.py`
- `services/api/tests/test_auth_login.py`

测试：

- 正确邮箱密码登录成功。
- 错误密码登录失败。
- 未注册邮箱登录失败。
- 登录成功响应设置 httpOnly Cookie。
- 退出后 Cookie 清除。

验收：

- 登录/退出闭环可用。
- 前端后续可基于 Cookie 读取当前用户。

### Task 5：当前用户与鉴权依赖

交付：

- 实现 `GET /api/v1/auth/me`。
- 实现后端 `get_current_user` 依赖。
- 未登录访问受保护接口返回 401 中文错误。

建议文件：

- `services/api/app/api/deps.py`
- `services/api/app/api/v1/auth.py`
- `services/api/tests/test_auth_me.py`

测试：

- 登录后可获取当前用户。
- 未登录不能获取当前用户。
- 过期或无效 Cookie 返回未授权。
- 返回结果不包含敏感字段。

验收：

- 后续业务接口可复用鉴权依赖。
- 未登录访问受保护资源的错误格式一致。

### Task 6：产品空间基础 CRUD

交付：

- 实现 `GET /api/v1/spaces`。
- 实现 `POST /api/v1/spaces`。
- 实现 `GET /api/v1/spaces/{space_id}`。
- 创建空间时自动创建默认知识库。
- 所有查询必须按 `user_id` 过滤。

建议文件：

- `services/api/app/api/v1/spaces.py`
- `services/api/app/schemas/space.py`
- `services/api/app/services/space_service.py`
- `services/api/tests/test_spaces.py`

测试：

- 用户可创建空间。
- 创建空间后自动创建默认知识库。
- 用户只能看到自己的空间列表。
- 用户 A 不能访问用户 B 的空间。
- 空间名称为空时返回中文错误。

验收：

- 产品空间作为后续知识库、任务、报告的隔离边界可用。

### Task 7：前端 Next.js 骨架

交付：

- 创建 `apps/web`。
- 配置 TypeScript、Tailwind CSS、shadcn/ui。
- 创建基础页面：
  - `/`
  - `/login`
  - `/register`
  - `/app`
- 创建 API Client。
- 配置 `NEXT_PUBLIC_API_BASE_URL`。

建议文件：

- `apps/web/package.json`
- `apps/web/app/page.tsx`
- `apps/web/app/login/page.tsx`
- `apps/web/app/register/page.tsx`
- `apps/web/app/app/page.tsx`
- `apps/web/lib/api-client.ts`
- `apps/web/components/`

检查：

- 前端可启动。
- 公开首页可访问。
- 登录页、注册页、Dashboard 页面可访问。

验收：

- 前端骨架符合 `TECH_SPEC.md`。
- 公开首页只做产品介绍，不重点展示技术栈。

### Task 8：前端登录注册流程

交付：

- 注册页对接后端注册接口。
- 登录页对接后端登录接口。
- 登录成功跳转 `/app`。
- `/app` 页面读取当前用户。
- 未登录访问 `/app` 跳转登录。

建议文件：

- `apps/web/app/login/page.tsx`
- `apps/web/app/register/page.tsx`
- `apps/web/app/app/page.tsx`
- `apps/web/lib/api-client.ts`
- `apps/web/lib/auth.ts`

测试：

- 注册表单校验。
- 登录失败显示中文错误。
- 登录成功进入 Dashboard。
- 未登录访问 `/app` 时跳转登录。

验收：

- 用户可通过页面完成注册登录。

### Task 9：Dashboard 与空间入口

交付：

- Dashboard 展示当前用户信息。
- 展示产品空间列表。
- 支持新建产品空间。
- 支持进入空间详情占位页。

建议文件：

- `apps/web/app/app/page.tsx`
- `apps/web/app/app/spaces/[spaceId]/page.tsx`
- `apps/web/components/spaces/space-create-dialog.tsx`
- `apps/web/components/spaces/space-list.tsx`

测试：

- 空间列表只展示当前用户数据。
- 新建空间表单必填校验。
- 新建空间成功后列表刷新。

验收：

- 用户登录后可以创建并进入产品空间。

### Task 10：V0.1 收尾

交付：

- 补充 README 当前阶段说明。
- 补充 `.env.example`。
- 运行后端测试。
- 运行前端基础检查。
- 记录未完成事项和下一版本入口。

验收清单：

- 用户可以注册。
- 用户可以登录。
- 用户可以退出。
- 用户可以进入 Dashboard。
- 用户可以创建产品空间。
- 创建空间后自动生成默认知识库。
- 用户 A 不能访问用户 B 的空间。
- 未登录用户不能访问应用页面。

## V0.2：知识库与文档上传

目标：完成产品空间内文档上传、文档列表、文档状态管理。

交付任务：

- 创建 `documents` 表和迁移。
- 实现文件上传接口。
- 支持 PDF、DOCX、TXT、MD 文件类型校验。
- 限制单文件 20MB。
- 本地开发保存到本地 storage。
- 部署环境保存到 Supabase Storage。
- 展示知识库文档列表。
- 展示文档状态：`uploaded`、`processing`、`indexed`、`failed`。
- 实现删除文档和重新索引入口占位。

验收：

- 用户可在空间内上传文档。
- 文档记录保存到数据库。
- 文档只能被所属用户访问。
- 文件过大或格式不支持时显示中文错误。

## V0.3：RAG 检索

目标：完成文档解析、切分、embedding、pgvector 检索闭环。

交付任务：

- 实现 PDF、DOCX、TXT、MD 文本解析。
- 实现 chunk 切分。
- 接入 DashScope `text-embedding-v4`。
- 创建 `document_chunks` 表和 pgvector 索引。
- 实现 `/spaces/{space_id}/retrieval/search`。
- 检索强制过滤 `user_id + space_id`。
- 前端知识库页展示索引状态和失败原因。

验收：

- 文档可以完成索引。
- 查询可以返回相关 chunk。
- chunk 带来源文档和 metadata。
- 用户 A 无法检索用户 B 的 chunk。
- 当前空间无法检索其他空间的 chunk。

## V0.4：竞品分析任务与报告生成

目标：完成从新建分析任务到生成中文报告的主流程。

交付任务：

- 创建 `analysis_tasks`、`agent_runs`、`competitor_reports`、`report_evidence` 表。
- 实现模型配置页，用户配置 DeepSeek API Key。
- API Key 加密保存，前端只显示脱敏信息。
- 实现新建竞品分析任务页。
- 支持 0-3 个已知竞品输入。
- 默认使用半自动补充竞品。
- 实现 DeepSeek LLM Provider。
- 实现 Bocha Search Provider。
- 实现 Basic Scrape Provider。
- 实现基础多 Agent 流水线。
- 生成中文 Markdown 报告和结构化 JSON。
- 实现报告详情页和历史报告页。

验收：

- 未配置 DeepSeek Key 不能运行任务。
- 用户可以创建“企业知识库 Copilot”分析任务。
- 系统最多分析 3 个竞品。
- 自动补充竞品必须有搜索证据。
- 报告包含 PRD 要求的核心字段。
- 报告展示私有知识库引用和公开资料来源。

## V0.5：多 Agent 工作流优化与导出

目标：提升任务可解释性、失败恢复能力和报告交付体验。

交付任务：

- 完善 Agent 运行日志。
- 任务进度页展示每个 Agent 状态。
- 增加质量检查 Agent。
- 增加失败重试。
- 增加报告证据列表。
- 实现 PDF 导出。
- 实现 Word 导出。
- 评估是否引入 Render Worker + Redis。

验收：

- 用户可以看到 Agent 执行进度。
- 单个 Agent 失败能显示原因。
- 报告可以追溯来源。
- 报告可导出 PDF 和 Word。
- 如果任务耗时明显，给出 Worker 升级方案。

## V1.0：GitHub 可展示版本

目标：形成完整开源作品和公开 Demo。

交付任务：

- 完善 README。
- 增加架构图。
- 增加页面截图。
- 增加 `.env.example`。
- 增加本地启动说明。
- 增加 Vercel + Supabase + Render 部署说明。
- 准备“企业知识库 Copilot”示例空间、示例文档、示例报告。
- 部署公开 Demo。
- Demo 使用用户自带 API Key，不提供公共模型额度。

验收：

- 新用户可按 README 本地启动。
- GitHub 页面能清楚说明项目价值。
- 公开 Demo 可访问。
- 示例流程可完整展示：上传资料 -> 创建任务 -> 生成报告 -> 查看历史报告。

## Test Plan

后端测试重点：

- 注册、登录、退出、当前用户。
- 密码哈希保存。
- httpOnly Cookie 鉴权。
- 用户 A 不能访问用户 B 的空间、文档、chunk、任务、报告。
- API Key 加密保存。
- 未配置模型 Key 时不能运行任务。
- RAG 检索只返回当前用户当前空间的 chunk。
- 自动补充竞品必须有搜索证据。
- 报告字段完整。

前端测试重点：

- 未登录访问 `/app` 跳转登录。
- 注册、登录表单校验。
- Dashboard 展示当前用户空间。
- 上传文档状态展示。
- 新建任务表单校验。
- 任务进度轮询展示。
- 报告详情正常渲染。
- 模型设置页不显示明文 API Key。

集成验收重点：

- 注册新用户。
- 创建“企业知识库 Copilot”空间。
- 上传示例文档。
- 完成文档索引。
- 发起半自动竞品分析。
- 生成中文报告。
- 查看历史报告。
- 验证跨用户隔离。

## 暂不做事项

V1.0 前暂不做：

- 团队协作
- 组织空间
- 成员邀请
- 复杂 RBAC 权限系统
- 付费系统
- 浏览器插件
- 实时协同编辑
- 企业级审计日志
- 大规模爬虫平台
- 自动定时监控竞品
- 管理员后台
- 多知识库组合检索
- 报告模板市场

## 后续文档依赖关系

- 产品范围判断以 `PRD.md` 为准。
- 技术架构和接口设计以 `TECH_SPEC.md` 为准。
- 开发执行顺序以 `TASK_BREAKDOWN.md` 为准。
- GitHub 展示、启动方式和部署说明以 `README.md` 为准。

后续进入编码前，应先确认当前目标版本。例如：

- 如果目标是 V0.1，只读取 `PRD.md`、`TECH_SPEC.md` 和本文件的 V0.1 部分。
- 如果目标是 V0.3，再补读 V0.2 和 V0.3 的相关任务。
- 如果目标是 V1.0 展示，再补读 README 和部署说明。

## Assumptions

- `TASK_BREAKDOWN.md` 只负责开发拆解，不重复完整 PRD 和 TECH_SPEC。
- V0.1 先完成可运行骨架和用户系统，不提前实现 RAG 或 Agent。
- V0.1-V0.4 不引入 Redis。
- 本地数据库默认 Docker PostgreSQL + pgvector。
- 前端包管理器默认 `npm.cmd`。
- 后续进入实现时，每个后端核心模块按 TDD 执行。
- 当前 Git 仓库状态异常，生成文档后如需提交，需要先修复 Git 仓库识别问题。
