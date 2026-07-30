# GitHub Actions CI 设计

## 目标

在每次推送与 Pull Request 时，自动验证 JPFX 的后端、数据库迁移与前端构建质量；不部署、不发布、不调用外部 Provider，也不使用真实环境凭据。

## 工作流

新增单个 `.github/workflows/ci.yml`，触发条件为所有分支的 `push` 与针对 `main` 的 `pull_request`。工作流分为互不依赖的两个 job：`backend` 与 `frontend`，任一失败即在 GitHub Checks 中失败。

## 后端 job

- 使用 Ubuntu、Python 3.12 和 PostgreSQL 16 + pgvector 服务容器。
- 服务数据库、用户和密码均为 CI 专用测试值；通过 `TEST_DATABASE_URL` 注入，不读取仓库 `.env`。
- 安装 `services/api` 的项目与 dev 依赖后，顺序运行 Ruff 检查、Ruff 格式检查与 `pytest -q`。
- 测试夹具自行执行 Alembic `upgrade head`，因此同时覆盖当前迁移能在空测试库应用的边界。

## 前端 job

- 使用 Ubuntu 和锁定的 Node 版本，执行 `npm ci`。
- 顺序运行 Vitest、路由检查、`tsc --noEmit`、ESLint 和生产构建。
- 不创建 `.env.local`；这些静态与组件测试不需要调用真实 API。

## 安全与非目标

- 不读取、写入或输出真实 `.env`、Cookie、Token、用户 API Key、Provider Key 或数据库连接串。
- 不运行 Docker Compose，不部署到 Vercel/Render，不发布包，不创建 GitHub Release。
- 不调用 DashScope、DeepSeek 或 Bocha；测试继续使用既有受控替身。

## 验收标准

- `.github/workflows/ci.yml` 通过 YAML 语法与本地静态检查。
- 工作流仅使用 CI 测试环境变量，不含敏感值或 `secrets` 引用。
- 前端与后端命令和仓库 README 的本地门禁保持一致。
- GitHub 首次运行结果单独记录；本地创建工作流文件不等同于 GitHub 云端已执行。
