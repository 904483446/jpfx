# JPFX 证据编辑部前端重构 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (- [ ]) syntax for tracking.

**Goal:** 在不改变 JPFX 的既有路由、认证、表单、数据请求和安全边界前提下，完成首页、认证页和应用内页面的证据编辑部视觉重构。

**Architecture:** 先在全局样式中建立纸张主题和语义令牌，再以无业务请求的标题、状态印章、状态面板为基础重排页面。业务组件保留现有 lib API 和状态机，只改变视觉编排；任何结论、证据、指标和状态均来自真实业务数据。

**Tech Stack:** Next.js 16、React 19、TypeScript、Tailwind CSS 4、现有 shadcn/Base UI、Vitest、Testing Library。

---

## 文件结构

| 文件 | 职责 |
| --- | --- |
| apps/web/app/globals.css | 纸张主题、深色主题、字体、圆角、焦点和减少动效令牌。 |
| apps/web/components/evidence/* | 无请求的标题、状态印章、加载骨架和空状态原语。 |
| apps/web/components/landing/* | 首页的真实产品流程和主视觉。 |
| apps/web/components/auth/* | 认证页布局，保留认证表单行为。 |
| apps/web/components/app-shell.tsx | 目录侧栏、顶部上下文与主体区域。 |
| apps/web/components/app/* | 资料、任务、报告和设置的档案布局。 |
| 同名 *.test.tsx | 语义、状态与既有交互的回归保护。 |

## Task 1: 建立语义令牌和展示原语

**Files:**
- Create: apps/web/components/evidence/page-header.tsx
- Create: apps/web/components/evidence/status-stamp.tsx
- Create: apps/web/components/evidence/state-panel.tsx
- Create: apps/web/components/evidence/page-header.test.tsx
- Create: apps/web/components/evidence/status-stamp.test.tsx
- Modify: apps/web/app/globals.css

- [ ] **Step 1: 写失败测试，固定展示原语的语义与真实状态映射。**

    render(<StatusStamp status="indexed" />);
    expect(screen.getByText("已索引")).toBeInTheDocument();
    expect(screen.getByLabelText("文档状态：已索引")).toBeInTheDocument();

- [ ] **Step 2: 运行测试并确认新模块尚不存在。**

Run: npm test -- components/evidence/status-stamp.test.tsx

Expected: FAIL with module-not-found for status-stamp.

- [ ] **Step 3: 创建展示原语和纸张主题令牌。**

    export type EvidenceStatus =
      "uploaded" | "processing" | "indexed" | "failed" |
      "draft" | "queued" | "running" | "completed";

    export function StatusStamp({ status }: { status: EvidenceStatus }) {
      const label = statusLabels[status];
      return <span aria-label={"文档状态：" + label} className={statusClassNames[status]}>{label}</span>;
    }

    :root { --paper: #f7f4ee; --ink: #1d1c19; --vermilion: #b6452c; --line: #d8d1c6; }
    @media (prefers-reduced-motion: reduce) {
      *, *::before, *::after { animation-duration: .01ms !important; transition-duration: .01ms !important; }
    }

PageHeader 接收 eyebrow、title、description、actions。StatePanel 接收 kind、title、description、action，不接收业务数据或网络回调。

- [ ] **Step 4: 运行新增原语测试。**

Run: npm test -- components/evidence/page-header.test.tsx components/evidence/status-stamp.test.tsx

Expected: PASS.

- [ ] **Step 5: 提交原语。**

    git add apps/web/app/globals.css apps/web/components/evidence
    git commit -m "feat: add evidence desk design primitives"

## Task 2: 重构品牌、首页与真实产品流程

**Files:**
- Modify: apps/web/components/brand-mark.tsx
- Modify: apps/web/components/landing/steps.tsx
- Modify: apps/web/app/page.tsx
- Create: apps/web/app/page.test.tsx

- [ ] **Step 1: 写首页语义和路由失败测试。**

    render(<Home />);
    expect(screen.getByRole("link", { name: "登录" })).toHaveAttribute("href", "/login");
    expect(screen.getByRole("link", { name: "创建账户" })).toHaveAttribute("href", "/register");
    expect(screen.getByRole("heading", { name: /把竞品洞察变成可验证的决策/ })).toBeInTheDocument();

- [ ] **Step 2: 运行首页测试并确认新首屏尚未出现。**

Run: npm test -- app/page.test.tsx

Expected: FAIL because the new heading and register CTA label are absent.

- [ ] **Step 3: 用分屏档案首页替换现有首屏。**

    <section className="evidence-hero" id="product">
      <div><p className="eyebrow">竞争情报证据台</p><h1>把竞品洞察变成可验证的决策。</h1></div>
      <ProductWorkflowPreview />
    </section>

ProductWorkflowPreview 只能展示真实流程名称“资料入库、分析任务、报告交付”，不能显示虚构数字或虚构客户。Steps 改为不等宽三段流程，手机端单列。BrandMark 仍是指向 / 的 Link。

- [ ] **Step 4: 运行首页测试。**

Run: npm test -- app/page.test.tsx

Expected: PASS.

- [ ] **Step 5: 提交首页。**

    git add apps/web/app/page.tsx apps/web/app/page.test.tsx apps/web/components/brand-mark.tsx apps/web/components/landing/steps.tsx
    git commit -m "feat: redesign evidence desk landing page"

## Task 3: 重构认证壳且保持认证表单契约

**Files:**
- Modify: apps/web/components/auth/auth-shell.tsx
- Modify: apps/web/components/auth/auth-form.tsx
- Modify: apps/web/components/auth/auth-form.test.tsx
- Modify: apps/web/app/login/page.tsx
- Modify: apps/web/app/register/page.tsx

- [ ] **Step 1: 为双栏壳和表单标签补充失败测试。**

    render(<AuthShell title="欢迎回来" description="说明" footer={<span>尾部</span>}><form aria-label="登录表单" /></AuthShell>);
    expect(screen.getByText("证据优先的竞争情报工作台")).toBeInTheDocument();
    expect(screen.getByRole("main")).toHaveClass("auth-dossier");

- [ ] **Step 2: 运行认证测试。**

Run: npm test -- components/auth/auth-form.test.tsx

Expected: FAIL on missing dossier copy or class.

- [ ] **Step 3: 实现档案封面认证布局。**

    return <main className="auth-dossier">
      <aside aria-label="产品说明">...</aside>
      <section aria-labelledby="auth-title">{children}</section>
    </main>;

保留 display-name、email、password 的 id、autoComplete、提交锁、错误 role=alert 与路由跳转；仅替换分组和令牌。

- [ ] **Step 4: 运行认证测试。**

Run: npm test -- components/auth/auth-form.test.tsx

Expected: PASS, including现有登录和注册请求断言.

- [ ] **Step 5: 提交认证重构。**

    git add apps/web/components/auth apps/web/app/login/page.tsx apps/web/app/register/page.tsx
    git commit -m "feat: redesign authentication dossier pages"

## Task 4: 重构应用壳、概览和空间入口

**Files:**
- Modify: apps/web/components/app-shell.tsx
- Modify: apps/web/components/app/authenticated-app.tsx
- Modify: apps/web/components/app/dashboard-spaces.tsx
- Modify: apps/web/components/app/space-create-dialog.tsx
- Modify: apps/web/components/app/authenticated-app.test.tsx
- Modify: apps/web/components/app/dashboard-spaces.test.tsx
- Modify: apps/web/components/app/space-create-dialog.test.tsx

- [ ] **Step 1: 写失败测试，覆盖目录式导航、加载骨架和空空间主操作。**

    render(<DashboardSpaces user={user} />);
    expect(await screen.findByRole("button", { name: "新建产品空间" })).toBeEnabled();
    expect(screen.getByText("还没有产品空间")).toBeInTheDocument();

- [ ] **Step 2: 运行概览测试。**

Run: npm test -- components/app/authenticated-app.test.tsx components/app/dashboard-spaces.test.tsx components/app/space-create-dialog.test.tsx

Expected: FAIL on新目录标签或骨架状态。

- [ ] **Step 3: 实现目录侧栏与空间档案布局。**

    <main className="app-dossier">
      <aside aria-label="主导航">{navigation}</aside>
      <section><header className="context-bar">{context}</header>{children}</section>
    </main>

导航项只包含已实现或明确不可用的入口。保留 listSpaces、未授权跳转、SpaceCreateDialog 回调、Escape、遮罩点击、提交锁和字段 id。

- [ ] **Step 4: 运行概览测试。**

Run: npm test -- components/app/authenticated-app.test.tsx components/app/dashboard-spaces.test.tsx components/app/space-create-dialog.test.tsx

Expected: PASS.

- [ ] **Step 5: 提交应用壳与概览。**

    git add apps/web/components/app-shell.tsx apps/web/components/app/authenticated-app.tsx apps/web/components/app/dashboard-spaces.tsx apps/web/components/app/space-create-dialog.tsx apps/web/components/app/*.test.tsx
    git commit -m "feat: redesign workspace shell and space dashboard"

## Task 5: 重构资料档案与检索结果

**Files:**
- Modify: apps/web/app/app/spaces/[spaceId]/page.tsx
- Modify: apps/web/components/app/space-documents.tsx
- Modify: apps/web/components/app/space-retrieval.tsx
- Modify: apps/web/components/app/space-documents.test.tsx
- Modify: apps/web/components/app/space-retrieval.test.tsx

- [ ] **Step 1: 写失败测试，确保状态印章与检索相似度语义。**

    expect(await screen.findByLabelText("文档状态：已索引")).toBeInTheDocument();
    expect(screen.getByText(/相似度/)).toBeInTheDocument();
    expect(screen.queryByText(/可信度/)).not.toBeInTheDocument();

- [ ] **Step 2: 运行资料与检索测试。**

Run: npm test -- components/app/space-documents.test.tsx components/app/space-retrieval.test.tsx

Expected: FAIL because current rows have no semantic status stamp.

- [ ] **Step 3: 以资料条目和引用卡片重排现有结果。**

    <li className="document-record">
      <div><h2>{document.filename}</h2><StatusStamp status={document.status} /></div>
      <DocumentActions document={document} />
    </li>

不得改变 20MB 限制、上传格式、删除和重新索引请求。检索继续展示 filename、chunk_index 和 similarity，并明确使用“相似度”标签。

- [ ] **Step 4: 运行资料与检索测试。**

Run: npm test -- components/app/space-documents.test.tsx components/app/space-retrieval.test.tsx

Expected: PASS.

- [ ] **Step 5: 提交资料模块。**

    git add "apps/web/app/app/spaces/[spaceId]/page.tsx" apps/web/components/app/space-documents.tsx apps/web/components/app/space-retrieval.tsx apps/web/components/app/space-*.test.tsx
    git commit -m "feat: redesign space documents and retrieval"

## Task 6: 重构任务创建、候选确认与真实运行状态

**Files:**
- Modify: apps/web/app/app/spaces/[spaceId]/tasks/new/page.tsx
- Modify: apps/web/app/app/tasks/[taskId]/page.tsx
- Modify: apps/web/components/app/analysis-task-create.tsx
- Modify: apps/web/components/app/candidate-confirmation.tsx
- Modify: apps/web/components/app/analysis-task-status.tsx
- Modify: 对应的三个 *.test.tsx

- [ ] **Step 1: 写失败测试，锁定阶段时间线和候选证据邻接关系。**

    render(<AnalysisTaskStatus taskId="task-1" />);
    expect(await screen.findByText("模型调用失败")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "重试分析" })).toBeEnabled();

    expect(screen.getByRole("checkbox", { name: "选择 竞品 A" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "候选证据来源" })).toBeInTheDocument();

- [ ] **Step 2: 运行任务测试。**

Run: npm test -- components/app/analysis-task-create.test.tsx components/app/candidate-confirmation.test.tsx components/app/analysis-task-status.test.tsx

Expected: FAIL on中文时间线与新证据标签。

- [ ] **Step 3: 实现任务档案表单、候选证据条目和状态时间线。**

    const taskStages = ["草稿", "等待执行", "分析中", "已完成"] as const;
    <ol aria-label="任务进度">{taskStages.map((label) => <li key={label}>{label}</li>)}</ol>

运行状态完全由 AnalysisTask.status 和 task.stage 决定。保留 0-3 已知竞品、手动选择 1-3 候选、自动选择、轮询停止、重试、未授权跳转和安全外链。

- [ ] **Step 4: 运行任务测试。**

Run: npm test -- components/app/analysis-task-create.test.tsx components/app/candidate-confirmation.test.tsx components/app/analysis-task-status.test.tsx

Expected: PASS.

- [ ] **Step 5: 提交任务流程。**

    git add "apps/web/app/app/spaces/[spaceId]/tasks/new/page.tsx" "apps/web/app/app/tasks/[taskId]/page.tsx" apps/web/components/app/analysis-task-*.tsx apps/web/components/app/candidate-confirmation.*
    git commit -m "feat: redesign analysis task evidence flow"

## Task 7: 重构报告详情与证据账本

**Files:**
- Modify: apps/web/app/app/reports/[reportId]/page.tsx
- Modify: apps/web/components/app/report-detail.tsx
- Modify: apps/web/components/app/report-detail.test.tsx

- [ ] **Step 1: 写失败测试，覆盖报告抬头、来源类型和安全外链。**

    expect(await screen.findByRole("heading", { name: report.title })).toBeInTheDocument();
    expect(screen.getByText("证据链")).toBeInTheDocument();
    expect(screen.getByText("模型推断不构成事实证据，需进一步验证。")).toBeInTheDocument();
    expect(screen.queryByRole("link", { name: "不安全来源" })).not.toBeInTheDocument();

- [ ] **Step 2: 运行报告测试。**

Run: npm test -- components/app/report-detail.test.tsx

Expected: FAIL because the new evidence-ledger heading is absent.

- [ ] **Step 3: 实现报告档案布局。**

    <article className="report-dossier">
      <ReportHeader report={report} onExport={exportFile} />
      <ExecutiveFinding summary={report.structured_json.executive_summary} />
      <EvidenceLedger evidence={evidence} />
    </article>

将 ReportBody 拆为不请求数据的 ReportHeader、ExecutiveFinding、CompetitorComparison、ListSection、EvidenceLedger。保留 getReport、getReportEvidence、PDF/DOCX 下载、未授权跳转与 isSafeExternalUrl 的精确校验；证据类型不得合并或改写。

- [ ] **Step 4: 运行报告测试。**

Run: npm test -- components/app/report-detail.test.tsx

Expected: PASS, including javascript、file 与 data URL 不渲染链接的回归测试。

- [ ] **Step 5: 提交报告页。**

    git add "apps/web/app/app/reports/[reportId]/page.tsx" apps/web/components/app/report-detail.tsx apps/web/components/app/report-detail.test.tsx
    git commit -m "feat: redesign evidence report detail"

## Task 8: 重构模型设置并保持密钥脱敏边界

**Files:**
- Modify: apps/web/components/app/deepseek-settings.tsx
- Modify: apps/web/components/app/deepseek-settings.test.tsx
- Modify: apps/web/app/app/settings/page.tsx

- [ ] **Step 1: 写失败测试，确保配置状态可见但输入值会清空。**

    await user.type(screen.getByLabelText("DeepSeek API Key"), "secret-value");
    await user.click(screen.getByRole("button", { name: "保存配置" }));
    expect(screen.getByLabelText("DeepSeek API Key")).toHaveValue("");
    expect(screen.getByText("已配置")).toBeInTheDocument();

- [ ] **Step 2: 运行设置测试。**

Run: npm test -- components/app/deepseek-settings.test.tsx

Expected: FAIL on档案样式的结构或状态文本。

- [ ] **Step 3: 实现配置档案布局。**

    <section aria-labelledby="deepseek-settings-heading" className="settings-dossier">
      <StatusStamp status={config?.is_configured ? "indexed" : "draft"} />
      <form onSubmit={onSubmit}>...</form>
    </section>

显示文本映射为“已配置/待配置”，但 Key 不得传给印章或日志。保留 password 输入、autoComplete=off、提交后清空、api_key_hint 和未授权跳转。

- [ ] **Step 4: 运行设置测试。**

Run: npm test -- components/app/deepseek-settings.test.tsx

Expected: PASS with existing脱敏断言。

- [ ] **Step 5: 提交设置页。**

    git add apps/web/components/app/deepseek-settings.tsx apps/web/components/app/deepseek-settings.test.tsx apps/web/app/app/settings/page.tsx
    git commit -m "feat: redesign secure model settings"

## Task 9: 响应式、深色模式和全量前端门禁

**Files:**
- Modify: apps/web/app/globals.css
- Modify: 受前八任务影响且仍含硬编码旧主题的 apps/web/**/*.tsx
- Test: apps/web/app/page.test.tsx 与全部 apps/web/components/**/*.test.tsx

- [ ] **Step 1: 写失败测试，覆盖应用壳的关键可访问语义。**

    render(<AppShell><h1>内容</h1></AppShell>);
    expect(screen.getByRole("navigation", { name: "主导航" })).toBeInTheDocument();
    expect(screen.getByRole("main")).toBeInTheDocument();

- [ ] **Step 2: 运行应用壳测试。**

Run: npm test -- components/app/authenticated-app.test.tsx

Expected: FAIL if navigation 或 main landmark 缺失。

- [ ] **Step 3: 完成令牌替换和无障碍收口。**

    .app-dossier { min-height: 100dvh; background: var(--paper); color: var(--ink); }
    @media (max-width: 767px) {
      .app-dossier { grid-template-columns: 1fr; }
      .app-sidebar { display: none; }
    }

逐页替换遗留的深色面板和青色主题硬编码为令牌或展示原语类。不得改动数据 API、路由参数和请求函数。确认深色令牌下正文、表单、焦点环、状态印章和导出按钮均有可读对比。

- [ ] **Step 4: 运行全量前端质量门禁。**

Run:

    npm test
    npm run check:routes
    npx tsc --noEmit
    npm run lint
    npm run build
    npm audit --omit=dev

Expected: 所有命令退出码为 0。任一失败时，停止提交并先修复或报告具体失败；不得把后端既有时间依赖失败计入前端绿色结果。

- [ ] **Step 5: 在浅色、深色、窄屏和减少动态设置下进行人工视觉检查，并提交收口。**

    git add apps/web
    git commit -m "feat: polish evidence desk responsive states"

检查：无横向溢出、无重叠、按钮文字不换行、表单标签可见、键盘焦点可见、加载/空/错误状态完整、无伪造结论或虚构指标。

## 计划自检

- 规格覆盖：Task 1 覆盖令牌与状态，Task 2-3 覆盖公开和认证面，Task 4-6 覆盖工作台、资料和任务，Task 7 覆盖报告与证据，Task 8 覆盖密钥配置，Task 9 覆盖响应式、深色、动效和前端门禁。
- 边界覆盖：各任务保留路由、表单、请求、用户/空间隔离、报告证据类型、导出 URL 校验和 Key 脱敏；不引入新后端能力。
- 占位检查：本文不存在未定义的后续实施占位；每个代码变更都给出目标文件、测试、命令和最小实现形态。
- 类型一致性：EvidenceStatus 在 Task 1 定义，Task 5 和 Task 8 只使用该联合类型；业务任务状态继续来自 AnalysisTask.status，不转换后端值。

