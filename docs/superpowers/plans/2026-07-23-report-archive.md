# 报告归档闭环 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 让已登录用户能按自己拥有的产品空间查看历史竞品报告，并从 `/app/reports` 安全进入既有报告详情页。

**Architecture:** 后端在既有 `/reports` 路由增加列表端点，所有查询固定按当前用户过滤，并可选按当前用户拥有的 `space_id` 过滤。前端在既有 reports client 中增加列表请求，在新的纯展示 `ReportArchiveList` 组件中处理加载、空、错误和报告链接；详情、证据和导出契约保持不变。

**Tech Stack:** FastAPI、SQLAlchemy、Pydantic、pytest、Next.js、React、TypeScript、Vitest、Testing Library。

---

## 文件结构

- 修改 `services/api/app/api/v1/reports.py`：增加受当前用户保护的 `GET /reports`，以及可选 `space_id` 过滤。
- 修改 `services/api/app/schemas/report.py`：复用既有 `ReportResponse` 作为列表元素，不暴露证据、模型配置或其他用户数据。
- 修改 `services/api/tests/test_reports.py`：覆盖默认排序、用户隔离、空间过滤和非法/无权空间过滤。
- 修改 `apps/web/lib/reports.ts`：增加 `listReports(spaceId?)`，保持 `apiRequest` 的 Cookie 与错误契约。
- 修改 `apps/web/lib/reports.test.ts`：覆盖无筛选和 URL 编码后的空间筛选请求。
- 创建 `apps/web/components/app/report-archive-list.tsx`：只接收报告列表，负责真实数据的归档条目和状态呈现。
- 创建 `apps/web/components/app/report-archive-list.test.tsx`：覆盖列表、空态、错误态和报告详情链接。
- 创建 `apps/web/app/app/reports/page.tsx`：使用既有 `AppShell` 渲染报告中心页面。
- 创建 `apps/web/app/app/reports/page.test.tsx`：覆盖页面使用应用壳并渲染列表组件。

## Task 1: 后端报告列表与隔离

**Files:**
- Modify: `services/api/app/api/v1/reports.py`
- Test: `services/api/tests/test_reports.py`

- [ ] **Step 1: 写失败的列表、排序和隔离测试。**

```python
def test_list_reports_returns_current_users_reports_newest_first(client, database_session):
    user = _authenticate(client, database_session, "reports-list@example.com")
    first = _create_report(database_session, user)
    second = _create_report(database_session, user)
    second.created_at = first.created_at + timedelta(seconds=1)
    database_session.commit()

    response = client.get("/api/v1/reports")

    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == [str(second.id), str(first.id)]

def test_list_reports_cannot_enumerate_another_users_reports(client, database_session):
    owner = _authenticate(client, database_session, "reports-list-owner@example.com")
    _create_report(database_session, owner)
    _authenticate(client, database_session, "reports-list-other@example.com")

    assert client.get("/api/v1/reports").json() == []
```

- [ ] **Step 2: 运行失败测试并确认端点尚不存在。**

Run: `D:\Codex_project\jpfx\services\api\.venv\Scripts\python.exe -m pytest tests/test_reports.py -q -p no:cacheprovider`

Expected: FAIL，因为 `GET /api/v1/reports` 目前会被动态 `/{report_id}` 路由当作 UUID 解析而返回验证错误。

- [ ] **Step 3: 以当前用户为边界实现最小列表端点。**

```python
@router.get("", response_model=list[ReportResponse])
def list_reports(
    space_id: UUID | None = None,
    current_user: Annotated[User, Depends(get_current_user)],
    database_session: Annotated[Session, Depends(get_db_session)],
) -> list[ReportResponse]:
    statement = select(CompetitorReport).where(CompetitorReport.user_id == current_user.id)
    if space_id is not None:
        statement = statement.where(CompetitorReport.space_id == space_id)
    reports = database_session.scalars(statement.order_by(CompetitorReport.created_at.desc())).all()
    return [ReportResponse.model_validate(report) for report in reports]
```

端点不得接收 `user_id`，不得返回 `structured_json` 以外的敏感设置，且不得改动 `_owned_report`、证据快照或导出逻辑。

- [ ] **Step 4: 增加空间过滤测试并运行后端定向测试。**

```python
def test_list_reports_filters_only_current_users_selected_space(client, database_session):
    user = _authenticate(client, database_session, "reports-space-filter@example.com")
    selected = _create_report(database_session, user)
    other_space_report = _create_report(database_session, user)

    response = client.get(f"/api/v1/reports?space_id={selected.space_id}")

    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == [str(selected.id)]
    assert str(other_space_report.id) not in response.text
```

Run: `D:\Codex_project\jpfx\services\api\.venv\Scripts\python.exe -m pytest tests/test_reports.py -q -p no:cacheprovider`

Expected: PASS。

- [ ] **Step 5: 提交后端列表闭环。**

```powershell
git add services/api/app/api/v1/reports.py services/api/tests/test_reports.py
git commit -m "feat: list owned competitor reports"
```

## Task 2: 前端报告客户端与归档列表

**Files:**
- Modify: `apps/web/lib/reports.ts`
- Modify: `apps/web/lib/reports.test.ts`
- Create: `apps/web/components/app/report-archive-list.tsx`
- Create: `apps/web/components/app/report-archive-list.test.tsx`

- [ ] **Step 1: 写客户端与组件失败测试。**

```tsx
it("requests reports with an optional encoded space filter", async () => {
  await listReports("space id");
  expect(apiRequest).toHaveBeenCalledWith("/reports?space_id=space%20id");
});

it("links each real report to its existing dossier page", async () => {
  listReports.mockResolvedValue([report]);
  render(<ReportArchiveList />);
  expect(await screen.findByRole("link", { name: report.title })).toHaveAttribute(
    "href", "/app/reports/report-1"
  );
});
```

- [ ] **Step 2: 运行定向前端测试并确认模块尚不存在。**

Run: `npm.cmd test -- lib/reports.test.ts components/app/report-archive-list.test.tsx`

Expected: FAIL，`listReports` 和 `ReportArchiveList` 尚未定义。

- [ ] **Step 3: 实现最小客户端与状态完整的列表组件。**

```tsx
export function listReports(spaceId?: string) {
  const query = spaceId ? `?space_id=${encodeURIComponent(spaceId)}` : "";
  return apiRequest<CompetitorReport[]>(`/reports${query}`);
}
```

组件首次加载调用 `listReports()`；`UNAUTHORIZED` 使用 `router.replace("/login")`；其他错误显示 `role="alert"` 和“重试”按钮；空数组显示“还没有归档报告”；每条记录显示标题、创建时间、空间 ID 和“查看报告”链接。不得复制详情内容、证据或导出按钮。

- [ ] **Step 4: 运行定向前端测试。**

Run: `npm.cmd test -- lib/reports.test.ts components/app/report-archive-list.test.tsx`

Expected: PASS。

- [ ] **Step 5: 提交前端归档列表组件。**

```powershell
git add apps/web/lib/reports.ts apps/web/lib/reports.test.ts apps/web/components/app/report-archive-list.tsx apps/web/components/app/report-archive-list.test.tsx
git commit -m "feat: add report archive list"
```

## Task 3: 报告中心路由和回归门禁

**Files:**
- Create: `apps/web/app/app/reports/page.tsx`
- Create: `apps/web/app/app/reports/page.test.tsx`
- Modify: `README.md`
- Modify: `TASK_BREAKDOWN.md`
- Modify: `docs/superpowers/handoffs/2026-07-23-current-project-status.md`

- [ ] **Step 1: 写报告中心路由失败测试。**

```tsx
vi.mock("@/components/app-shell", () => ({ AppShell: ({ children }: { children: ReactNode }) => <div data-testid="shell">{children}</div> }));
vi.mock("@/components/app/report-archive-list", () => ({ ReportArchiveList: () => <div>archive list</div> }));

it("places the report center inside the authenticated application shell", () => {
  render(<ReportsPage />);
  expect(screen.getByTestId("shell")).toHaveTextContent("报告中心");
  expect(screen.getByText("archive list")).toBeInTheDocument();
});
```

- [ ] **Step 2: 运行路由测试并确认页面尚不存在。**

Run: `npm.cmd test -- app/app/reports/page.test.tsx`

Expected: FAIL，因为 `/app/reports/page.tsx` 尚不存在。

- [ ] **Step 3: 实现报告中心页面并更新已完成状态。**

```tsx
export default function ReportsPage() {
  return <AppShell><section className="mx-auto max-w-6xl"><p>报告中心</p><h1>研究归档</h1><ReportArchiveList /></section></AppShell>;
}
```

根 README、路线图和当前状态记录只将“报告列表 API 与 `/app/reports`”从待补项改为已完成；真实浏览器、Docker/Alembic、第三方 Provider 与 V1.0 的验证边界保持未完成。

- [ ] **Step 4: 运行前端全量门禁与后端回归。**

Run:

```powershell
cd apps/web
npm.cmd test
npm.cmd run check:routes
npx.cmd tsc --noEmit
npm.cmd run lint
npm.cmd run build
```

Run:

```powershell
cd services/api
.\.venv\Scripts\python.exe -m ruff check --no-cache .
.\.venv\Scripts\python.exe -m ruff format --check --no-cache .
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
```

Expected: 所有命令通过。若依赖、测试数据库或 Docker 未准备好，记录具体失败，不得将未运行命令表述为通过。

- [ ] **Step 5: 提交路由、状态记录和最终验证。**

```powershell
git diff --check main...HEAD
git add apps/web/app/app/reports/page.tsx apps/web/app/app/reports/page.test.tsx README.md TASK_BREAKDOWN.md docs/superpowers/handoffs/2026-07-23-current-project-status.md
git commit -m "feat: complete report archive center"
```

## 计划自检

- API 列表只通过 Cookie 当前用户过滤，未引入可客户端伪造的 `user_id`。
- 空间过滤是可选收窄条件，不能扩大访问范围；查询无结果返回空数组，不泄露是否存在他人空间。
- 列表只复用 `CompetitorReport` 的现有公开字段；证据、导出和详情继续使用原有按 ID 端点和所有权检查。
- 每个新增行为均先有失败测试、失败确认、最小实现、通过验证和独立提交步骤。
