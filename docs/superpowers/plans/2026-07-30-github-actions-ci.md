# GitHub Actions CI Implementation Plan

**Goal:** 为 push 与 Pull Request 提供前后端自动质量门禁。

### Task 1: 添加 CI 工作流

**Files:**
- Create: `.github/workflows/ci.yml`

- [ ] 定义 `push` 与针对 `main` 的 `pull_request` 触发器，并设置最小只读权限。
- [ ] 添加 backend job：Python 3.12、pgvector PostgreSQL 服务、CI 测试环境变量、`ruff check`、`ruff format --check`、`pytest -q`。
- [ ] 添加 frontend job：Node、`npm ci`、Vitest、路由检查、TypeScript、lint、build。
- [ ] 不使用 `.env`、GitHub Secrets、部署命令或外部 Provider。

### Task 2: 本地静态验证

**Files:**
- Modify: `docs/superpowers/handoffs/2026-07-30-github-actions-ci.md`

- [ ] 用 YAML 解析器验证工作流语法。
- [ ] 运行前端现有门禁，确认工作流命令与本地命令一致。
- [ ] 检查工作流不包含敏感变量、发布或部署步骤。
- [ ] 记录 GitHub 首次云端执行仍需在推送 PR 后单独确认。
