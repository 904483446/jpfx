# 前端测试 Worker 稳定性 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 让 `apps/web` 的默认 Vitest 全量测试在 Windows/jsdom 环境以最多两个 worker 稳定运行。

**Architecture:** Vitest 已统一从 `apps/web/vitest.config.ts` 读取 `test` 配置。仅在该对象中声明 `maxWorkers: 2`，因此 `npm.cmd test` 自动继承限制，无需修改每条命令或测试案例。测试的断言和 5 秒默认超时保持不变，避免将资源争用伪装为更宽松的质量门槛。

**Tech Stack:** Next.js 16、React 19、Vitest 4、jsdom、TypeScript、npm（Windows）。

---

## 文件结构

- 修改：`apps/web/vitest.config.ts` — 前端 Vitest 的共享运行配置；新增唯一的并发上限。
- 新增：`docs/superpowers/specs/2026-07-28-test-worker-stability-design.md` — 已提交的设计和边界。
- 新增：`docs/superpowers/plans/2026-07-28-test-worker-stability.md` — 本实施计划；不进入产品运行时。

### Task 1: 确认基线并添加最小配置

**Files:**
- Modify: `apps/web/vitest.config.ts:8-11`
- Test: `apps/web/components/app/analysis-task-create.test.tsx`

- [x] **Step 1: 以已验证的稳定参数确认测试基线**

  从 `apps/web` 运行：

  ```powershell
  npm.cmd test -- --maxWorkers=2
  ```

  预期：109 个测试全部通过。该命令验证原有测试逻辑在低并发时正确，不修改测试案例。

- [x] **Step 2: 运行默认全量命令作为问题复现检查**

  从 `apps/web` 运行：

  ```powershell
  npm.cmd test
  ```

  预期：此历史问题是偶发的；若复现，失败表现为 `analysis-task-create.test.tsx` 的
  `creates a task without any known competitor` 超过 5 秒。无论本次是否复现，都不改该
  测试、断言或超时。

- [x] **Step 3: 写入最小实现**

  将 `apps/web/vitest.config.ts` 的 `test` 对象改为：

  ```ts
  test: {
    environment: "jsdom",
    setupFiles: ["./test/setup.ts"],
    maxWorkers: 2,
  },
  ```

  只新增 `maxWorkers: 2`；其余解析别名、测试环境和初始化文件保持原样。

- [x] **Step 4: 验证默认命令已读取配置**

  从 `apps/web` 连续三次运行：

  ```powershell
  npm.cmd test
  ```

  预期：每次均为 109/109 通过，命令无需 `--maxWorkers` 参数。

- [x] **Step 5: 提交最小配置改动**

  ```powershell
  git add apps/web/vitest.config.ts
  git commit -m "test: limit frontend vitest workers"
  ```

### Task 2: 运行其余前端质量门禁并记录范围

**Files:**
- Modify: `apps/web/vitest.config.ts:8-12`
- Test: `apps/web/scripts/check-routes.mjs`

- [x] **Step 1: 检查路由约束**

  从 `apps/web` 运行：

  ```powershell
  npm.cmd run check:routes
  ```

  预期：退出码 0。

- [x] **Step 2: 类型检查**

  从 `apps/web` 运行：

  ```powershell
  npx.cmd tsc --noEmit
  ```

  预期：退出码 0，无 TypeScript 错误。

- [x] **Step 3: 静态检查**

  从 `apps/web` 运行：

  ```powershell
  npm.cmd run lint
  ```

  预期：退出码 0。

- [x] **Step 4: 生产构建检查**

  从 `apps/web` 运行：

  ```powershell
  npm.cmd run build
  ```

  预期：退出码 0；这仅验证前端构建，不等同于浏览器、后端、Provider、Docker 或部署验证。

- [x] **Step 5: 查看最终差异并提交计划文档**

  ```powershell
  git diff --check main...HEAD
  git status --short --branch
  git add docs/superpowers/plans/2026-07-28-test-worker-stability.md
  git commit -m "docs: plan frontend test worker stability"
  ```

  预期：与 `main` 的差异仅包含设计文档、计划文档和 `maxWorkers: 2` 配置；不包含
  `.env`、依赖锁文件或业务代码。
