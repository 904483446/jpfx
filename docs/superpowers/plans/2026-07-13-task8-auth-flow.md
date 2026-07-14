# Task 8 Auth Flow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在不读取 Cookie/JWT 的前提下，实现注册、登录、当前用户读取与 `/app` 前端鉴权跳转。

**Architecture:** 认证接口类型和请求函数集中在 `lib/auth.ts`，所有 HTTP 请求继续委托给 `lib/api-client.ts`。登录与注册表单是独立客户端组件；受保护应用壳也是独立客户端组件，在加载时请求 `/auth/me`，仅 401 跳转登录。路由文件只组装既有页面外壳和客户端组件。

**Tech Stack:** Next.js App Router、React 19、TypeScript、Tailwind CSS、Vitest、React Testing Library、jsdom。

---

## 文件结构

| 文件 | 职责 |
| --- | --- |
| `apps/web/lib/auth.ts` | 定义后端用户和认证请求类型，封装 `/auth/register`、`/auth/login`、`/auth/me` 调用。 |
| `apps/web/lib/auth.test.ts` | 验证认证请求路径、方法、JSON 请求体和 API Client 委托。 |
| `apps/web/components/auth/auth-form.tsx` | 注册/登录表单的输入、最小客户端校验、提交状态、错误显示和跳转。 |
| `apps/web/components/auth/auth-form.test.tsx` | 验证注册/登录交互、错误和重复提交保护。 |
| `apps/web/components/app/authenticated-app.tsx` | 读取当前用户、处理 401 跳转、渲染加载/错误/已认证应用内容。 |
| `apps/web/components/app/authenticated-app.test.tsx` | 验证 `/auth/me` 成功、401 和非 401 错误行为。 |
| `apps/web/app/login/page.tsx` | 用 `AuthShell` 组合登录表单。 |
| `apps/web/app/register/page.tsx` | 用 `AuthShell` 组合注册表单。 |
| `apps/web/app/app/page.tsx` | 用 `AppShell` 和受保护内容组件组合 `/app`。 |
| `apps/web/vitest.config.ts` | 为组件测试启用 jsdom 与测试初始化文件。 |
| `apps/web/test/setup.ts` | 注册 `@testing-library/jest-dom/vitest` 断言扩展。 |
| `apps/web/package.json`、`apps/web/package-lock.json` | 增加前端组件测试所需开发依赖。 |

### Task 1：建立可运行的组件测试基线

**Files:**

- Modify: `apps/web/package.json`
- Modify: `apps/web/package-lock.json`
- Modify: `apps/web/vitest.config.ts`
- Create: `apps/web/test/setup.ts`

- [ ] **Step 1：安装组件测试运行时依赖**

在 `apps/web` 执行：

```powershell
npm.cmd install -D @testing-library/jest-dom @testing-library/react @testing-library/user-event jsdom
```

预期：`package.json` 与锁文件只新增四项开发依赖，不改生产依赖和 `postcss` override。

- [ ] **Step 2：配置 jsdom 测试环境**

将 `apps/web/vitest.config.ts` 改为：

```ts
import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    environment: "jsdom",
    setupFiles: ["./test/setup.ts"],
  },
});
```

创建 `apps/web/test/setup.ts`：

```ts
import "@testing-library/jest-dom/vitest";
```

- [ ] **Step 3：验证既有 API Client 测试仍通过**

运行：

```powershell
npm.cmd run test -- lib/api-client.test.ts
```

预期：5 个既有测试通过，证明 jsdom 配置没有改变 API Client 的可观察行为。

- [ ] **Step 4：提交测试基础设施**

```powershell
git add apps/web/package.json apps/web/package-lock.json apps/web/vitest.config.ts apps/web/test/setup.ts
git commit -m "test: add frontend component test setup"
```

### Task 2：以 TDD 建立认证请求契约

**Files:**

- Create: `apps/web/lib/auth.ts`
- Create: `apps/web/lib/auth.test.ts`

- [ ] **Step 1：写出认证请求失败测试**

创建 `apps/web/lib/auth.test.ts`，以 mock 的 `apiRequest` 验证三个固定契约：

```ts
import { describe, expect, it, vi } from "vitest";

vi.mock("./api-client", () => ({ apiRequest: vi.fn() }));

import { apiRequest } from "./api-client";
import { getCurrentUser, login, register } from "./auth";

const request = vi.mocked(apiRequest);

describe("auth API", () => {
  it("posts registration fields to /auth/register", async () => {
    request.mockResolvedValueOnce(undefined);
    await register({ displayName: "测试用户", email: "user@example.com", password: "password-1" });
    expect(request).toHaveBeenCalledWith("/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ display_name: "测试用户", email: "user@example.com", password: "password-1" }),
    });
  });
});
```

同一文件增加对 `login` 的 `/auth/login` 请求体断言，以及对 `getCurrentUser` 的 `"/auth/me"` 调用断言。此时测试应因找不到 `./auth` 而失败。

- [ ] **Step 2：运行失败测试**

```powershell
npm.cmd run test -- lib/auth.test.ts
```

预期：失败原因是无法解析 `./auth`，不是断言或测试环境错误。

- [ ] **Step 3：实现最小认证请求模块**

创建 `apps/web/lib/auth.ts`：

```ts
import { apiRequest } from "./api-client";

export type CurrentUser = {
  id: string;
  email: string;
  display_name: string;
  is_admin: boolean;
  created_at: string;
  updated_at: string;
};

export type RegisterInput = { displayName: string; email: string; password: string };
export type LoginInput = { email: string; password: string };

const jsonRequest = (body: object): RequestInit => ({
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(body),
});

export function register(input: RegisterInput) {
  return apiRequest<CurrentUser>("/auth/register", jsonRequest({
    display_name: input.displayName,
    email: input.email,
    password: input.password,
  }));
}

export function login(input: LoginInput) {
  return apiRequest<CurrentUser>("/auth/login", jsonRequest(input));
}

export function getCurrentUser() {
  return apiRequest<CurrentUser>("/auth/me");
}
```

- [ ] **Step 4：运行认证模块测试并提交**

```powershell
npm.cmd run test -- lib/auth.test.ts
git add apps/web/lib/auth.ts apps/web/lib/auth.test.ts
git commit -m "feat: add frontend auth API helpers"
```

预期：`auth API` 的注册、登录和当前用户请求断言全部通过。

### Task 3：以 TDD 实现注册和登录表单

**Files:**

- Create: `apps/web/components/auth/auth-form.tsx`
- Create: `apps/web/components/auth/auth-form.test.tsx`
- Modify: `apps/web/app/login/page.tsx`
- Modify: `apps/web/app/register/page.tsx`

- [ ] **Step 1：写失败的表单交互测试**

创建 `apps/web/components/auth/auth-form.test.tsx`，mock `next/navigation` 的 `useRouter` 和 `@/lib/auth`。至少写出以下三个测试：

```tsx
it("registers and redirects to /login", async () => {
  render(<AuthForm mode="register" />);
  await userEvent.type(screen.getByLabelText("昵称"), "测试用户");
  await userEvent.type(screen.getByLabelText("邮箱地址"), "user@example.com");
  await userEvent.type(screen.getByLabelText("密码"), "password-1");
  await userEvent.click(screen.getByRole("button", { name: "注册" }));
  await waitFor(() => expect(register).toHaveBeenCalledWith({ displayName: "测试用户", email: "user@example.com", password: "password-1" }));
  expect(replace).toHaveBeenCalledWith("/login");
});

it("logs in and redirects to /app", async () => {
  render(<AuthForm mode="login" />);
  await userEvent.type(screen.getByLabelText("邮箱地址"), "user@example.com");
  await userEvent.type(screen.getByLabelText("密码"), "password-1");
  await userEvent.click(screen.getByRole("button", { name: "登录" }));
  await waitFor(() => expect(login).toHaveBeenCalled());
  expect(replace).toHaveBeenCalledWith("/app");
});

it("shows the backend Chinese error and disables repeat submission", async () => {
  register.mockRejectedValueOnce(new ApiClientError("EMAIL_EXISTS", "该邮箱已注册"));
  render(<AuthForm mode="register" />);
  // 填入合法字段后提交，断言“该邮箱已注册”出现；请求进行时按钮 disabled。
});
```

补充一个客户端校验测试：空字段、无效邮箱或短于 8 字符密码时不调用认证函数，并显示对应中文提示。此时测试因组件不存在而失败。

- [ ] **Step 2：运行失败测试**

```powershell
npm.cmd run test -- components/auth/auth-form.test.tsx
```

预期：失败原因是无法解析 `auth-form.tsx`。

- [ ] **Step 3：实现最小客户端表单组件**

创建 `apps/web/components/auth/auth-form.tsx`。组件必须以 `"use client"` 开头，使用 `useState` 保存字段、错误和 `isSubmitting`，使用 `useRouter().replace` 跳转。核心提交逻辑如下：

```tsx
const onSubmit = async (event: FormEvent<HTMLFormElement>) => {
  event.preventDefault();
  const validationMessage = validate(values, mode);
  if (validationMessage) {
    setError(validationMessage);
    return;
  }

  setError(null);
  setIsSubmitting(true);
  try {
    if (mode === "register") {
      await register({ displayName: values.displayName, email: values.email, password: values.password });
      router.replace("/login");
    } else {
      await login({ email: values.email, password: values.password });
      router.replace("/app");
    }
  } catch (error) {
    setError(error instanceof Error ? error.message : "网络请求失败，请稍后重试");
  } finally {
    setIsSubmitting(false);
  }
};
```

`validate` 返回以下明确中文信息：`请填写昵称`、`请填写邮箱地址`、`请输入有效的邮箱地址`、`请填写密码`、`密码长度应为 8 到 128 个字符`。表单使用既有 `Input`、`Button`，输入有对应 `label` 和 `aria-describedby`，错误使用 `role="alert"`。

- [ ] **Step 4：接入两个路由入口**

将 `app/login/page.tsx` 的静态输入区替换为：

```tsx
<AuthForm mode="login" />
```

将 `app/register/page.tsx` 的静态输入区替换为：

```tsx
<AuthForm mode="register" />
```

保留现有 `AuthShell` 标题、说明和登录/注册链接。

- [ ] **Step 5：验证通过并提交**

```powershell
npm.cmd run test -- components/auth/auth-form.test.tsx
npm.cmd run lint
git add apps/web/components/auth/auth-form.tsx apps/web/components/auth/auth-form.test.tsx apps/web/app/login/page.tsx apps/web/app/register/page.tsx
git commit -m "feat: add frontend login and registration forms"
```

### Task 4：以 TDD 实现 `/app` 当前用户鉴权

**Files:**

- Create: `apps/web/components/app/authenticated-app.tsx`
- Create: `apps/web/components/app/authenticated-app.test.tsx`
- Modify: `apps/web/app/app/page.tsx`

- [ ] **Step 1：写失败的 `/app` 鉴权测试**

创建 `apps/web/components/app/authenticated-app.test.tsx`，mock `getCurrentUser` 和 `useRouter`，覆盖：

```tsx
it("renders the current user after /auth/me succeeds", async () => {
  getCurrentUser.mockResolvedValueOnce({ id: "user-1", email: "user@example.com", display_name: "测试用户", is_admin: false, created_at: "2026-01-01T00:00:00Z", updated_at: "2026-01-01T00:00:00Z" });
  render(<AuthenticatedApp />);
  expect(screen.getByText("正在验证登录状态…")).toBeInTheDocument();
  expect(await screen.findByText("测试用户")).toBeInTheDocument();
});

it("redirects only UNAUTHORIZED errors to /login", async () => {
  getCurrentUser.mockRejectedValueOnce(new ApiClientError("UNAUTHORIZED", "登录状态无效或已过期"));
  render(<AuthenticatedApp />);
  await waitFor(() => expect(replace).toHaveBeenCalledWith("/login"));
});

it("renders retry UI for non-401 errors without redirecting", async () => {
  getCurrentUser.mockRejectedValueOnce(new ApiClientError("NETWORK_ERROR", "网络请求失败，请稍后重试"));
  render(<AuthenticatedApp />);
  expect(await screen.findByRole("alert")).toHaveTextContent("网络请求失败，请稍后重试");
  expect(replace).not.toHaveBeenCalled();
});
```

测试应先因组件不存在而失败。

- [ ] **Step 2：运行失败测试**

```powershell
npm.cmd run test -- components/app/authenticated-app.test.tsx
```

预期：失败原因是无法解析 `authenticated-app.tsx`。

- [ ] **Step 3：实现最小受保护内容组件**

创建 `apps/web/components/app/authenticated-app.tsx`，以 `"use client"` 开头。通过 `useEffect` 调用 `getCurrentUser`，状态为 `loading`、`user`、`error`；401 调用 `router.replace("/login")`；非 401 显示 `role="alert"` 和“重试”按钮。成功时渲染：

```tsx
<div className="max-w-3xl">
  <p className="text-sm font-medium text-[#14b8a6]">工作台</p>
  <h1 className="mt-2 text-3xl font-semibold tracking-tight">欢迎回来，{user.display_name}</h1>
  <p className="mt-2 text-sm text-slate-500">{user.email}</p>
  <div className="mt-8 rounded-2xl border border-dashed border-slate-300 bg-white p-8 text-center text-slate-500">产品空间将在 Task 9 接入。</div>
</div>
```

- [ ] **Step 4：接入 `/app` 路由入口**

将 `app/app/page.tsx` 保持为静态路由组合，仅使用既有 `AppShell` 包裹 `<AuthenticatedApp />`：

```tsx
import { AuthenticatedApp } from "@/components/app/authenticated-app";
import { AppShell } from "@/components/app-shell";

export default function AppPage() {
  return <AppShell><AuthenticatedApp /></AppShell>;
}
```

当前用户昵称与邮箱只在 `AuthenticatedApp` 成功状态中渲染；不得在该页请求 spaces。

- [ ] **Step 5：验证通过并提交**

```powershell
npm.cmd run test -- components/app/authenticated-app.test.tsx
npm.cmd run lint
git add apps/web/components/app/authenticated-app.tsx apps/web/components/app/authenticated-app.test.tsx apps/web/app/app/page.tsx
git commit -m "feat: protect frontend app route"
```

### Task 5：运行完整验证与浏览器烟雾测试

**Files:**

- Modify: `README.md`（仅将下一步从 Task 8 更新为 Task 9，并补充 Task 8 的真实认证检查命令）

- [ ] **Step 1：更新完成状态说明**

README 必须准确说明：Task 8 已实现注册、登录、`/app` 当前用户校验；Task 9 才实现空间列表与创建。不得声称实现了退出登录、空间列表或 Cookie 可被前端读取。

- [ ] **Step 2：运行前端完整自动化验证**

```powershell
npm.cmd run test
npm.cmd run check:routes
npm.cmd exec tsc -- --noEmit
npm.cmd run lint
npm.cmd run build
npm.cmd audit --omit=dev
```

预期：测试全部通过，四条既有路由仍存在，类型检查/lint/build 成功，生产依赖审计无漏洞。

- [ ] **Step 3：运行本地浏览器烟雾验证**

在后端与前端均已使用本地 `.env` 启动的前提下，验证以下序列：注册新邮箱后进入 `/login`；登录后跳转 `/app` 并显示昵称；刷新 `/app` 保持登录；清除站点 Cookie 后直访 `/app` 跳转 `/login`。浏览器 Network 中不应出现 `/spaces` 请求，前端存储中不应出现 JWT。

- [ ] **Step 4：提交完成说明**

```powershell
git add README.md
git commit -m "docs: record Task 8 completion"
```

## 计划自检

- 设计覆盖：注册跳转登录、登录跳转应用、`/auth/me`、401 与非 401 分流、Cookie 边界、最小校验、重复提交、测试和浏览器烟雾验证均有对应任务。
- 范围控制：计划没有后端接口改动、退出登录、空间请求、状态库、Server Actions、middleware 或部署。
- 类型一致性：`CurrentUser` 对应后端 `UserResponse` 的 JSON 字段；`RegisterInput.displayName` 在请求边界显式映射为 `display_name`。
