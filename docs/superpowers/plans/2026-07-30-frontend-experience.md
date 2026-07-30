# JPFX 前端体验统一优化 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在不改变业务行为、安全边界或 API 契约的前提下，统一全站前端的研究档案式体验，并补齐已确认的导航、任务、报告和设置页信息层级。

**Architecture:** 保持现有 Next.js 路由与数据加载组件。先用全局语义令牌和复用组件固定标题、区块、状态与空态的视觉规则，再逐页组合这些基础组件；设置页只调整既有 DeepSeek 配置的展示和交互反馈，不增加删除密钥 API。

**Tech Stack:** Next.js、React、TypeScript、Tailwind CSS、shadcn/ui、Vitest、Testing Library。

---

### Task 1: 固定全局视觉令牌与应用壳语义

**Files:**
- Modify: `apps/web/app/globals.css`
- Modify: `apps/web/components/app-shell.tsx`
- Modify: `apps/web/components/app-shell.test.tsx`

- [ ] **Step 1: 为导航和窄屏布局写失败测试。**

在 `app-shell.test.tsx` 断言五个导航名称均可访问，设置链接为 `/app/settings`，主内容有 `main` 地标，导航有中文 `aria-label`。

```tsx
expect(screen.getByRole("link", { name: /设置/ })).toHaveAttribute("href", "/app/settings");
expect(screen.getByRole("main", { name: "主要内容" })).toBeInTheDocument();
```

- [ ] **Step 2: 运行定向测试确认失败。**

Run: `cd apps/web; npm.cmd test -- app-shell.test.tsx`

Expected: FAIL，原因是新的主要内容地标断言尚未满足。

- [ ] **Step 3: 最小化实现应用壳与令牌调整。**

在 `globals.css` 保留现有纸张、墨色、朱红令牌，只补充可复用的细边框、面板和标题层级变量。`app-shell.tsx` 保持现有五个路由，给 `<main>` 增加 `aria-label="主要内容"`，用响应式类让导航在窄屏保持可阅读、在桌面固定为目录栏；不引入图标库或远程字体。

- [ ] **Step 4: 运行定向测试确认通过。**

Run: `cd apps/web; npm.cmd test -- app-shell.test.tsx`

Expected: PASS。

- [ ] **Step 5: 提交基础视觉层。**

```powershell
git add apps/web/app/globals.css apps/web/components/app-shell.tsx apps/web/components/app-shell.test.tsx
git commit -m "feat: unify app shell hierarchy"
```

### Task 2: 统一首页与认证页面的标题、操作和表单层级

**Files:**
- Modify: `apps/web/app/page.tsx`
- Modify: `apps/web/app/page.test.tsx`
- Modify: `apps/web/components/auth/auth-shell.tsx`
- Modify: `apps/web/components/auth/auth-form.tsx`
- Modify: `apps/web/components/auth/auth-form.test.tsx`

- [ ] **Step 1: 写失败测试锁定真实流程与表单语义。**

首页测试断言“资料入库、分析任务、报告交付”仍按顺序出现，认证测试断言每个输入仍有可见 label，提交按钮禁用行为不变。

```tsx
expect(screen.getByText("资料入库")).toBeInTheDocument();
expect(screen.getByLabelText("邮箱地址")).toBeEnabled();
```

- [ ] **Step 2: 运行定向测试确认失败。**

Run: `cd apps/web; npm.cmd test -- page.test.tsx components/auth/auth-form.test.tsx`

Expected: FAIL，新的流程顺序或语义断言未满足。

- [ ] **Step 3: 最小化实现。**

首页仅调整首屏标题、流程预览、CTA 层级与窄屏间距；认证壳保留双栏档案布局并提升标题/说明层级。不得改字段顺序、验证规则、`router.replace` 路径或 API 调用。

- [ ] **Step 4: 运行定向测试确认通过。**

Run: `cd apps/web; npm.cmd test -- page.test.tsx components/auth/auth-form.test.tsx`

Expected: PASS。

- [ ] **Step 5: 提交认证与首页体验。**

```powershell
git add apps/web/app/page.tsx apps/web/app/page.test.tsx apps/web/components/auth/auth-shell.tsx apps/web/components/auth/auth-form.tsx apps/web/components/auth/auth-form.test.tsx
git commit -m "feat: refine landing and auth hierarchy"
```

### Task 3: 强化研究总览、空间入口和空状态

**Files:**
- Modify: `apps/web/components/evidence/page-header.tsx`
- Modify: `apps/web/components/evidence/state-panel.tsx`
- Modify: `apps/web/components/evidence/page-header.test.tsx`
- Modify: `apps/web/components/app/dashboard-spaces.tsx`
- Modify: `apps/web/components/app/dashboard-spaces.test.tsx`
- Modify: `apps/web/app/app/spaces/[spaceId]/page.tsx`

- [ ] **Step 1: 写失败测试。**

断言研究总览在空状态只给出创建空间操作；空间详情仍保留“新建分析任务”及由 `spaceId` 组成的安全链接。

```tsx
expect(screen.getByRole("button", { name: "创建第一个产品空间" })).toBeInTheDocument();
expect(screen.getByRole("link", { name: "新建分析任务" })).toHaveAttribute("href", "/app/spaces/space-1/tasks/new");
```

- [ ] **Step 2: 运行定向测试确认失败。**

Run: `cd apps/web; npm.cmd test -- dashboard-spaces.test.tsx app/spaces/[spaceId]/page.test.tsx`

Expected: FAIL，新的语义标题或空态断言未满足。

- [ ] **Step 3: 最小化实现。**

让 `PageHeader` 支持档案式 eyebrow 与统一操作区；`DashboardSpaces` 使用它呈现研究总览和空间卡片；空间页仅重排现有介绍、任务入口、资料与检索区块。不得请求额外接口或产生示例空间。

- [ ] **Step 4: 运行定向测试确认通过。**

Run: `cd apps/web; npm.cmd test -- dashboard-spaces.test.tsx app/spaces/[spaceId]/page.test.tsx components/evidence/page-header.test.tsx`

Expected: PASS。

- [ ] **Step 5: 提交空间体验。**

```powershell
git add apps/web/components/evidence/page-header.tsx apps/web/components/evidence/state-panel.tsx apps/web/components/evidence/page-header.test.tsx apps/web/components/app/dashboard-spaces.tsx apps/web/components/app/dashboard-spaces.test.tsx apps/web/app/app/spaces/[spaceId]/page.tsx
git commit -m "feat: clarify research overview and spaces"
```

### Task 4: 优化任务时间线与 Agent 运行记录阅读顺序

**Files:**
- Modify: `apps/web/components/app/analysis-task-status.tsx`
- Modify: `apps/web/components/app/analysis-task-status.test.tsx`
- Modify: `apps/web/components/app/analysis-agent-run-history.tsx`
- Modify: `apps/web/components/app/analysis-agent-run-history.test.tsx`

- [ ] **Step 1: 写失败测试。**

断言任务状态、当前阶段、失败重试、七个阶段和 Agent 运行记录仍以真实数据渲染，且“证据质量检查”作为可读阶段文案出现。

```tsx
expect(screen.getByText("证据质量检查")).toBeInTheDocument();
expect(screen.getByRole("button", { name: "重新分析" })).toBeInTheDocument();
```

- [ ] **Step 2: 运行定向测试确认失败。**

Run: `cd apps/web; npm.cmd test -- analysis-task-status.test.tsx analysis-agent-run-history.test.tsx`

Expected: FAIL，新增时间线结构或状态关联断言尚未满足。

- [ ] **Step 3: 最小化实现。**

重排任务首屏为标题/状态、时间线、当前阶段/失败原因、运行记录。保留两秒轮询、`retryAnalysisTask`、状态映射及历史轮次排序；不得添加评分、模拟任务或改变重试行为。

- [ ] **Step 4: 运行定向测试确认通过。**

Run: `cd apps/web; npm.cmd test -- analysis-task-status.test.tsx analysis-agent-run-history.test.tsx`

Expected: PASS。

- [ ] **Step 5: 提交任务体验。**

```powershell
git add apps/web/components/app/analysis-task-status.tsx apps/web/components/app/analysis-task-status.test.tsx apps/web/components/app/analysis-agent-run-history.tsx apps/web/components/app/analysis-agent-run-history.test.tsx
git commit -m "feat: improve task evidence timeline"
```

### Task 5: 重排报告阅读体验并保留导出安全性

**Files:**
- Modify: `apps/web/components/app/report-detail.tsx`
- Modify: `apps/web/components/app/report-detail.test.tsx`
- Modify: `apps/web/components/app/report-archive.tsx`
- Modify: `apps/web/components/app/report-archive-list.tsx`
- Modify: `apps/web/components/app/report-archive-list.test.tsx`
- Modify: `apps/web/app/app/reports/page.tsx`

- [ ] **Step 1: 写失败测试。**

断言报告详情的标题、生成时间、PDF/DOCX 导出与证据展示仍存在，下载期间仍禁用两个导出操作。

```tsx
expect(screen.getByRole("button", { name: "下载 PDF" })).toBeEnabled();
expect(screen.getByText("报告归档")).toBeInTheDocument();
```

- [ ] **Step 2: 运行定向测试确认失败。**

Run: `cd apps/web; npm.cmd test -- report-detail.test.tsx report-archive-list.test.tsx`

Expected: FAIL，新的报告区块标题或阅读顺序断言未满足。

- [ ] **Step 3: 最小化实现。**

用现有 `ReportArchive` 数据按“结论、对比、建议、风险与不确定性、证据”增强分区视觉；保留 `getReport`、`getReportEvidence`、`downloadReport` 和错误处理。报告中心仅统一页头与列表层级。

- [ ] **Step 4: 运行定向测试确认通过。**

Run: `cd apps/web; npm.cmd test -- report-detail.test.tsx report-archive-list.test.tsx`

Expected: PASS。

- [ ] **Step 5: 提交报告体验。**

```powershell
git add apps/web/components/app/report-detail.tsx apps/web/components/app/report-detail.test.tsx apps/web/components/app/report-archive.tsx apps/web/components/app/report-archive-list.tsx apps/web/components/app/report-archive-list.test.tsx apps/web/app/app/reports/page.tsx
git commit -m "feat: improve report reading hierarchy"
```

### Task 6: 完成安全模型设置页的展示优化

**Files:**
- Modify: `apps/web/components/app/deepseek-settings.tsx`
- Modify: `apps/web/components/app/deepseek-settings.test.tsx`
- Modify: `apps/web/app/app/settings/page.tsx`

- [ ] **Step 1: 写失败测试。**

断言“模型设置”、DeepSeek、已配置/待配置、掩码提示、安全说明和密码输入框存在；保存后输入框保持为空，且没有完整密钥文本被渲染。

```tsx
expect(screen.getByRole("heading", { name: "模型设置" })).toBeInTheDocument();
expect(screen.getByLabelText("DeepSeek API Key")).toHaveAttribute("type", "password");
expect(screen.queryByText("test-key-123")).not.toBeInTheDocument();
```

- [ ] **Step 2: 运行定向测试确认失败。**

Run: `cd apps/web; npm.cmd test -- deepseek-settings.test.tsx`

Expected: FAIL，新的页面标题或安全说明断言尚未满足。

- [ ] **Step 3: 最小化实现。**

将现有设置页的标题改为“模型设置”，保留 `getDeepSeekConfig` 和 `saveDeepSeekConfig`；用配置摘要、安全说明与表单区块组织页面。不得添加清除按钮或端点，不得将 Key 写入浏览器存储，不得改变未授权跳转。

- [ ] **Step 4: 运行定向测试确认通过。**

Run: `cd apps/web; npm.cmd test -- deepseek-settings.test.tsx`

Expected: PASS。

- [ ] **Step 5: 提交设置体验。**

```powershell
git add apps/web/components/app/deepseek-settings.tsx apps/web/components/app/deepseek-settings.test.tsx apps/web/app/app/settings/page.tsx
git commit -m "feat: clarify secure model settings"
```

### Task 7: 执行全量前端验证并记录边界

**Files:**
- Modify: `docs/superpowers/handoffs/2026-07-30-frontend-experience.md`

- [ ] **Step 1: 运行完整前端门禁。**

Run:

```powershell
cd apps/web
npm.cmd test
npm.cmd run check:routes
npx.cmd tsc --noEmit
npm.cmd run lint
npm.cmd run build
```

Expected: 全部退出码为 0。若新 worktree 缺少依赖，先运行 `npm.cmd ci`，不修改锁文件。

- [ ] **Step 2: 做静态安全与差异检查。**

Run:

```powershell
git diff --check main...HEAD
rg -n 'sk-[A-Za-z0-9]{20,}|BEGIN .*PRIVATE|postgresql\+psycopg://' apps/web docs
```

Expected: `git diff --check` 通过；扫描没有真实密钥、私钥或连接串匹配。

- [ ] **Step 3: 写交接记录。**

在 handoff 中列出每条命令的真实结果、实际修改的页面、未改变的 API/密钥边界，以及仍未验证的真实 Provider、生产部署、CI 与跨设备视觉验收。

- [ ] **Step 4: 提交验证记录。**

```powershell
git add docs/superpowers/handoffs/2026-07-30-frontend-experience.md
git commit -m "docs: record frontend experience verification"
```
