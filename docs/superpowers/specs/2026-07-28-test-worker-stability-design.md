# 前端测试 Worker 稳定性设计

## 背景与证据

`apps/web` 的全量 Vitest 运行在 Windows 环境使用默认并发度时，曾偶发使
`components/app/analysis-task-create.test.tsx` 中的异步交互测试超过 5 秒。
同一套测试在显式 `--maxWorkers=1` 与 `--maxWorkers=2` 下均通过（109 个测试），
且该测试文件单独运行通过。因此此处处理的是 jsdom worker 的本机资源争用，
不是改变业务行为或放宽测试断言。

## 方案比较

1. **默认固定为 2 个 worker（采用）**：在 `vitest.config.ts` 的 `test` 配置中设置
   `maxWorkers: 2`。日常 `npm.cmd test` 即稳定，仍保留两个并发 worker。
2. **仅依赖人工命令参数**：不改仓库，但每位开发者和 CI 都容易遗漏参数，不能保证
   默认质量门禁稳定。
3. **提高该测试的超时**：表面上减少失败，但会掩盖实际的资源争用并降低对真实慢测
   试的敏感度；不采用。

## 设计

仅修改 `apps/web/vitest.config.ts`：在现有 `test` 配置中增加 `maxWorkers: 2`。
不修改测试案例、业务代码、测试超时、依赖版本、CI 或 `.env` 文件。

Vitest 在执行 `npm.cmd test` 时读取该配置，因此所有本地默认测试运行都受同一上限
约束；使用者仍可在命令行显式覆盖该值，用于诊断或更高资源的环境。

## 验收与边界

- `npm.cmd test` 连续运行至少三次，均为 109/109 通过。
- 继续运行 `npm.cmd run check:routes`、`npx.cmd tsc --noEmit`、`npm.cmd run lint` 与
  `npm.cmd run build`，以确认配置改动未影响其他前端门禁。
- 不将这组本地结果表述为浏览器、后端、Provider、Docker 或部署环境验证。
