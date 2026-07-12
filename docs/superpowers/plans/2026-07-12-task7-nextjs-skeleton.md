# Task 7：前端 Next.js 骨架实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use \`executing-plans\` to implement this plan task-by-task. Steps use checkbox (\`- [ ]\`) syntax for tracking.

**Goal:** 在 \`apps/web\` 交付符合已确认视觉方向的 Next.js 静态骨架、可复用 API Client 和四个可访问路由。

**Architecture:** Next.js App Router 负责页面与静态路由，Tailwind CSS 负责布局和设计 tokens，shadcn/ui 提供 \`Button\`、\`Input\`。 \`lib/api-client.ts\` 是唯一的后端请求基础设施，默认携带 Cookie，但不创建具体认证或空间请求。

**Tech Stack:** Next.js、React、TypeScript、Tailwind CSS、shadcn/ui、Vitest、npm.cmd。

---

## 文件结构

| 文件 | 职责 |
| --- | --- |
| \`apps/web/app/*\` | 根布局与四个静态路由。 |
| \`apps/web/components/*\` | 品牌、认证外壳、应用壳和首页步骤。 |
| \`apps/web/lib/api-client.ts\` | 基地址、Cookie 请求配置、中文错误解析。 |
| \`apps/web/lib/api-client.test.ts\` | API Client 单元测试。 |
| \`apps/web/.env.example\` | 前端 API 基地址示例。 |

### Task 1：创建可验证的 Next.js 基础项目

**Files:**

- Delete: \`apps/web/.gitkeep\`
- Create: \`apps/web/package.json\`、\`apps/web/next.config.ts\`、\`apps/web/tsconfig.json\`、\`apps/web/app/layout.tsx\`、\`apps/web/app/globals.css\`、\`apps/web/app/page.tsx\`
- Create: \`apps/web/components.json\`、\`apps/web/components/ui/button.tsx\`、\`apps/web/components/ui/input.tsx\`、\`apps/web/vitest.config.ts\`、\`apps/web/.env.example\`
- Modify: \`.gitignore\`

- [ ] **Step 1: 删除占位文件并生成 Next.js App Router 项目**

使用 \`apply_patch\` 删除 \`apps/web/.gitkeep\`。在 \`apps/web\` 执行：

\`\`\`powershell
npm.cmd create next-app@latest . -- --ts --tailwind --eslint --app --use-npm --import-alias "@/*"
\`\`\`

预期：生成 TypeScript、Tailwind、ESLint、App Router 项目；不选择 \`src/\` 目录，页面路径保持 \`app/*\`。

- [ ] **Step 2: 安装 shadcn/ui 与 Vitest**

\`\`\`powershell
npx.cmd shadcn@latest init --yes --style new-york --base-color slate --css-variables
npx.cmd shadcn@latest add button input
npm.cmd install -D vitest
\`\`\`

创建 \`vitest.config.ts\`：

\`\`\`ts
import { defineConfig } from "vitest/config";

export default defineConfig({
  test: { environment: "node" },
});
\`\`\`

在 \`package.json\` 的 \`scripts\` 增加：

\`\`\`json
"test": "vitest run"
\`\`\`

- [ ] **Step 3: 添加环境变量示例与忽略规则**

创建 \`apps/web/.env.example\`：

\`\`\`dotenv
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000/api/v1
\`\`\`

使用 \`apply_patch\` 在根 \`.gitignore\` 的本地环境段加入：

\`\`\`gitignore
apps/web/.env.local
\`\`\`

- [ ] **Step 4: 验证基础项目**

\`\`\`powershell
npm.cmd run lint
npm.cmd run build
\`\`\`

预期：lint 与 build 成功。Vitest 此时尚无测试文件，不运行 \`npm.cmd run test\`。

- [ ] **Step 5: 提交基础项目**

\`\`\`powershell
git add .gitignore apps/web
git commit -m "chore: scaffold Next.js frontend"
\`\`\`

### Task 2：以 TDD 实现 API Client

**Files:**

- Create: \`apps/web/lib/api-client.ts\`
- Create: \`apps/web/lib/api-client.test.ts\`

- [ ] **Step 1: 写失败测试**

创建 \`lib/api-client.test.ts\`：

\`\`\`ts
import { afterEach, describe, expect, it, vi } from "vitest";
import { ApiClientError, apiRequest, getApiBaseUrl } from "./api-client";

const originalBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL;

afterEach(() => {
  process.env.NEXT_PUBLIC_API_BASE_URL = originalBaseUrl;
  vi.unstubAllGlobals();
});

describe("api client", () => {
  it("缺少 API 基地址时明确报错", () => {
    delete process.env.NEXT_PUBLIC_API_BASE_URL;
    expect(() => getApiBaseUrl()).toThrow("缺少 NEXT_PUBLIC_API_BASE_URL 配置");
  });

  it("使用基地址和 httpOnly Cookie 选项发送请求", async () => {
    process.env.NEXT_PUBLIC_API_BASE_URL = "http://127.0.0.1:8000/api/v1/";
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ status: "ok" }), { status: 200 }),
    );
    vi.stubGlobal("fetch", fetchMock);

    await apiRequest<{ status: string }>("/health");

    expect(fetchMock).toHaveBeenCalledWith(
      "http://127.0.0.1:8000/api/v1/health",
      expect.objectContaining({ credentials: "include" }),
    );
  });

  it("把后端中文错误结构转换为 ApiClientError", async () => {
    process.env.NEXT_PUBLIC_API_BASE_URL = "http://127.0.0.1:8000/api/v1";
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ error: { code: "UNAUTHORIZED", message: "登录状态无效或已过期", details: {} } }), { status: 401 }),
    ));

    await expect(apiRequest("/auth/me")).rejects.toMatchObject<ApiClientError>({
      code: "UNAUTHORIZED",
      message: "登录状态无效或已过期",
      details: {},
    });
  });
});
\`\`\`

- [ ] **Step 2: RED，确认测试失败**

\`\`\`powershell
npm.cmd run test -- lib/api-client.test.ts
\`\`\`

预期：失败，提示找不到 \`./api-client\`。

- [ ] **Step 3: 写最小实现**

创建 \`lib/api-client.ts\`：

\`\`\`ts
export class ApiClientError extends Error {
  constructor(
    public readonly code: string,
    message: string,
    public readonly details: Record<string, unknown> = {},
  ) {
    super(message);
    this.name = "ApiClientError";
  }
}

export function getApiBaseUrl(): string {
  const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL?.trim();
  if (!baseUrl) throw new Error("缺少 NEXT_PUBLIC_API_BASE_URL 配置");
  return baseUrl.replace(/\/$/, "");
}

export async function apiRequest<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(\`\${getApiBaseUrl()}/\${path.replace(/^\//, "")}\`, {
    ...init,
    credentials: "include",
  });
  const body: unknown = await response.json().catch(() => null);

  if (!response.ok) {
    const error = body as { error?: { code?: string; message?: string; details?: Record<string, unknown> } } | null;
    if (error?.error?.code && error.error.message) {
      throw new ApiClientError(error.error.code, error.error.message, error.error.details ?? {});
    }
    throw new ApiClientError("NETWORK_ERROR", "网络请求失败，请稍后重试");
  }
  return body as T;
}
\`\`\`

- [ ] **Step 4: GREEN，运行单元测试与前端检查**

\`\`\`powershell
npm.cmd run test -- lib/api-client.test.ts
npm.cmd run lint
npm.cmd run build
\`\`\`

预期：全部通过。

- [ ] **Step 5: 提交 API Client**

\`\`\`powershell
git add apps/web/lib apps/web/package.json apps/web/vitest.config.ts
git commit -m "feat: add frontend API client foundation"
\`\`\`

### Task 3：实现共享视觉组件与四个静态路由

**Files:**

- Create: \`apps/web/components/brand-mark.tsx\`
- Create: \`apps/web/components/auth/auth-shell.tsx\`
- Create: \`apps/web/components/app-shell.tsx\`
- Create: \`apps/web/components/landing/steps.tsx\`
- Modify: \`apps/web/app/layout.tsx\`、\`apps/web/app/globals.css\`、\`apps/web/app/page.tsx\`
- Create: \`apps/web/app/login/page.tsx\`、\`apps/web/app/register/page.tsx\`、\`apps/web/app/app/page.tsx\`

- [ ] **Step 1: 写失败的路由存在性检查**

创建 \`apps/web/scripts/check-routes.mjs\`：

\`\`\`js
import { access } from "node:fs/promises";

for (const routeFile of ["app/page.tsx", "app/login/page.tsx", "app/register/page.tsx", "app/app/page.tsx"]) {
  await access(new URL(\`../\${routeFile}\`, import.meta.url));
}
console.log("STATIC_ROUTE_FILES=ok");
\`\`\`

在 \`package.json\` 增加：

\`\`\`json
"check:routes": "node scripts/check-routes.mjs"
\`\`\`

- [ ] **Step 2: RED，确认缺少路由文件**

\`\`\`powershell
npm.cmd run check:routes
\`\`\`

预期：失败，首先报告缺少 \`app/login/page.tsx\`。

- [ ] **Step 3: 实现共享组件和页面**

固定组件接口：

\`\`\`tsx
// components/brand-mark.tsx
import Link from "next/link";

export function BrandMark() {
  return <Link className="font-bold tracking-tight text-slate-950" href="/">◇ 竞品智研台</Link>;
}
\`\`\`

\`\`\`tsx
// components/auth/auth-shell.tsx
import type { ReactNode } from "react";
import { BrandMark } from "@/components/brand-mark";

export function AuthShell({ title, description, children, footer }: {
  title: string; description: string; children: ReactNode; footer: ReactNode;
}) {
  return <main className="grid min-h-screen place-items-center bg-slate-50 p-6"><section className="w-full max-w-md rounded-2xl border bg-white p-8 shadow-sm"><BrandMark /><h1 className="mt-10 text-3xl font-semibold">{title}</h1><p className="mt-2 text-sm text-slate-500">{description}</p><div className="mt-8">{children}</div><div className="mt-6 text-center text-sm text-slate-500">{footer}</div></section></main>;
}
\`\`\`

\`app/page.tsx\` 使用 \`Link\` 输出主按钮“登录”到 \`/login\`、次按钮“注册”到 \`/register\`，并渲染“整理资料、分析竞品、输出报告”三张步骤卡。认证页只使用未绑定提交处理器的 \`Input\` 和 \`Button type="button"\`，并输出已确认的互跳链接。 \`app/app/page.tsx\` 必须只呈现 \`AppShell\` 和静态文本：\`Task 8 接入当前用户；Task 9 展示空间列表。\`

\`globals.css\` 使用 CSS variables 与 Tailwind utilities 固定：导航 \`#0a1f33\`、主操作 \`#1677ff\`、强调 \`#14b8a6\`、内容背景 \`#f6f9fb\`。不得创建 API 调用、表单状态或鉴权代码。

- [ ] **Step 4: GREEN，确认路由和构建通过**

\`\`\`powershell
npm.cmd run check:routes
npm.cmd run lint
npm.cmd run build
\`\`\`

预期：输出 \`STATIC_ROUTE_FILES=ok\`，lint 与 production build 均成功。

- [ ] **Step 5: 真实浏览器烟雾验证**

启动：

\`\`\`powershell
npm.cmd run dev
\`\`\`

访问 \`http://localhost:3000/\`、\`/login\`、\`/register\`、\`/app\`。验证：首页主/次按钮分别转到 \`/login\`、\`/register\`；认证页有互跳链接；\`/app\` 只含静态应用壳，Network 不出现 \`/api/v1/auth/me\` 或 \`/api/v1/spaces\`。

- [ ] **Step 6: 提交静态页面**

\`\`\`powershell
git add apps/web/app apps/web/components apps/web/scripts apps/web/package.json
git commit -m "feat: add Task 7 frontend skeleton pages"
\`\`\`

### Task 4：记录完成状态并做最终验证

**Files:**

- Modify: \`README.md\`

- [ ] **Step 1: 更新 README**

将“下一步是 Task 7：前端 Next.js 骨架”改为 Task 7 已完成、下一步为 Task 8 前端登录注册流程；补充前端启动、环境变量复制与检查命令。不得声称已经实现真实登录、注册、\`/app\` 鉴权或空间列表。

- [ ] **Step 2: 运行最终前端验证**

在 \`apps/web\` 串行执行：

\`\`\`powershell
npm.cmd run test
npm.cmd run check:routes
npm.cmd run lint
npm.cmd run build
npm.cmd audit --omit=dev
\`\`\`

预期：单元测试、路由检查、lint、build 通过；审计无高危生产依赖漏洞。若 audit 因网络不可用失败，如实记录验证缺口。

- [ ] **Step 3: 回归后端并检查 Git 状态**

在 \`services/api\` 串行执行：

\`\`\`powershell
.\.venv\Scripts\python.exe -m ruff check --no-cache .
.\.venv\Scripts\python.exe -m ruff format --check --no-cache .
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider -q
.\.venv\Scripts\python.exe -m pip check
\`\`\`

然后执行：

\`\`\`powershell
git status --short --branch
\`\`\`

- [ ] **Step 4: 提交完成说明**

\`\`\`powershell
git add README.md
git commit -m "docs: record Task 7 completion"
\`\`\`

## 计划自检

- 设计覆盖：四个路由、静态跳转、shadcn/ui、环境变量、API Client、中文错误、Cookie 选项、视觉 tokens、范围排除、lint/build/浏览器验证均有对应任务。
- TDD 覆盖：Task 2 先写 API Client 失败测试再实现；Task 3 先写路由存在性失败检查再补齐页面。静态视觉没有运行时业务逻辑，以 build 与浏览器烟雾作为行为验证。
- 范围控制：没有认证请求、Cookie 读取、路由守卫、空间 CRUD、文档、RAG、Agent 或前端状态库。

