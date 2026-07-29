# 证据质量门设计

## 目标

在竞品分析任务调用模型、创建报告之前，阻断没有可追溯来源的报告，并让用户在任务进度中
看到“证据质量检查”阶段。通过的报告保留一份不含原文和密钥的质量摘要，供后续详情页或
导出使用。

## 范围

本次只实现当前 V0.5 的第一项：证据完整性与来源可追溯检查。复用现有
`TaskEvidence`、`AnalysisTask.stage` 和 `CompetitorReport.structured_json`，不新增
数据库表、迁移、Agent 日志表、Provider 调用、重试语义或报告详情页布局。

质量检查只消费已按 `task_id + user_id + space_id` 查询出的 `web` 与
`private_knowledge` 证据；`model_inference` 不能作为通过质量门的证据。

## 质量规则

以下任一条件不满足即失败：

1. 至少存在一条允许的证据。
2. 每条网页证据有非空标题，且 `source_url` 是带 hostname 的 `http` 或 `https` URL。
3. 每条私有知识库证据有非空标题，并关联 `document_id`、`chunk_id` 和
   `knowledge_base_id`。
4. 检查输入只来自当前任务、当前用户和当前空间；不相信模型返回的自报来源。

失败时任务保持既有 `failed` 状态机语义，不创建 `CompetitorReport`，也不调用模型。
任务错误信息使用用户可读、不会泄露 URL、文档内容或凭据的失败原因，例如“证据质量检查
未通过：没有可追溯证据”。

## 后端设计

新增一个纯函数式的 `evidence_quality` 服务，输入允许的 `TaskEvidence` 列表，输出
`EvidenceQualitySummary`：

```python
{
  "status": "passed",
  "evidence_count": 3,
  "web_evidence_count": 2,
  "private_knowledge_evidence_count": 1,
}
```

它不访问数据库、不写状态、不调用模型，因而可独立进行单元测试。URL 校验采用与导出
同一安全规则：仅允许 `http/https` 且必须存在 hostname；不允许 `javascript:`、`file:`、
`data:`、无 hostname 或畸形 URL。

`analysis_runner` 在获取并持久化证据后先将任务阶段写为 `quality_checking`，调用该服务，
然后才设置 `analyzing` 并调用模型。通过后将摘要写入
`structured_json["quality_check"]`，同时保留既有 `structured_json["evidence"]` 快照。
失败由专用 `AppError` 进入既有失败持久化路径，并保留安全、具体的失败消息。

## 前端设计

任务状态组件把 `quality_checking` 映射为“证据质量检查”，并在进度列表中加入该阶段。
不新增网络请求，不读取报告 JSON，不显示证据原文或 URL；失败任务继续复用既有错误与
“重新分析”入口。

## 测试与验收

先为纯服务写失败测试，再实现最小校验；覆盖空证据、无效网页 URL、缺少私有关联和
有效混合证据。随后为 runner 写集成测试，证明：

- 质量通过时模型调用一次、报告含质量摘要、任务完成。
- 质量失败时模型不被调用、报告不存在、任务失败并带安全原因。
- 跨用户、跨空间或 `model_inference` 证据不会被 runner 作为通过依据。

前端组件测试覆盖 `quality_checking` 标签。完整后运行后端 pytest、Ruff、前端 Vitest、
路由检查、类型检查、lint 和构建；真实 Provider、部署和浏览器新报告流程仍不作为本次
验收结论。
