# Agent 杩愯璁板綍 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** 涓烘瘡涓€娆＄珵鍝佸垎鏋愭寔涔呭寲鍥涗釜鍥哄畾闃舵鐨勫畨鍏ㄨ繍琛岃褰曪紝骞跺湪浠诲姟璇︽儏椤垫樉绀哄綋鍓嶄笌鍘嗗彶灏濊瘯銆?
**Architecture:** `AnalysisAgentRun` 浠ヤ换鍔°€佺敤鎴峰拰绌洪棿涓烘墍鏈夋潈杈圭晫銆傚紑濮嬩笌閲嶈瘯鍦ㄥ悓涓€浜嬪姟涓垱寤烘柊灏濊瘯鐨勫洓鏉?queued 璁板綍锛涚嫭绔嬫湇鍔¤礋璐ｉ樁娈佃浆鎹紝runner 鍙皟鐢ㄥ畠銆傛棦鏈変换鍔¤疆璇㈠搷搴旇繑鍥炲彈杩囨护璁板綍锛屽墠绔彧娓叉煋涓枃鏍囩銆佺姸鎬併€佹椂闂村拰瀹夊叏閿欒娑堟伅銆?
**Tech Stack:** Python 3銆丼QLAlchemy銆丄lembic銆丗astAPI銆丳ydantic銆乸ytest銆丯ext.js銆丷eact銆乀ypeScript銆乂itest銆乀esting Library銆?
---

## 鏂囦欢缁撴瀯

- Create: `services/api/app/models/analysis_agent_run.py` 鈥?妯″瀷銆佸浐瀹氶敭涓庣姸鎬佺害鏉熴€?- Create: `services/api/app/services/analysis_agent_run_service.py` 鈥?灏濊瘯鍒涘缓銆佺姸鎬佽浆鎹笌鏌ヨ銆?- Create: `services/api/alembic/versions/20260729_0005_add_analysis_agent_runs.py` 鈥?鏂拌〃銆佸閿€佺害鏉熷拰绱㈠紩銆?- Modify: `services/api/app/models/__init__.py`銆乣analysis_task_service.py`銆乣analysis_runner.py`銆乣api/v1/analysis_tasks.py`銆乣schemas/analysis_task.py`銆?- Modify: `services/api/tests/test_migrations.py`銆乣test_analysis_tasks.py`銆乣test_analysis_runner.py`銆?- Create: `apps/web/components/app/analysis-agent-run-history.tsx` 鍙婂叾娴嬭瘯銆?- Modify: `apps/web/lib/analysis-tasks.ts`銆乣components/app/analysis-task-status.tsx` 鍙婂叾娴嬭瘯銆?- Create: `docs/superpowers/handoffs/2026-07-29-agent-run-records.md`銆?
### Task 1: 妯″瀷涓庤縼绉?
**Files:** Create 妯″瀷鍜岃縼绉伙紱Modify 妯″瀷瀵煎嚭銆乣tests/test_migrations.py`銆?
- [x] **Step 1: 鍐欏け璐ヨ縼绉绘祴璇曘€?*

鍦?round-trip 娴嬭瘯鐨勮〃闆嗗悎鍔犲叆 `analysis_agent_runs`锛屽苟鏂█锛?
```python
constraints = inspector.get_unique_constraints("analysis_agent_runs")
assert frozenset({"task_id", "attempt", "agent_key"}) in {
    frozenset(item["column_names"]) for item in constraints
}
```

downgrade 鍚庣殑鈥滀笉搴斿瓨鍦ㄢ€濋泦鍚堜篃鍔犲叆姝よ〃銆?
- [x] **Step 2: 纭澶辫触銆?*

```powershell
& "D:\Codex_project\jpfx\services\api\.venv\Scripts\python.exe" -m pytest tests/test_migrations.py -q
```

棰勬湡锛欶AIL锛屽洜涓?head migration 鏈垱寤鸿琛ㄣ€?
- [x] **Step 3: 鏈€灏忓疄鐜般€?*

妯″瀷涓庤縼绉诲畾涔変互涓嬬害鏉燂細

```python
AGENT_KEYS = ("evidence_collection", "quality_check", "model_analysis", "report_generation")
AGENT_RUN_STATUSES = ("queued", "running", "completed", "failed", "skipped")
UniqueConstraint("task_id", "attempt", "agent_key", name="uq_analysis_agent_runs_task_attempt_agent")
CheckConstraint("attempt > 0", name="ck_analysis_agent_runs_attempt_positive")
```

鏂板 `user_id + space_id + task_id` 澶嶅悎浠诲姟鎵€鏈夋潈澶栭敭锛圕ASCADE锛夛紝淇濆瓨 UTC 寮€濮?缁撴潫鏃堕棿涓庡畨鍏?`error_message`锛屽苟寤?`(task_id, attempt)` 绱㈠紩銆傚鍑?`AnalysisAgentRun`銆?
- [x] **Step 4: 纭鍙樼豢骞舵彁浜ゃ€?*

閲嶈窇 Step 2锛涢鏈?PASS銆傜劧鍚庯細

```powershell
git add services/api/app/models/analysis_agent_run.py services/api/app/models/__init__.py services/api/alembic/versions/20260729_0005_add_analysis_agent_runs.py services/api/tests/test_migrations.py
git commit -m "feat: persist analysis agent runs"
```

### Task 2: 鎺掗槦銆侀噸璇曚笌瀹夊叏鍝嶅簲

**Files:** Create `analysis_agent_run_service.py`; Modify task service銆丄PI銆乻chema 涓庝换鍔?API 娴嬭瘯銆?
- [x] **Step 1: 鍐欏け璐ユ祴璇曘€?*

鍦?run API 鐨?202 鍝嶅簲鏂█鍥涙潯 `attempt=1` queued 璁板綍锛涘湪 retry 娴嬭瘯涓缃け璐ョ殑 attempt 1锛屾柇瑷€杩斿洖鏂板 attempt 2 鐨勫洓鏉?queued 璁板綍锛岀涓€杞笉鍙樸€傝法鐢ㄦ埛璇诲彇浠诲姟缁х画 404 涓斾笉杩斿洖璁板綍銆?
- [x] **Step 2: 纭澶辫触銆?*

```powershell
& "D:\Codex_project\jpfx\services\api\.venv\Scripts\python.exe" -m pytest tests/test_analysis_tasks.py -q
```

棰勬湡锛欶AIL锛屽洜涓哄皻鏃?`agent_runs` 鍙婂垱寤洪€昏緫銆?
- [x] **Step 3: 鏈€灏忓疄鐜般€?*

鏈嶅姟鎺ュ彛锛?
```python
def create_agent_run_attempt(session: Session, task: AnalysisTask) -> list[AnalysisAgentRun]: ...
def list_agent_runs(session: Session, task: AnalysisTask) -> list[AnalysisAgentRun]: ...
```

鍓嶈€呰绠楄浠诲姟鏈€澶?attempt 鍔犱竴锛屾寜 `AGENT_KEYS` 鍥哄畾椤哄簭鏂板鍥涙潯 queued 璁板綍涓斾笉鑷 commit銆備袱涓棦鏈夋帓闃熸湇鍔″湪鐘舵€佽浆鎹€佹竻闄ら敊璇悗璋冪敤瀹冿紝鍐嶇敤鍘熸湁涓€娆?commit 鍘熷瓙鍐欏叆銆傛柊澧炲彧鍚?`attempt, agent_key, status, started_at, completed_at, error_message` 鐨?`AgentRunResponse`锛沗AnalysisTaskResponse.agent_runs` 榛樿涓虹┖鏁扮粍銆備换鍔″搷搴斾互 `task_id + user_id + space_id` 杩囨护骞舵寜 attempt/鍥哄畾閿帓搴忋€?
- [x] **Step 4: 纭鍙樼豢骞舵彁浜ゃ€?*

閲嶈窇 Step 2锛涢鏈熸墍鏈変换鍔?API 娴嬭瘯閫氳繃銆傜劧鍚庯細

```powershell
git add services/api/app/services/analysis_agent_run_service.py services/api/app/services/analysis_task_service.py services/api/app/api/v1/analysis_tasks.py services/api/app/schemas/analysis_task.py services/api/tests/test_analysis_tasks.py
git commit -m "feat: expose analysis agent run attempts"
```

### Task 3: runner 闃舵鐘舵€?
**Files:** Modify 杩愯璁板綍鏈嶅姟銆乣analysis_runner.py` 涓?runner 娴嬭瘯銆?
- [x] **Step 1: 鍐欏け璐ユ祴璇曘€?*

璁╂祴璇曞す鍏烽€氳繃 `create_agent_run_attempt` 寤虹珛绗竴杞褰曘€傛垚鍔熷悗鏂█鍥涢樁娈典緷娆?completed 涓斿潎鏈夊紑濮?缁撴潫鏃堕棿銆傝川閲忛棬澶辫触鍚庢柇瑷€锛?
```python
assert [(run.agent_key, run.status) for run in runs] == [
    ("evidence_collection", "completed"),
    ("quality_check", "failed"),
    ("model_analysis", "skipped"),
    ("report_generation", "skipped"),
]
assert provider.prompts == []
```

- [x] **Step 2: 纭澶辫触銆?*

```powershell
& "D:\Codex_project\jpfx\services\api\.venv\Scripts\python.exe" -m pytest tests/test_analysis_runner.py -q
```

棰勬湡锛欶AIL锛屽洜涓?runner 鏈浆鎹㈣褰曠姸鎬併€?
- [x] **Step 3: 鏈€灏忓疄鐜般€?*

鏂板锛?
```python
def start_agent_run(session: Session, task: AnalysisTask, agent_key: str) -> None: ...
def complete_agent_run(session: Session, task: AnalysisTask, agent_key: str) -> None: ...
def fail_agent_run(session: Session, task: AnalysisTask, agent_key: str, message: str) -> None: ...
```

runner 渚濇鎺ョ嚎锛氱鏈夋绱€佽川閲忛棬銆丳rovider/JSON 鏍￠獙銆佹姤鍛婁繚瀛樸€傜敤 `current_agent_key` 璁板綍寮傚父褰掑睘锛涘け璐ユ椂褰撳墠琛岀疆 failed锛屽墿浣?queued 琛岀疆 skipped銆傝川閲忛棬淇濈暀鍏蜂綋瀹夊叏涓枃娑堟伅锛屽叾浠栧け璐ヤ繚鐣欐棦鏈夐€氱敤涓枃娑堟伅锛涗笉寰楀啓鍏ュ紓甯稿瓧绗︿覆銆乁RL 鎴?API key銆?
- [x] **Step 4: 纭鍙樼豢骞舵彁浜ゃ€?*

```powershell
& "D:\Codex_project\jpfx\services\api\.venv\Scripts\python.exe" -m pytest tests/test_analysis_runner.py tests/test_analysis_tasks.py -q
git add services/api/app/services/analysis_agent_run_service.py services/api/app/services/analysis_runner.py services/api/tests/test_analysis_runner.py
git commit -m "feat: track analysis agent stages"
```

棰勬湡锛氭垚鍔熴€佽川閲忛棬澶辫触銆侀厤缃け璐ュ拰閲嶈瘯鍦烘櫙鍏ㄩ儴閫氳繃銆?
### Task 4: 鍓嶇杩愯鍘嗗彶

**Files:** Create 灞曠ず缁勪欢鍜屾祴璇曪紱Modify 瀹㈡埛绔被鍨嬨€佺姸鎬佺粍浠跺強娴嬭瘯銆?
- [x] **Step 1: 鍐欏け璐ユ祴璇曘€?*

涓よ疆璁板綍鐨勭粍浠舵祴璇曟柇瑷€鈥滅 2 娆¤繍琛屸€濄€佷腑鏂団€滆瘉鎹川閲忔鏌モ€濄€佸け璐ュ畨鍏ㄦ枃妗堜笌 skipped 鐨勨€滄湭鎵ц鈥濓紝骞舵柇瑷€椤甸潰涓嶅瓨鍦?`quality_check`銆乣skipped` 鍘熷鏋氫妇銆傜姸鎬佺粍浠舵祴璇曞湪杞杩斿洖 `agent_runs` 鍚庢柇瑷€鈥淎gent 杩愯璁板綍鈥濄€?
- [x] **Step 2: 纭澶辫触銆?*

```powershell
npm.cmd test -- components/app/analysis-agent-run-history.test.tsx components/app/analysis-task-status.test.tsx
```

棰勬湡锛欶AIL锛屽洜涓虹粍浠朵笌绫诲瀷涓嶅瓨鍦ㄣ€?
- [x] **Step 3: 鏈€灏忓疄鐜般€?*

澧炲姞锛?
```ts
export interface AnalysisAgentRun {
  attempt: number;
  agent_key: "evidence_collection" | "quality_check" | "model_analysis" | "report_generation";
  status: "queued" | "running" | "completed" | "failed" | "skipped";
  started_at: string | null;
  completed_at: string | null;
  error_message: string | null;
}
```

缁勪欢鎸?attempt 闄嶅簭鍒嗙粍锛屼娇鐢ㄥ浐瀹氫腑鏂?key/status 鏄犲皠锛屽彧娓叉煋鐘舵€併€佹牸寮忓寲鏃堕棿鍜屽畨鍏ㄩ敊璇€傚皢瀹冩寕杞藉湪鐜版湁鐘舵€佸崱涓嬶紱涓嶅鍔犺姹傘€佹寜閽€佸鍑哄叆鍙ｆ垨鎶ュ憡椤甸潰鏀瑰姩銆?
- [x] **Step 4: 纭鍙樼豢骞舵彁浜ゃ€?*

```powershell
npm.cmd test -- components/app/analysis-agent-run-history.test.tsx components/app/analysis-task-status.test.tsx
git add apps/web/lib/analysis-tasks.ts apps/web/components/app/analysis-agent-run-history.tsx apps/web/components/app/analysis-agent-run-history.test.tsx apps/web/components/app/analysis-task-status.tsx apps/web/components/app/analysis-task-status.test.tsx
git commit -m "feat: show analysis agent run history"
```

### Task 5: 瀹屾暣楠岃瘉涓庝氦鎺?
**Files:** Create handoff; Modify 鏈鍒掔殑 checkbox銆?
- [x] **Step 1: 鍚庣闂ㄧ銆?*

```powershell
& "D:\Codex_project\jpfx\services\api\.venv\Scripts\python.exe" -m ruff check --no-cache .
& "D:\Codex_project\jpfx\services\api\.venv\Scripts\python.exe" -m ruff format --check --no-cache .
& "D:\Codex_project\jpfx\services\api\.venv\Scripts\python.exe" -m pytest -q
```

- [x] **Step 2: 鍓嶇闂ㄧ銆?*

```powershell
npm.cmd test
npm.cmd run check:routes
npx.cmd tsc --noEmit
npm.cmd run lint
npm.cmd run build
```

鑻ユ棤 `node_modules`锛屽厛杩愯 `npm.cmd ci`锛屼笉寰椾慨鏀归攣鏂囦欢銆?
- [x] **Step 3: 浜ゆ帴銆佸樊寮傛鏌ュ拰鎻愪氦銆?*

璁板綍鐪熷疄缁撴灉浠ュ強鏈獙璇佺殑 Provider銆佹祻瑙堝櫒绔埌绔€侀儴缃蹭笌 CI銆傝繍琛岋細

```powershell
git diff --check main...HEAD
git status --short --branch
git add docs/superpowers/plans/2026-07-29-agent-run-records.md docs/superpowers/handoffs/2026-07-29-agent-run-records.md
git commit -m "docs: record agent run history"
```

棰勬湡锛氬樊寮備笉鍚?`.env`銆佸瘑閽ャ€乀oken銆丆ookie銆侀攣鏂囦欢鎴栨棤鍏虫枃浠躲€?
