# V0.1 Task 9 Dashboard 产品空间列表与创建 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** 在既有 Cookie 会话鉴权后的 /app 展示当前用户及其产品空间，支持弹窗创建并跳转详情占位页。

**Architecture:** AuthenticatedApp 继续作为 /auth/me 的唯一鉴权边界，认证成功后才渲染 DashboardSpaces 加载 GET /spaces。SpaceCreateDialog 管理表单与提交，spaces.ts 是唯一的空间请求层。

**Tech Stack:** Next.js App Router、React、TypeScript、Tailwind、现有 Button/Input、Vitest、Testing Library。

---

## 文件结构

| 文件 | 职责 |
| --- | --- |
| apps/web/lib/spaces.ts、spaces.test.ts | Space 类型及 GET/POST /spaces 请求契约。 |
| apps/web/components/app/space-create-dialog.tsx、.test.tsx | 受控可访问弹窗，字段校验、错误和提交锁。 |
| apps/web/components/app/dashboard-spaces.tsx、.test.tsx | 当前用户欢迎信息、列表状态、卡片和创建入口。 |
| apps/web/components/app/authenticated-app.tsx、.test.tsx | 成功获取用户后交给 Dashboard，保持 Task 8 鉴权语义。 |
| apps/web/app/app/spaces/[spaceId]/page.tsx | 无数据请求的详情占位页。 |
| apps/web/scripts/check-routes.mjs | 新动态路由入口检查。 |
| README.md | Task 9 真实完成状态。 |

### Task 1：建立 spaces API 请求层

**Files:**
- Create: apps/web/lib/spaces.ts
- Create: apps/web/lib/spaces.test.ts

- [ ] **Step 1：写失败的请求契约测试**

创建测试，mock apiRequest，并精确覆盖 GET、完整 POST 映射及空选填字段：

~~~ts
import { afterEach, describe, expect, it, vi } from "vitest";
import { apiRequest } from "./api-client";
import { createSpace, listSpaces } from "./spaces";

vi.mock("./api-client", () => ({ apiRequest: vi.fn() }));
const request = vi.mocked(apiRequest);

describe("spaces API helpers", () => {
  afterEach(() => vi.clearAllMocks());

  it("lists the current user's spaces", async () => {
    await listSpaces();
    expect(request).toHaveBeenCalledWith("/spaces");
  });

  it("maps all supported fields", async () => {
    await createSpace({ name: " 企业知识库 Copilot ", industry: "企业服务", productDirection: "AI 知识库", description: "面向内部知识问答" });
    expect(request).toHaveBeenCalledWith("/spaces", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: "企业知识库 Copilot", industry: "企业服务", product_direction: "AI 知识库", description: "面向内部知识问答" }),
    });
  });

  it("omits blank optional fields", async () => {
    await createSpace({ name: " 空间 ", industry: " ", productDirection: "", description: "\n" });
    expect(request).toHaveBeenCalledWith("/spaces", expect.objectContaining({ body: JSON.stringify({ name: "空间" }) }));
  });
});
~~~

- [ ] **Step 2：运行失败测试**

Run: npm.cmd run test -- lib/spaces.test.ts  
Expected: 因找不到 ./spaces 失败。

- [ ] **Step 3：实现最小请求层**

创建 apps/web/lib/spaces.ts：

~~~ts
import { apiRequest } from "./api-client";

export interface Space {
  id: string; name: string; industry: string | null; product_direction: string | null;
  description: string | null; created_at: string; updated_at: string;
}
export interface CreateSpaceInput {
  name: string; industry: string; productDirection: string; description: string;
}
function optionalText(value: string): string | undefined { return value.trim() || undefined; }
export async function listSpaces(): Promise<Space[]> {
  return (await apiRequest<Space[]>("/spaces")) ?? [];
}
export function createSpace(input: CreateSpaceInput): Promise<Space | undefined> {
  const industry = optionalText(input.industry);
  const productDirection = optionalText(input.productDirection);
  const description = optionalText(input.description);
  return apiRequest<Space>("/spaces", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      name: input.name.trim(),
      ...(industry ? { industry } : {}),
      ...(productDirection ? { product_direction: productDirection } : {}),
      ...(description ? { description } : {}),
    }),
  });
}
~~~

- [ ] **Step 4：验证并提交**

Run: npm.cmd run test -- lib/spaces.test.ts  
Expected: 3 个测试通过。

~~~powershell
git add apps/web/lib/spaces.ts apps/web/lib/spaces.test.ts
git commit -m "feat: add frontend spaces API helpers"
~~~

### Task 2：以 TDD 实现创建空间弹窗

**Files:**
- Create: apps/web/components/app/space-create-dialog.tsx
- Create: apps/web/components/app/space-create-dialog.test.tsx

- [ ] **Step 1：写失败的交互测试**

mock createSpace，固定 space 响应，并覆盖以下断言：

~~~tsx
it("rejects a blank name without a request", async () => {
  render(<SpaceCreateDialog open onOpenChange={vi.fn()} onCreated={vi.fn()} />);
  await userEvent.click(screen.getByRole("button", { name: "创建产品空间" }));
  expect(await screen.findByRole("alert")).toHaveTextContent("请填写产品空间名称");
  expect(createSpace).not.toHaveBeenCalled();
});

it("creates once and reports the response", async () => {
  createSpace.mockResolvedValueOnce(space);
  const onCreated = vi.fn();
  render(<SpaceCreateDialog open onOpenChange={vi.fn()} onCreated={onCreated} />);
  await userEvent.type(screen.getByLabelText("空间名称"), "企业知识库 Copilot");
  await userEvent.type(screen.getByLabelText("行业"), "企业服务");
  await userEvent.type(screen.getByLabelText("产品方向"), "AI 知识库");
  await userEvent.click(screen.getByRole("button", { name: "创建产品空间" }));
  await waitFor(() => expect(createSpace).toHaveBeenCalledTimes(1));
  expect(onCreated).toHaveBeenCalledWith(space);
});

it("keeps input when the backend returns Chinese error", async () => {
  createSpace.mockRejectedValueOnce(new ApiClientError("VALIDATION_ERROR", "产品空间名称不能为空"));
  render(<SpaceCreateDialog open onOpenChange={vi.fn()} onCreated={vi.fn()} />);
  await userEvent.type(screen.getByLabelText("空间名称"), "测试空间");
  await userEvent.click(screen.getByRole("button", { name: "创建产品空间" }));
  expect(await screen.findByRole("alert")).toHaveTextContent("产品空间名称不能为空");
  expect(screen.getByLabelText("空间名称")).toHaveValue("测试空间");
});
~~~

另测：open=false 不渲染；取消与 Escape 调用 onOpenChange(false)；未完成请求期间按钮 disabled，连续点击只请求一次。

- [ ] **Step 2：运行失败测试**

Run: npm.cmd run test -- components/app/space-create-dialog.test.tsx  
Expected: 找不到组件。

- [ ] **Step 3：实现受控弹窗**

实现公开接口：

~~~tsx
export function SpaceCreateDialog({
  open, onOpenChange, onCreated,
}: {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onCreated: (space: Space) => void;
}) { /* useState + useRef + useEffect implementation */ }
~~~

打开时以 useEffect 注册 Escape，关闭时清理、重置表单/错误。使用现有 Input，id 依次为 space-name、space-industry、space-product-direction；描述是 textarea。渲染的外层与语义固定为：

~~~tsx
<div className="fixed inset-0 z-50 grid place-items-center bg-slate-950/40 p-4" onMouseDown={onBackdropMouseDown}>
  <section aria-labelledby="create-space-title" aria-modal="true" className="w-full max-w-lg rounded-2xl bg-white p-6 shadow-xl" role="dialog">
    <h2 id="create-space-title">新建产品空间</h2>
    <form noValidate onSubmit={onSubmit}>{/* four labelled fields and actions */}</form>
  </section>
</div>
~~~

name.trim() 为空时显示“请填写产品空间名称”；提交调用 createSpace(values)，undefined 显示“网络请求失败，请稍后重试”，成功时先关闭再 onCreated(space)。仅显示 ApiClientError.message 或通用网络错误。遮罩仅在 target === currentTarget 时关闭。

- [ ] **Step 4：验证并提交**

~~~powershell
npm.cmd run test -- components/app/space-create-dialog.test.tsx
git add apps/web/components/app/space-create-dialog.tsx apps/web/components/app/space-create-dialog.test.tsx
git commit -m "feat: add product space creation dialog"
~~~

Expected: 全部弹窗测试通过。

### Task 3：以 TDD 接入 Dashboard

**Files:**
- Create: apps/web/components/app/dashboard-spaces.tsx
- Create: apps/web/components/app/dashboard-spaces.test.tsx
- Modify: apps/web/components/app/authenticated-app.tsx
- Modify: apps/web/components/app/authenticated-app.test.tsx

- [ ] **Step 1：写失败的列表与鉴权组合测试**

mock listSpaces 与 useRouter().replace。测试 /auth/me 成功后传入完整 CurrentUser；Dashboard 覆盖：加载“正在加载产品空间…”，成功显示“欢迎回来，测试用户”和 href=/app/spaces/space-1 卡片；空列表显示“还没有产品空间”；点击新建显示 role=dialog；UNAUTHORIZED 仅 replace("/login")；NETWORK_ERROR 显示 role=alert 和“重试”，重试成功后不跳转。

- [ ] **Step 2：运行失败测试**

Run: npm.cmd run test -- components/app/dashboard-spaces.test.tsx components/app/authenticated-app.test.tsx  
Expected: Dashboard 不存在且更新后的鉴权成功态失败。

- [ ] **Step 3：实现 Dashboard 并接入**

DashboardSpaces 接受 user: CurrentUser，初始 listSpaces()，以 requestVersion ref 忽略卸载/旧请求。UNAUTHORIZED 只 router.replace("/login")，非 401 显示 role=alert 和重试。成功态必须包含：

~~~tsx
<div className="max-w-5xl">
  <div className="flex flex-wrap items-start justify-between gap-4">
    <div><p>工作台</p><h1>欢迎回来，{user.display_name}</h1><p>{user.email}</p></div>
    <Button onClick={() => setIsDialogOpen(true)} type="button">新建产品空间</Button>
  </div>
  {/* loading、error、empty 或 cards */}
  <SpaceCreateDialog onCreated={(space) => router.replace("/app/spaces/" + space.id)} onOpenChange={setIsDialogOpen} open={isDialogOpen} />
</div>
~~~

卡片使用 next/link，aria-label 和文字均为 space.name，仅渲染非 null 的行业、产品方向、描述。不得排序、乐观插入、发送 user ID 或请求 GET /spaces/{id}。

AuthenticatedApp ready 分支改为：

~~~tsx
return <DashboardSpaces user={user} />;
~~~

保持所有现有 /auth/me 请求版本、401 跳转、非 401 重试逻辑，删除原 Task 9 占位 div。

- [ ] **Step 4：验证并提交**

~~~powershell
npm.cmd run test -- components/app/dashboard-spaces.test.tsx components/app/authenticated-app.test.tsx
git add apps/web/components/app/dashboard-spaces.tsx apps/web/components/app/dashboard-spaces.test.tsx apps/web/components/app/authenticated-app.tsx apps/web/components/app/authenticated-app.test.tsx
git commit -m "feat: show user spaces in dashboard"
~~~

Expected: Dashboard 和 Task 8 鉴权回归测试全通过。

### Task 4：增加详情占位路由

**Files:**
- Create: apps/web/app/app/spaces/[spaceId]/page.tsx
- Modify: apps/web/scripts/check-routes.mjs

- [ ] **Step 1：先让路由检查失败**

向路由数组加入 "app/app/spaces/[spaceId]/page.tsx"，运行 npm.cmd run check:routes，预期因文件缺失失败。

- [ ] **Step 2：实现无数据页**

创建：

~~~tsx
import Link from "next/link";

export default function SpaceDetailPlaceholderPage() {
  return (
    <main className="min-h-screen bg-[#f6f9fb] p-6 text-[#0a1f33] md:p-10">
      <section className="mx-auto max-w-3xl rounded-2xl border border-slate-200 bg-white p-8">
        <p className="text-sm font-medium text-[#14b8a6]">产品空间</p>
        <h1 className="mt-2 text-3xl font-semibold tracking-tight">产品空间详情</h1>
        <p className="mt-3 text-sm leading-6 text-slate-600">产品空间详情将在后续任务实现。</p>
        <Link className="mt-6 inline-flex text-sm font-medium text-[#1677ff] hover:underline" href="/app">返回工作台</Link>
      </section>
    </main>
  );
}
~~~

禁止读取 params、请求 API 或展示 ID/名称。

- [ ] **Step 3：验证并提交**

~~~powershell
npm.cmd run check:routes
npm.cmd exec tsc -- --noEmit
git add apps/web/app/app/spaces/[spaceId]/page.tsx apps/web/scripts/check-routes.mjs
git commit -m "feat: add product space detail placeholder"
~~~

Expected: STATIC_ROUTE_FILES=ok，类型检查无错误。

### Task 5：完整验证与文档校准

**Files:**
- Modify: README.md

- [ ] **Step 1：更新 README**

将阶段写为“V0.1 Task 0 至 Task 9 已完成”，补充 /app 已列出当前用户空间、弹窗创建四字段和成功跳转详情占位页；明确详情不加载数据，编辑删除、文档、知识库、RAG、竞品、报告仍不在范围内。

- [ ] **Step 2：运行完整自动化验证**

~~~powershell
npm.cmd run test
npm.cmd run check:routes
npm.cmd exec tsc -- --noEmit
npm.cmd run lint
npm.cmd run build
npm.cmd audit --omit=dev
~~~

Expected: 全部通过，审计输出 found 0 vulnerabilities。任何失败先记录阻塞，不继续提交。

- [ ] **Step 3：浏览器烟雾验证**

仅在用户已启动本地前后端时：验证 /app 用户/空间、空名称无请求、完整创建跳转 /app/spaces/{id}、刷新占位页不请求 GET /spaces/{id}、前端存储无 JWT。环境不可用则记录“浏览器烟雾验证未执行”，不读取 .env、Cookie、Token。

- [ ] **Step 4：提交完成文档**

~~~powershell
git add README.md
git commit -m "docs: record Task 9 dashboard spaces completion"
~~~

## 计划自检

- 覆盖当前用户、列表全部状态、方案 A 弹窗、字段规则、成功跳转与无数据详情页。
- 所有请求继续走 apiRequest 的 credentials include；无 user ID、Cookie/JWT、.env、后端改动或详情 API 请求。
- 不含编辑删除、知识库、文档、RAG、竞品、报告、退出登录或 V0.2+。

