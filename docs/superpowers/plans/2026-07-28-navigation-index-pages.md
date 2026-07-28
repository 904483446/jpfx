# Navigation Index Pages Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 修复侧栏“产品空间”和“分析任务”入口的 404，提供不伪造数据的受保护落地页。

**Architecture:** 空间集合页复用已有 `AuthenticatedApp`，让鉴权与空间列表逻辑保持单一来源。任务集合页使用 `AppShell` 提供只读空状态和到已有空间入口的链接；在没有任务聚合 API 时不请求或呈现模拟任务。

**Tech Stack:** Next.js App Router、React、TypeScript、Vitest、Testing Library。

---

### Task 1: 产品空间集合页

**Files:**
- Create: `apps/web/app/app/spaces/page.test.tsx`
- Create: `apps/web/app/app/spaces/page.tsx`

- [ ] **Step 1: Write the failing test**

```tsx
import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";

vi.mock("@/components/app-shell", () => ({
  AppShell: ({ children }: { children: ReactNode }) => <div data-testid="shell">{children}</div>,
}));
vi.mock("@/components/app/authenticated-app", () => ({
  AuthenticatedApp: () => <div>已加载产品空间</div>,
}));

import SpacesPage from "./page";

describe("SpacesPage", () => {
  it("renders the authenticated product-space index", () => {
    render(<SpacesPage />);
    expect(screen.getByTestId("shell")).toHaveTextContent("已加载产品空间");
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run from `apps/web`: `npm.cmd test -- app/app/spaces/page.test.tsx`

Expected: FAIL because `./page` does not exist.

- [ ] **Step 3: Write minimal implementation**

```tsx
import { AppShell } from "@/components/app-shell";
import { AuthenticatedApp } from "@/components/app/authenticated-app";

export default function SpacesPage() {
  return <AppShell><AuthenticatedApp /></AppShell>;
}
```

- [ ] **Step 4: Run test to verify it passes**

Run from `apps/web`: `npm.cmd test -- app/app/spaces/page.test.tsx`

Expected: PASS.

### Task 2: 分析任务集合页

**Files:**
- Create: `apps/web/app/app/tasks/page.test.tsx`
- Create: `apps/web/app/app/tasks/page.tsx`

- [ ] **Step 1: Write the failing test**

```tsx
import type { ReactNode } from "react";
import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";

vi.mock("@/components/app-shell", () => ({
  AppShell: ({ children }: { children: ReactNode }) => <div data-testid="shell">{children}</div>,
}));

import TasksPage from "./page";

describe("TasksPage", () => {
  it("explains where a user starts an analysis task", () => {
    render(<TasksPage />);
    expect(screen.getByTestId("shell")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "研究队列" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "进入产品空间" })).toHaveAttribute("href", "/app/spaces");
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run from `apps/web`: `npm.cmd test -- app/app/tasks/page.test.tsx`

Expected: FAIL because `./page` does not exist.

- [ ] **Step 3: Write minimal implementation**

```tsx
import Link from "next/link";
import { AppShell } from "@/components/app-shell";

export default function TasksPage() {
  return (
    <AppShell>
      <section className="mx-auto max-w-6xl">
        <p className="font-mono text-[0.68rem] tracking-[0.16em] text-primary">分析任务</p>
        <h1 className="mt-2 text-3xl font-semibold tracking-tight text-foreground">研究队列</h1>
        <p className="mt-3 max-w-2xl text-sm leading-6 text-muted-foreground">分析任务会绑定到一个产品空间，以便保留资料来源、候选证据和最终结论的上下文。</p>
        <div className="mt-8 border border-dashed border-border bg-card p-8 text-center sm:p-12">
          <p className="font-mono text-[0.68rem] tracking-[0.16em] text-muted-foreground">尚无可展示队列</p>
          <h2 className="mt-3 text-xl font-semibold">从产品空间发起分析</h2>
          <p className="mx-auto mt-2 max-w-md text-sm text-muted-foreground">进入一个产品空间后，即可基于已归集资料创建分析任务。</p>
          <Link className="mt-5 inline-block rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground transition-colors hover:bg-primary/85" href="/app/spaces">进入产品空间</Link>
        </div>
      </section>
    </AppShell>
  );
}
```

- [ ] **Step 4: Run test to verify it passes**

Run from `apps/web`: `npm.cmd test -- app/app/tasks/page.test.tsx`

Expected: PASS.

### Task 3: Regression and browser verification

**Files:**
- Verify: `apps/web/app/app/spaces/page.tsx`
- Verify: `apps/web/app/app/tasks/page.tsx`

- [ ] **Step 1: Run focused route and unit checks**

Run from `apps/web`: `npm.cmd test -- app/app/spaces/page.test.tsx app/app/tasks/page.test.tsx` and `npm.cmd run check:routes`

Expected: all focused tests and route checks pass.

- [ ] **Step 2: Run full frontend gates**

Run from `apps/web`: `npm.cmd test`, `npx.cmd tsc --noEmit`, and `npm.cmd run lint`

Expected: all commands exit 0.

- [ ] **Step 3: Verify in authenticated local browser**

Navigate to `/app/spaces` and `/app/tasks`. Confirm neither page shows a 404 and the task page only presents an empty-state explanation.

- [ ] **Step 4: Commit**

```powershell
git add apps/web/app/app/spaces/page.tsx apps/web/app/app/spaces/page.test.tsx apps/web/app/app/tasks/page.tsx apps/web/app/app/tasks/page.test.tsx
git commit -m "fix: add navigation index pages"
```

## Self-review

- Spec coverage: Task 1 implements the shared authenticated space index; Task 2 implements the honest task landing page; Task 3 covers route, frontend, and browser verification.
- Placeholder scan: no TBD/TODO markers or unspecified files remain.
- Type consistency: both pages are default Next.js page exports and use existing component import paths.
