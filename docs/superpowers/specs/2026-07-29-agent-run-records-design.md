# Agent 运行记录设计

## 目标

让竞品分析任务的每一轮执行都能被用户回看：四个固定阶段何时开始和结束、是否成功、失败在哪一步，以及重试后发生了什么。记录必须保持任务、用户和产品空间隔离，不得保存或返回模型请求、原始证据、URL、密钥或 Provider 原始错误。

本设计完成 V0.5 的“Agent 运行记录”和“任务页显示每个 Agent 状态”两项；此前已经合并的证据质量门成为其中一个可审计阶段。

## 范围与非目标

范围：

- 为每次开始或重试创建一轮持久化阶段记录。
- 记录证据采集、证据质量检查、模型分析和报告生成四个固定阶段。
- 在既有任务轮询响应中返回记录，在既有任务详情页显示运行历史。
- 复用现有安全中文错误文案和 `AnalysisTask` 状态机。

非目标：

- 不引入 Redis、独立 Worker、消息队列、实时推送或新的外部 Provider 调用。
- 不记录每个函数调用、模型请求/响应、原始证据、URL、密钥或 Provider 内部错误。
- 不改变报告详情、导出契约、候选发现流程或现有任务总进度条语义。
- 不增加日志下载、日志管理页或用户可编辑的 Agent 编排。

## 数据模型

新增 `analysis_agent_runs` 表和 `AnalysisAgentRun` 模型：

| 字段 | 规则 |
| --- | --- |
| `id` | UUID 主键。 |
| `task_id` | 指向 `analysis_tasks`，删除任务时级联删除。 |
| `user_id` / `space_id` | 与任务创建时的归属快照一致，用于查询时双重隔离。 |
| `attempt` | 从 1 开始的正整数；每次重新分析加 1。 |
| `agent_key` | `evidence_collection`、`quality_check`、`model_analysis`、`report_generation` 之一。 |
| `status` | `queued`、`running`、`completed`、`failed`、`skipped` 之一。 |
| `started_at` / `completed_at` | 仅在实际开始或结束时写入 UTC 时间。 |
| `error_message` | 仅 `failed` 记录可填，保存安全中文原因。 |

对 `(task_id, attempt, agent_key)` 建立唯一约束；对 `(task_id, attempt)` 建立排序索引。`user_id`、`space_id` 不接受客户端输入，只从受所有权校验的任务复制。

## 执行状态流

当 `queue_analysis_task` 或 `retry_analysis_task` 使任务进入 `queued` 时，服务在同一数据库事务中计算该任务最大 `attempt + 1`，创建四条 `queued` 记录，并按固定阶段顺序保存。API 的 202 或重试响应因此能立即呈现待执行步骤。

`analysis_runner` 仍将任务从 `queued` 置为 `running`，并继续维护现有 `AnalysisTask.stage`，以保持现有进度条与客户端兼容。runner 按以下顺序推进同一轮的记录：

1. `evidence_collection`：私有知识检索并保存私有证据。
2. `quality_check`：调用既有 `validate_evidence_quality`。
3. `model_analysis`：读取已配置密钥、调用 Provider、校验模型 JSON。
4. `report_generation`：组装结构化内容并保存 `CompetitorReport`。

进入阶段时，将该记录置为 `running` 并写入 `started_at`；阶段成功后置为 `completed` 并写入 `completed_at`。任务成功时四条记录均为 `completed`，并继续使用既有 `AnalysisTask.status="completed"` 和完成时间。

任何阶段出现 `AppError` 或未预期异常时，当前运行记录置为 `failed`；其错误消息与任务已有安全错误消息保持一致。随后将本轮其余 `queued` 记录置为 `skipped` 并写入结束时间，再沿用既有 `_persist_failure` 将任务置为 `failed`。质量门失败仍绝不调用 Provider 或创建报告。

重试不会覆盖旧记录：新轮次从 `attempt + 1` 重新创建四条记录，旧轮次只读保留。

## API 与权限

不新增独立运行日志端点。扩展现有 `AnalysisTaskResponse`，增加 `agent_runs` 数组；`GET /analysis-tasks/{task_id}`、运行和重试响应都通过既有 `_task_response` 填充它。

查询固定为当前已获取任务的 `task_id + user_id + space_id`，按 `attempt` 升序、固定 Agent 顺序返回。响应只包含：`attempt`、`agent_key`、`status`、`started_at`、`completed_at` 和 `error_message`。不会返回外部 URL、证据引文、模型配置或任何密钥字段。

## 前端展示

`AnalysisTaskStatus` 保留现有总进度条，并新增“Agent 运行记录”区块：

- 使用固定中文标签：证据采集、证据质量检查、模型分析、报告生成。
- 每轮以“第 N 次运行”分组；最新轮次默认展开，旧轮次保持可读的只读列表。
- 每项展示状态、开始/结束时间；失败显示安全错误原因，`skipped` 显示“未执行”。
- 前端不直接展示后端枚举值，也不从任务或报告 JSON 推断敏感详情。

现有两秒轮询不变，因此运行记录随现有任务状态自动刷新；完成或失败后仍停止轮询。

## 测试与验收

后端测试先覆盖：

- 迁移创建表、唯一约束和任务级联删除。
- 首次运行创建四条 `attempt=1` 的 `queued` 记录。
- 任务读取只返回当前用户和空间的记录，跨用户/空间无法读取。
- runner 成功时四阶段按顺序完成；质量门失败时当前阶段失败、后续阶段跳过，Provider 不被调用。
- 重试新增 `attempt=2` 而不改写第一轮记录。
- 响应不包含模型请求、URL、证据正文、密钥或 Provider 原始错误。

前端测试先覆盖：

- 当前轮与历史轮的中文阶段和状态展示。
- `failed` 显示安全错误，`skipped` 显示“未执行”。
- 原始 `agent_key` / `status` 枚举不直接出现在页面中。
- 原有轮询、失败重试和总进度条测试保持通过。

完整门禁继续使用后端 pytest、Ruff/format，以及前端 Vitest、路由检查、TypeScript、lint 和生产构建。真实 Provider、浏览器端到端流程、部署和 CI 不作为本次验收结论。
