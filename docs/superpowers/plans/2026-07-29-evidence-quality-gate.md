# 证据质量门 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在模型调用前阻断不具备可追溯证据的分析任务，并把通过摘要写入报告快照与任务进度。

**Architecture:** 新建无副作用的 `evidence_quality` 服务，接收已经按任务、用户和空间过滤的 `TaskEvidence`，返回计数摘要或抛出安全的 `AppError`。`analysis_runner` 在持久化检索证据后调用该服务，只有通过才调用模型并创建报告；前端只新增 `quality_checking` 阶段映射。

**Tech Stack:** Python 3、Pydantic、SQLAlchemy、FastAPI、pytest、Next.js、React、TypeScript、Vitest。

---

## 文件结构

- Create: `services/api/app/services/evidence_quality.py` — 纯证据规则、URL 验证和质量摘要。
- Create: `services/api/tests/test_evidence_quality.py` — 纯服务的 RED/GREEN 覆盖。
- Modify: `services/api/app/core/errors.py` — 增加安全的质量失败 `AppError` 工厂。
- Modify: `services/api/app/services/analysis_runner.py` — 在模型调用前运行质量门、持久化摘要和失败原因。
- Modify: `services/api/tests/test_analysis_runner.py` — 覆盖 runner 的阻断与成功快照。
- Modify: `apps/web/components/app/analysis-task-status.tsx` — 展示 `quality_checking` 阶段。
- Modify: `apps/web/components/app/analysis-task-status.test.tsx` — 覆盖阶段标签和进度位置。
- Create: `docs/superpowers/handoffs/2026-07-29-evidence-quality-gate.md` — 记录命令、结果和未验证边界。

### Task 1: 先以单元测试定义证据质量规则

**Files:**
- Create: `services/api/tests/test_evidence_quality.py`
- Create: `services/api/app/services/evidence_quality.py`
- Modify: `services/api/app/core/errors.py`

- [x] **Step 1: 写失败测试**

  在 `test_evidence_quality.py` 创建使用 `SimpleNamespace` 的最小证据工厂，并加入：

  ```python
  def test_validate_evidence_quality_counts_valid_web_and_private_evidence():
      summary = validate_evidence_quality([
          evidence("web", source_url="https://example.com/source"),
          evidence("private_knowledge", document_id=uuid4(), chunk_id=uuid4(), knowledge_base_id=uuid4()),
      ])
      assert summary.model_dump() == {
          "status": "passed", "evidence_count": 2,
          "web_evidence_count": 1, "private_knowledge_evidence_count": 1,
      }

  @pytest.mark.parametrize("source_url", [None, "javascript:alert(1)", "file:///tmp/a", "https://@"])
  def test_validate_evidence_quality_rejects_untraceable_web_evidence(source_url):
      with pytest.raises(AppError, match="网页证据缺少有效来源链接"):
          validate_evidence_quality([evidence("web", source_url=source_url)])

  def test_validate_evidence_quality_rejects_private_evidence_without_all_links():
      with pytest.raises(AppError, match="私有知识库证据缺少文档关联"):
          validate_evidence_quality([evidence("private_knowledge", document_id=uuid4())])
  ```

- [x] **Step 2: 确认测试按预期失败**

  从 `services/api` 运行：

  ```powershell
  .\.venv\Scripts\python.exe -m pytest tests/test_evidence_quality.py -q
  ```

  预期：FAIL，原因是 `evidence_quality` 模块或 `validate_evidence_quality` 尚不存在。

- [x] **Step 3: 实现最小纯服务与错误工厂**

  新服务导出以下稳定接口：

  ```python
  class EvidenceQualitySummary(BaseModel):
      status: Literal["passed"] = "passed"
      evidence_count: int
      web_evidence_count: int
      private_knowledge_evidence_count: int

  def validate_evidence_quality(evidence: Sequence[TaskEvidence]) -> EvidenceQualitySummary:
      ...
  ```

  仅接受 `web` 与 `private_knowledge`；空列表、未知类型、空标题、网页 URL 不安全、私有
  证据缺少三项关联均调用 `evidence_quality_failed(message)`。该错误返回
  `code="EVIDENCE_QUALITY_FAILED"`、安全中文 `message` 与 HTTP 422；URL 使用
  `urlparse` 检查 `http/https + hostname`。

- [x] **Step 4: 确认纯服务变绿**

  ```powershell
  .\.venv\Scripts\python.exe -m pytest tests/test_evidence_quality.py -q
  ```

  预期：所有新增规则测试通过。

- [x] **Step 5: 提交纯质量服务**

  ```powershell
  git add services/api/app/core/errors.py services/api/app/services/evidence_quality.py services/api/tests/test_evidence_quality.py
  git commit -m "feat: validate report evidence quality"
  ```

### Task 2: 在 runner 中阻断模型调用并保存摘要

**Files:**
- Modify: `services/api/app/services/analysis_runner.py:99-179`
- Modify: `services/api/tests/test_analysis_runner.py:119-225`

- [x] **Step 1: 写 runner 失败测试**

  在既有 runner 测试中添加：

  ```python
  def test_analysis_runner_fails_without_evidence_before_calling_provider(database_session, monkeypatch):
      user, space = _create_owner_and_space(database_session)
      task = _create_queued_task(database_session, user, space)
      database_session.query(TaskEvidence).filter_by(task_id=task.id).delete()
      database_session.commit()
      provider = FakeDeepSeekProvider()
      monkeypatch.setattr("app.services.analysis_runner.get_deepseek_api_key", lambda *_: "test-key")

      with pytest.raises(AppError, match="没有可追溯证据"):
          run_analysis_task(task.id, session_factory=_background_session_factory(database_session), embedding_provider=object(), provider_factory=lambda _: provider)

      assert provider.prompts == []
      assert database_session.query(CompetitorReport).filter_by(task_id=task.id).count() == 0
  ```

  同时扩展现有成功测试，断言：

  ```python
  assert report.structured_json["quality_check"] == {
      "status": "passed", "evidence_count": 2,
      "web_evidence_count": 1, "private_knowledge_evidence_count": 1,
  }
  ```

- [x] **Step 2: 确认 runner 测试失败**

  ```powershell
  .\.venv\Scripts\python.exe -m pytest tests/test_analysis_runner.py -q
  ```

  预期：空证据案例目前仍会调用 Fake Provider，且成功报告尚无 `quality_check`。

- [x] **Step 3: 最小接线 runner**

  在现有证据查询之后、`provider_factory(api_key).complete_json(...)` 之前：

  ```python
  task.stage = "quality_checking"
  database_session.commit()
  quality_check = validate_evidence_quality(evidence)
  task.stage = "analyzing"
  database_session.commit()
  ```

  在 `ReportContent` 中显式新增 `quality_check: EvidenceQualitySummary` 字段，然后创建
  `ReportContent` 时增加：

  ```python
  quality_check=quality_check.model_dump()
  ```

  让 `_persist_failure` 接收可选 `message`；捕获 `AppError as error` 时只为
  `EVIDENCE_QUALITY_FAILED` 保存 `error.message`，其他失败维持既有通用信息，避免改变
  Provider 错误暴露边界。

- [x] **Step 4: 确认 runner 测试变绿**

  ```powershell
  .\.venv\Scripts\python.exe -m pytest tests/test_analysis_runner.py tests/test_evidence_quality.py -q
  ```

  预期：质量失败不调用模型且不创建报告；有效证据的报告含摘要；既有失败语义继续通过。

- [x] **Step 5: 提交 runner 接线**

  ```powershell
  git add services/api/app/services/analysis_runner.py services/api/tests/test_analysis_runner.py
  git commit -m "feat: gate reports on traceable evidence"
  ```

### Task 3: 显示质量检查阶段并完成回归

**Files:**
- Modify: `apps/web/components/app/analysis-task-status.tsx:9-34`
- Modify: `apps/web/components/app/analysis-task-status.test.tsx:42-55`

- [x] **Step 1: 写前端失败测试**

  在参数化阶段测试中加入：

  ```tsx
  ["quality_checking", "证据质量检查", "证据质量检查"]
  ```

  并断言进度列表能显示“证据质量检查”。

- [x] **Step 2: 确认前端测试失败**

  从 `apps/web` 运行：

  ```powershell
  npm.cmd test -- components/app/analysis-task-status.test.tsx
  ```

  预期：FAIL，因为当前没有 `quality_checking` 映射或时间线条目。

- [x] **Step 3: 最小 UI 实现**

  在 `stages` 中于“模型调用”之前加入“证据质量检查”；在 `backendStageLabels` 增加：

  ```ts
  quality_checking: "证据质量检查",
  ```

  `stagePosition` 为该后端阶段返回对应新索引。不得新建 API、报告详情组件或日志页。

- [x] **Step 4: 确认前端测试变绿**

  ```powershell
  npm.cmd test -- components/app/analysis-task-status.test.tsx
  ```

  预期：通过，且既有失败、重试与轮询测试保持通过。

- [x] **Step 5: 跑完整质量门并提交 UI**

  ```powershell
  cd ..\..\services\api
  .\.venv\Scripts\python.exe -m ruff check --no-cache .
  .\.venv\Scripts\python.exe -m ruff format --check --no-cache .
  .\.venv\Scripts\python.exe -m pytest -q
  cd ..\..\apps\web
  npm.cmd test
  npm.cmd run check:routes
  npx.cmd tsc --noEmit
  npm.cmd run lint
  npm.cmd run build
  ```

  预期：全部退出码 0。若新 worktree 缺少前端依赖，先运行 `npm.cmd ci`，不修改锁文件。

  ```powershell
  git add apps/web/components/app/analysis-task-status.tsx apps/web/components/app/analysis-task-status.test.tsx
  git commit -m "feat: show evidence quality stage"
  ```

### Task 4: 记录边界并交付

**Files:**
- Create: `docs/superpowers/handoffs/2026-07-29-evidence-quality-gate.md`

- [x] **Step 1: 写入验证记录**

  记录每个后端/前端命令与结果，并明确：未调用真实 Provider，未验证生产部署或新报告的
  浏览器端到端流程，且本次没有数据库迁移。

- [x] **Step 2: 最终差异检查和提交**

  ```powershell
  git diff --check main...HEAD
  git status --short --branch
  git add docs/superpowers/handoffs/2026-07-29-evidence-quality-gate.md docs/superpowers/plans/2026-07-29-evidence-quality-gate.md
  git commit -m "docs: record evidence quality gate"
  ```

  预期：差异仅包含质量服务、runner 接线、对应测试、任务阶段 UI 与三份文档；不包含
  `.env`、密钥、锁文件或迁移。
