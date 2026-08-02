# GitHub Showcase README Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 JPFX 根目录 README 改造成作品集优先、可直接体验且不夸大验证状态的 GitHub 项目首页。

**Architecture:** 仅重构 `README.md` 的信息架构，继续复用 `docs/assets/v1-showcase` 中已有的脱敏截图和根目录 `.env.example`。不改动前后端、数据库、部署配置或外部 Provider 调用；GitHub About 元数据作为用户在网页端完成的独立交接项。

**Tech Stack:** GitHub Flavored Markdown、Mermaid、GitHub Actions workflow badge、现有 Next.js/FastAPI/Supabase 部署事实。

---

### Task 1: 重写作品集优先的仓库首页

**Files:**
- Modify: `README.md`
- Reuse: `docs/assets/v1-showcase/login-v2.png`
- Reuse: `docs/assets/v1-showcase/dashboard-v2.png`
- Reuse: `docs/assets/v1-showcase/task-or-report-v2.png`
- Reuse: `docs/assets/v1-showcase/settings-v2.png`
- Reference: `.github/workflows/ci.yml`
- Reference: `.env.example`

- [ ] **Step 1: 用以下首屏替换旧的“本地实现/未提供公开 Demo”定位**

```markdown
# JPFX｜AI 竞品研究工作台

> 面向 AI 产品经理的私有竞品研究工作台：将资料沉淀、RAG 检索、竞品分析任务、证据归档和报告导出串成一条可追溯工作流。

[在线体验](https://jpfx.vercel.app/) · [产品需求](PRD.md) · [技术设计](TECH_SPEC.md) · [任务拆分](TASK_BREAKDOWN.md)

![CI](https://github.com/904483446/jpfx/actions/workflows/ci.yml/badge.svg)
```

删除旧首屏中“公开 Demo 尚未提供”“生产部署属于后续验证”的表述。不要新增准确性无法确认的 badge、星标数、用户数或性能数据。

- [ ] **Step 2: 写入产品闭环和正式环境状态**

在首屏之后增加 `## 产品闭环`，使用以下流程文字和 Mermaid 图：

```text
产品空间 → 私有资料 → 向量索引与检索 → 竞品分析任务 → 证据与报告归档 → PDF / DOCX 导出
```

图中准确标注：浏览器请求由 Vercel 的 `/api` rewrite 转发至 Railway FastAPI；后端使用 Supabase PostgreSQL + pgvector 和私有 `jpfx-documents` Storage bucket；DashScope、DeepSeek、Bocha 仅在对应 Key 配置后调用。

紧随其后增加 `## 正式环境已验证`，只列出：健康检查、注册登录与 Cookie 会话、工作空间、私有资料上传、跨 Railway 重部署的资料保留、DashScope 文档索引、文档删除。明确注明 DeepSeek 分析和 Bocha 检索尚未完成真实生产调用验收。

- [ ] **Step 3: 将现有截图组织为可扫描的产品界面区**

增加 `## 产品界面`，按以下顺序使用已有图片和一句中文说明：

```markdown
### 登录与安全会话
![登录页](docs/assets/v1-showcase/login-v2.png)

### 工作台与空间入口
![工作台](docs/assets/v1-showcase/dashboard-v2.png)

### 分析任务与报告
![任务与报告](docs/assets/v1-showcase/task-or-report-v2.png)

### 用户级模型设置
![模型设置](docs/assets/v1-showcase/settings-v2.png)
```

保留图片“真实脱敏界面截图”的说明；不添加录屏、虚构任务结果或真实 API Key 截图。

- [ ] **Step 4: 重组能力、技术架构与安全边界**

将旧的长能力表拆为三个小表：

```text
已实现并已验证：认证、空间、上传/删除、私有 Storage、向量索引、报告导出。
已实现且需配置：DashScope 向量、DeepSeek 分析、Bocha 检索。
安全边界：httpOnly Cookie、用户/空间隔离、私有 bucket、后端专用 Secret Key。
```

在 `## 技术架构` 中保留前端、后端、数据和部署四行，并使用下列真实服务名称：Vercel、Railway、Supabase PostgreSQL + pgvector、Supabase Storage。不得写入任何域名之外的真实配置值。

- [ ] **Step 5: 后置并压缩本地运行与测试信息**

将 `## 本地启动` 移到截图、能力和架构之后，并保持下列原则：

```text
1. 仅从 .env.example 创建本地 .env；不提交真实凭据。
2. docker compose up -d --wait db
3. services/api 中执行 alembic upgrade head 并启动 uvicorn。
4. apps/web/.env.local 配置本地 NEXT_PUBLIC_API_BASE_URL。
5. apps/web 中执行 npm.cmd ci 与 npm.cmd run dev。
```

保留后端 Ruff/pytest 与前端 test/routes/tsc/lint/build 命令，但删除已过期的“生产部署未验证”和“公开 Demo 未提供”段落。

- [ ] **Step 6: 静态验证 README 内容与资产引用**

运行：

```powershell
$readme = Get-Content -LiteralPath README.md -Raw
$required = @(
  'https://jpfx.vercel.app/',
  'actions/workflows/ci.yml/badge.svg',
  'docs/assets/v1-showcase/login-v2.png',
  'docs/assets/v1-showcase/dashboard-v2.png',
  'docs/assets/v1-showcase/task-or-report-v2.png',
  'docs/assets/v1-showcase/settings-v2.png',
  'DeepSeek',
  'Bocha'
)
$required | ForEach-Object { if (-not $readme.Contains($_)) { throw "README 缺少: $_" } }
@(
  'docs/assets/v1-showcase/login-v2.png',
  'docs/assets/v1-showcase/dashboard-v2.png',
  'docs/assets/v1-showcase/task-or-report-v2.png',
  'docs/assets/v1-showcase/settings-v2.png'
) | ForEach-Object { if (-not (Test-Path -LiteralPath $_)) { throw "截图不存在: $_" } }
if ($readme -match '公开 Demo 尚未提供|生产部署.*后续验证') { throw 'README 仍含过期部署表述' }
```

预期：命令无输出、退出码为 0。

- [ ] **Step 7: 检查差异并提交**

运行：

```powershell
git diff --check
git diff -- README.md
git add README.md
git commit -m "docs: polish GitHub project showcase"
```

预期：无空白错误；提交只包含 README 改动。

### Task 2: 交接 GitHub 页面元数据设置

**Files:**
- No repository file changes

- [ ] **Step 1: 在 GitHub 仓库 About 中设置展示信息**

用户在 GitHub 仓库主页右侧 `About` → 齿轮中填写：

```text
Description: 面向 AI 产品经理的私有竞品研究工作台，支持资料沉淀、RAG 检索、竞品分析和证据化报告导出。
Website: https://jpfx.vercel.app/
Topics: ai-product-management, competitive-intelligence, rag, fastapi, nextjs, supabase, pgvector
```

不在 Description 或 Topics 中写“已验证所有 AI Provider”“无代码”“自动取代研究员”等不可证实的营销表述。

- [ ] **Step 2: 在 GitHub 页面检查 README 渲染和入口**

打开仓库主页，确认：在线体验链接可打开、CI badge 有状态、四张截图可显示、Mermaid 图渲染、`.env.example` 没有被展示为真实配置。

- [ ] **Step 3: 记录验收结论**

在 PR 描述中记录：README 静态校验结果、GitHub 页面渲染结果和是否完成 About 设置；不附任何 Key、Cookie、数据库 URI 或截图中的敏感值。
