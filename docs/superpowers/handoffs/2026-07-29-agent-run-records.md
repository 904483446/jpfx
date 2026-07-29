# Agent 运行记录交接

日期：2026-07-29
分支：`codex/agent-run-records`
基线：`main` / `d1669ab`

## 已实现

- 增加 `analysis_agent_runs` 持久化表和 Alembic 迁移，按任务、用户、空间的复合外键保持所有权隔离。
- 每次开始或重试都会新建一轮四阶段记录：证据收集、质量检查、模型分析、报告生成。
- Runner 会更新阶段状态、起止时间和安全中文失败原因；质量门失败时，未开始的后续阶段标为“未执行”。
- 任务详情 API 返回经过任务所有权过滤的运行记录。
- 任务详情页按轮次从新到旧展示记录，以中文展示阶段和状态，不展示原始枚举、URL、证据正文、密钥或 Provider 原始错误。

## 已验证

后端：

- `python -m ruff check --no-cache .`
- `python -m ruff format --check --no-cache .`
- `python -m pytest -q`：190 passed

前端：

- `npm.cmd test`：30 个文件、113 项测试通过。
- `npm.cmd run check:routes`
- `npx.cmd tsc --noEmit`
- `npm.cmd run lint`
- `npm.cmd run build`

## 未验证边界

- 未用真实模型 Provider 执行分析；测试只覆盖受控替身与安全失败路径。
- 未做真实浏览器端到端验收、CI 或部署环境验证。
- 需要在含有真实任务数据的本地环境运行迁移后，人工查看任务详情页的视觉效果。

## 建议收尾

1. 由用户检查变更后推送分支并创建 PR。
