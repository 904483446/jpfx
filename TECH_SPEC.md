# TECH_SPEC.md：AI 产品经理竞品分析平台技术方案

## 1. 技术总览

本项目采用正式前后端分离架构：

- 前端：Next.js + React + TypeScript + Tailwind CSS + shadcn/ui
- 后端：FastAPI + Pydantic + SQLAlchemy + Alembic
- 数据库：Supabase PostgreSQL
- 向量检索：pgvector
- 文件存储：Supabase Storage
- 后端部署：Render
- 前端部署：Vercel
- 默认聊天模型：DeepSeek，用户自行配置 API Key
- 默认 embedding：通义 DashScope `text-embedding-v4`
- 默认搜索：博查 AI Search API
- 搜索备选：百度千帆百度搜索 API
- 抓取策略：后端网页解析优先，失败时使用搜索摘要兜底

核心设计原则：

- 用户数据必须通过 `user_id` 隔离。
- 产品空间数据必须通过 `space_id` 隔离。
- API Key 加密保存，不写入仓库。
- 多 Agent 使用固定流水线，不做完全自治 Agent。
- 第一版保证主流程稳定，不做大规模爬虫平台。

## 2. 代码结构

推荐项目结构：

```text
jpfx/
  PRD.md
  TECH_SPEC.md
  TASK_BREAKDOWN.md
  README.md
  .env.example
  apps/
    web/
      app/
      components/
      lib/
      types/
      package.json
  services/
    api/
      app/
        main.py
        core/
        api/
        models/
        schemas/
        services/
        agents/
        providers/
        workers/
      alembic/
      tests/
      pyproject.toml
```

说明：

- `apps/web` 存放 Next.js 前端。
- `services/api` 存放 FastAPI 后端。
- `providers` 存放模型、搜索、抓取、存储等外部服务适配。
- `agents` 存放竞品分析 Agent 流程。
- `workers` 存放文档索引、报告生成等后台任务逻辑。

## 3. 前端技术方案

前端使用 Next.js App Router。

页面分组：

- `/`：公开首页，只做产品介绍，不突出技术栈。
- `/login`：登录页。
- `/register`：注册页。
- `/app`：登录后 Dashboard。
- `/app/spaces`：产品空间列表。
- `/app/spaces/[spaceId]`：空间工作台。
- `/app/spaces/[spaceId]/knowledge`：知识库管理。
- `/app/spaces/[spaceId]/tasks/new`：新建竞品分析任务。
- `/app/tasks/[taskId]`：任务进度。
- `/app/reports`：历史报告。
- `/app/reports/[reportId]`：报告详情。
- `/app/settings`：用户设置和模型配置。

UI 方案：

- Tailwind CSS 做样式系统。
- shadcn/ui 提供按钮、表单、对话框、表格、Tabs、Toast 等组件。
- `frontend-design` 技能用于后续页面视觉设计和细节打磨。
- 产品首页保持简洁，重点说明“上传资料、分析竞品、生成报告”。

前端状态：

- 登录态通过后端 httpOnly Cookie 管理。
- 前端 API Client 统一封装请求和中文错误提示。
- 任务进度页 V0.4 使用轮询，V0.5 可升级为 SSE/WebSocket。

## 4. 后端技术方案

后端使用 FastAPI。

核心模块：

- `auth`：注册、登录、退出、当前用户。
- `users`：用户资料。
- `spaces`：产品空间。
- `model_configs`：模型配置与 API Key 加密。
- `knowledge_bases`：空间默认知识库。
- `documents`：文档上传、解析状态、索引状态。
- `retrieval`：RAG 检索。
- `analysis_tasks`：竞品分析任务。
- `agents`：多 Agent 流水线。
- `reports`：报告与证据。
- `exports`：PDF/Word 导出，V0.5 实现。

鉴权方案：

- 用户邮箱密码注册。
- 密码使用 bcrypt 或 argon2 哈希。
- 登录后设置 httpOnly Cookie。
- 后端依赖 `get_current_user` 保护业务接口。
- 所有业务查询必须带当前用户过滤。

后台任务策略：

- V0.1-V0.4：使用后端内部任务状态和轻量后台执行。
- V0.5：如果任务耗时明显，再引入 Render Worker + Redis。
- 文档索引和报告生成都必须写入任务状态，前端通过轮询查看。

## 5. 数据库与数据模型

数据库使用 Supabase PostgreSQL。

启用扩展：

- `pgvector`
- `uuid-ossp` 或使用应用层 UUID

### users

用途：用户账号。

主要字段：

- `id`
- `email`
- `password_hash`
- `display_name`
- `is_admin`
- `created_at`
- `updated_at`

### spaces

用途：产品空间。

主要字段：

- `id`
- `user_id`
- `name`
- `industry`
- `product_direction`
- `description`
- `created_at`
- `updated_at`
- `deleted_at`

### model_configs

用途：用户模型配置。

主要字段：

- `id`
- `user_id`
- `provider_name`
- `base_url`
- `default_model`
- `encrypted_api_key`
- `api_key_hint`
- `is_active`
- `created_at`
- `updated_at`

默认配置建议：

- Provider：DeepSeek
- Base URL：`https://api.deepseek.com`
- Model：`deepseek-chat`

### knowledge_bases

用途：空间默认知识库。

主要字段：

- `id`
- `user_id`
- `space_id`
- `name`
- `description`
- `created_at`
- `updated_at`

### documents

用途：上传文档记录。

主要字段：

- `id`
- `user_id`
- `space_id`
- `knowledge_base_id`
- `filename`
- `file_type`
- `file_size`
- `storage_path`
- `status`
- `error_message`
- `created_at`
- `updated_at`

状态：

- `uploaded`
- `processing`
- `indexed`
- `failed`

### document_chunks

用途：文档切片与向量。

主要字段：

- `id`
- `user_id`
- `space_id`
- `document_id`
- `chunk_index`
- `content`
- `embedding`
- `metadata`
- `created_at`

规则：

- embedding 默认使用 DashScope `text-embedding-v4`。
- 检索必须按 `user_id + space_id` 过滤。

### analysis_tasks

用途：竞品分析任务。

主要字段：

- `id`
- `user_id`
- `space_id`
- `title`
- `industry`
- `product_direction`
- `keywords`
- `known_competitors`
- `final_competitors`
- `discovery_mode`
- `status`
- `error_message`
- `created_at`
- `completed_at`

`discovery_mode`：

- `manual`
- `semi_auto`
- `auto`

MVP 默认：`semi_auto`。

### agent_runs

用途：Agent 执行记录。

主要字段：

- `id`
- `task_id`
- `agent_name`
- `status`
- `input_json`
- `output_json`
- `error_message`
- `started_at`
- `finished_at`

### competitor_reports

用途：竞品报告。

主要字段：

- `id`
- `user_id`
- `space_id`
- `task_id`
- `title`
- `markdown_content`
- `structured_json`
- `confidence_score`
- `created_at`
- `updated_at`

### report_evidence

用途：报告证据来源。

主要字段：

- `id`
- `report_id`
- `source_type`
- `source_title`
- `source_url`
- `document_id`
- `chunk_id`
- `quote`
- `created_at`

`source_type`：

- `web`
- `private_knowledge`
- `model_inference`

## 6. Provider 抽象

Provider 用于隔离外部服务，避免业务代码绑定单一厂商。

### LLMProvider

用途：聊天、分析、报告生成。

默认实现：

- DeepSeek Provider

兼容实现：

- OpenAI-compatible Provider

核心方法：

```text
chat(messages, model, temperature) -> text/json
```

### EmbeddingProvider

用途：文档 chunk 和查询向量化。

默认实现：

- DashScope Embedding Provider

核心方法：

```text
embed(texts) -> vectors
```

### SearchProvider

用途：搜索竞品和公开资料。

默认实现：

- Bocha Search Provider

备选实现：

- Baidu Qianfan Search Provider

核心方法：

```text
search(query, limit) -> search_results
```

### ScrapeProvider

用途：抽取网页正文。

默认实现：

- Basic Web Scraper

兜底策略：

- 抓取失败时使用 SearchProvider 返回的标题、摘要、URL。

核心方法：

```text
scrape(url) -> page_text
```

## 7. RAG 技术流程

文档入库流程：

1. 用户上传文件。
2. 保存到 Supabase Storage 或本地开发 storage。
3. 创建 `documents` 记录。
4. 解析文本。
5. 文本清洗。
6. 按 800-1200 tokens 切分 chunk。
7. chunk overlap 默认 100-200 tokens。
8. 调用 DashScope embedding。
9. 写入 `document_chunks`。
10. 更新 document 状态为 indexed。

检索流程：

1. Agent 生成 RAG 查询问题。
2. 调用 DashScope embedding 生成 query vector。
3. 使用 pgvector 检索。
4. 强制过滤 `user_id` 和 `space_id`。
5. 返回 top_k，默认 8。
6. 报告中保留引用来源。

## 8. 竞品发现与资料收集流程

MVP 默认使用半自动模式：

1. 用户输入行业、产品方向、关键词。
2. 用户可以输入 0-3 个已知竞品。
3. 如果用户不输入竞品，系统进入自动发现模式。
4. 需求理解 Agent 生成候选竞品搜索问题。
5. LLM 基于用户输入补充候选竞品。
6. SearchProvider 调用博查搜索验证候选竞品。
7. 最终最多保留 3 个竞品。
8. ScrapeProvider 抓取官网、产品页、价格页、帮助中心、新闻稿。
9. 抓取失败时使用搜索摘要兜底。

规则：

- 不能只凭模型猜测确认竞品。
- 自动补充的竞品必须有搜索证据。
- 报告中要区分网页证据、私有知识库证据和模型推断。

## 9. 多 Agent 工作流

Agent 固定顺序执行：

1. 需求理解 Agent
2. 私有知识库检索 Agent
3. 公开资料收集 Agent
4. 竞品分析 Agent
5. 产品策略建议 Agent
6. 报告生成 Agent
7. 质量检查 Agent

每个 Agent 必须：

- 有明确输入。
- 有明确输出。
- 写入 `agent_runs`。
- 失败时记录 `error_message`。
- 不直接访问其他用户数据。

最终报告字段：

- 竞品定位
- 核心功能
- 目标用户
- 商业模式
- AI 能力
- 产品优劣势
- 差异化机会
- 可落地产品建议
- 风险与不确定性
- 信息来源

## 10. API 设计

接口前缀：`/api/v1`

### Auth

- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/logout`
- `GET /auth/me`

### Users

- `GET /users/me`
- `PATCH /users/me`

### Spaces

- `GET /spaces`
- `POST /spaces`
- `GET /spaces/{space_id}`
- `PATCH /spaces/{space_id}`
- `DELETE /spaces/{space_id}`

### Model Configs

- `GET /model-configs`
- `POST /model-configs`
- `PATCH /model-configs/{config_id}`
- `DELETE /model-configs/{config_id}`
- `POST /model-configs/{config_id}/test`

### Knowledge Base

- `GET /spaces/{space_id}/knowledge-base`
- `PATCH /knowledge-bases/{knowledge_base_id}`

### Documents

- `POST /spaces/{space_id}/documents`
- `GET /spaces/{space_id}/documents`
- `GET /documents/{document_id}`
- `DELETE /documents/{document_id}`
- `POST /documents/{document_id}/reindex`

### Retrieval

- `POST /spaces/{space_id}/retrieval/search`

### Analysis Tasks

- `POST /spaces/{space_id}/analysis-tasks`
- `GET /spaces/{space_id}/analysis-tasks`
- `GET /analysis-tasks/{task_id}`
- `POST /analysis-tasks/{task_id}/run`
- `POST /analysis-tasks/{task_id}/retry`

### Reports

- `GET /spaces/{space_id}/reports`
- `GET /reports/{report_id}`
- `GET /reports/{report_id}/evidence`
- `GET /reports/{report_id}/export/pdf`
- `GET /reports/{report_id}/export/docx`

## 11. 安全设计

必须遵守：

- 密码哈希保存。
- API Key 加密保存。
- `.env` 不提交仓库。
- `.env.example` 只保留变量名。
- 所有业务查询带 `user_id`。
- 空间内资源查询带 `space_id`。
- 后端统一返回中文错误结构。
- 前端不展示明文 API Key。
- 日志不记录 API Key、密码、Cookie。

错误结构：

```json
{
  "error": {
    "code": "DOCUMENT_PARSE_FAILED",
    "message": "文档解析失败",
    "details": {}
  }
}
```

## 12. 导出方案

V0.5 实现导出。

PDF：

- 优先使用前端报告页面打印样式或后端 HTML 转 PDF。
- 报告内容以 Markdown/HTML 渲染后导出。

Word：

- 后端使用 `python-docx` 生成 `.docx`。
- 保留标题、表格、列表、证据链接。

V0.4 只要求在线查看报告。

## 13. 部署方案

### Vercel

部署：

- Next.js 前端

环境变量：

- `NEXT_PUBLIC_API_BASE_URL`

### Supabase

用于：

- PostgreSQL
- pgvector
- Storage

需要配置：

- 数据库连接字符串
- Storage bucket
- pgvector 扩展

### Render

部署：

- FastAPI 后端

环境变量：

- `DATABASE_URL`
- `JWT_SECRET`
- `API_KEY_ENCRYPTION_SECRET`
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `SUPABASE_STORAGE_BUCKET`
- `BOCHA_API_KEY`
- `DASHSCOPE_API_KEY`

用户自己的 DeepSeek Key 存在数据库中，加密保存，不作为平台环境变量。

## 14. 测试计划

后端测试：

- 用户注册登录。
- 密码不会明文保存。
- 未登录无法访问业务接口。
- 用户 A 不能访问用户 B 的空间。
- 用户 A 不能访问用户 B 的文档。
- RAG 检索只返回当前用户当前空间的 chunk。
- API Key 存储后不是明文。
- 未配置模型 Key 时不能运行分析任务。
- 自动补充竞品必须有搜索证据。
- 报告字段完整。

前端测试：

- 未登录访问 `/app` 跳转登录。
- 登录后进入 Dashboard。
- 创建空间表单校验。
- 上传文档状态展示。
- 新建分析任务表单校验。
- 报告详情正常渲染。
- 模型设置页不显示明文 API Key。

集成验收：

- 用户注册登录。
- 创建“企业知识库 Copilot”产品空间。
- 上传一份示例文档。
- 完成文档索引。
- 发起半自动竞品分析任务。
- 系统生成中文报告。
- 报告包含私有知识库引用和公开资料来源。
