# JPFX Production Deployment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 JPFX 发布为 Vercel 前端、Railway FastAPI 服务和 Supabase PostgreSQL/pgvector 的可验证试运行环境。

**Architecture:** 浏览器访问 Vercel 域名的 `/api/v1/*`；Next.js rewrite 在服务端转发至 Railway，避免 Vercel 与 Railway 不同站点导致 Cookie 失效。Railway 使用 Supabase PostgreSQL，并将资料存储挂载到 Railway Persistent Volume。

**Tech Stack:** Next.js 16、FastAPI、Uvicorn、SQLAlchemy、Alembic、PostgreSQL 16、pgvector、Supabase、Railway、Vercel。

---

## 文件结构

- Create: `services/api/Dockerfile` — Railway Python 3.12 运行镜像。
- Create: `services/api/.dockerignore` — 排除虚拟环境、缓存与本地资料。
- Modify: `apps/web/next.config.ts` — 服务器端 `/api/*` 代理。
- Create: `apps/web/next.config.test.ts` — rewrite 行为测试。
- Modify: `.env.example` — 变量名称与非敏感示例。
- Modify: `README.md` — 部署说明与验证边界。
- Create: `docs/superpowers/handoffs/2026-07-30-production-deployment.md` — 无敏感值的发布证据。

### Task 1: 为同源 Cookie 代理补齐可测试的前端配置

**Files:**
- Modify: `apps/web/next.config.ts`
- Create: `apps/web/next.config.test.ts`
- Modify: `.env.example`

- [ ] **Step 1: 写出失败测试**

```ts
import { describe, expect, it, vi } from "vitest";
import { getApiProxyRewrites } from "./next.config";

describe("getApiProxyRewrites", () => {
  it("returns no external destination without API_PROXY_TARGET", () => {
    vi.stubEnv("API_PROXY_TARGET", "");
    expect(getApiProxyRewrites()).toEqual([]);
  });

  it("proxies the public API path to Railway", () => {
    vi.stubEnv("API_PROXY_TARGET", "https://jpfx-api.up.railway.app/");
    expect(getApiProxyRewrites()).toEqual([
      { source: "/api/:path*", destination: "https://jpfx-api.up.railway.app/api/:path*" },
    ]);
  });
});
```

- [ ] **Step 2: 运行测试并确认失败**

Run: `cd apps/web; npm.cmd test -- next.config.test.ts`

Expected: FAIL，提示 `getApiProxyRewrites` 未导出。

- [ ] **Step 3: 实现最小 rewrite**

```ts
import type { NextConfig } from "next";

export function getApiProxyRewrites() {
  const target = process.env.API_PROXY_TARGET?.trim().replace(/\/$/, "");
  return target ? [{ source: "/api/:path*", destination: `${target}/api/:path*` }] : [];
}

const nextConfig: NextConfig = {
  allowedDevOrigins: ["127.0.0.1", "localhost"],
  async rewrites() {
    return getApiProxyRewrites();
  },
};

export default nextConfig;
```

- [ ] **Step 4: 补充 `.env.example`**

```text
NEXT_PUBLIC_API_BASE_URL=/api/v1
API_PROXY_TARGET=https://your-railway-service.up.railway.app
DATABASE_URL=postgresql+psycopg://postgres.PROJECT_REF:YOUR_PASSWORD@HOST:5432/postgres?sslmode=require
AUTH_COOKIE_SECURE=true
DOCUMENT_STORAGE_ROOT=/app/storage
```

- [ ] **Step 5: 验证并提交**

Run: `cd apps/web; npm.cmd test; npm.cmd run check:routes; npx.cmd tsc --noEmit; npm.cmd run lint; npm.cmd run build`

Expected: 全部退出码为 0。

```powershell
git add apps/web/next.config.ts apps/web/next.config.test.ts .env.example
git commit -m "feat: proxy production API through web origin"
```

### Task 2: 将 FastAPI 制作为 Railway 可运行镜像

**Files:**
- Create: `services/api/Dockerfile`
- Create: `services/api/.dockerignore`

- [ ] **Step 1: 编写 Dockerfile**

```dockerfile
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app
COPY pyproject.toml ./
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./
RUN pip install --upgrade pip && pip install .
EXPOSE 8000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
```

- [ ] **Step 2: 编写 Docker 忽略清单**

```text
.venv/
.pytest_cache/
__pycache__/
*.py[cod]
tests/
storage/
```

- [ ] **Step 3: 本地构建并提交**

Run: `docker build -t jpfx-api:deployment-check services/api`

Expected: 镜像构建成功。`/api/v1/health` 只证明应用进程存活，不能替代数据库连通性验证。

```powershell
git add services/api/Dockerfile services/api/.dockerignore
git commit -m "build: add Railway API container"
```

### Task 3: 用户完成三平台配置

**Files:**
- Modify: `README.md`
- Create: `docs/superpowers/handoffs/2026-07-30-production-deployment.md`

- [ ] **Step 1: 创建 Supabase 项目并启用扩展**

1. 登录 Supabase，点击 **New project**，项目名填 `jpfx-production`，选择离用户最近的地区；数据库密码使用密码管理器生成并保存。
2. 打开 **SQL Editor → New query**，运行：

```sql
create extension if not exists vector;
create extension if not exists "uuid-ossp";
```

3. 在 **Connect** 选择兼容 IPv4 的连接方式。复制 URI 到密码管理器，仅用于 Railway 的 `DATABASE_URL`；不发送到聊天、不提交到 Git。

- [ ] **Step 2: 创建 Railway 后端服务**

1. **New Project → Deploy from GitHub repo**，选择 `904483446/jpfx`；完成合并后部署分支必须为 `main`。
2. 服务 **Settings → Root Directory** 填 `services/api`，构建方式选择 Dockerfile，Start Command 保持空白。
3. **Variables** 填 `DATABASE_URL`、`JWT_SECRET`、`AUTH_COOKIE_SECURE=true`、`CORS_ALLOWED_ORIGINS=https://YOUR_VERCEL_DOMAIN`、`DOCUMENT_STORAGE_ROOT=/app/storage`。
4. **Volumes** 创建 Persistent Volume，Mount Path 填 `/app/storage`。
5. **Deploy → Pre-deploy Command** 填 `alembic upgrade head`；**Healthcheck Path** 填 `/api/v1/health`；记录 Railway 公网域名但不记录任何变量值。

- [ ] **Step 3: 创建 Vercel 前端项目**

1. **Add New → Project**，导入 `904483446/jpfx`，Root Directory 选 `apps/web`，Framework 保持 Next.js。
2. **Environment Variables** 填 `NEXT_PUBLIC_API_BASE_URL=/api/v1` 与 `API_PROXY_TARGET=https://YOUR_RAILWAY_DOMAIN`；后者没有 `/api/v1` 后缀。
3. 点击 **Deploy**，把 Vercel 项目域名写入 Railway 的 `CORS_ALLOWED_ORIGINS`，不带末尾 `/`。
4. Railway 重新部署后，在 Vercel 执行一次 Redeploy，确保 rewrite 使用最终 Railway 域名。

- [ ] **Step 4: 浏览器验收与证据记录**

1. 打开 Vercel URL，注册仅用于验收的测试账号并登录。
2. 刷新后仍保持登录；退出登录后访问 `/app` 必须回到 `/login`。
3. 创建空间，上传无敏感 TXT，刷新后仍可见。
4. Railway 日志无迁移、连接或文件路径错误；Supabase Table Editor 可见对应记录。
5. 文档只记录 URL、成功步骤、HTTP 状态和未验证项；绝不记录连接串、Cookie、Token 或 API Key。

### Task 4: 预发布复核

**Files:**
- Modify: `README.md`
- Modify: `docs/superpowers/handoffs/2026-07-30-production-deployment.md`

- [ ] **Step 1: 运行全部门禁**

```powershell
cd services/api
.\.venv\Scripts\python.exe -m ruff check --no-cache .
.\.venv\Scripts\python.exe -m ruff format --check --no-cache .
.\.venv\Scripts\python.exe -m pytest -q
cd ../../apps/web
npm.cmd test
npm.cmd run check:routes
npx.cmd tsc --noEmit
npm.cmd run lint
npm.cmd run build
```

Expected: 每条命令退出码为 0；PR 的 GitHub Actions 四项检查均为绿色。

- [ ] **Step 2: 检查变更并发布**

Run: `git diff --check main...HEAD`

Expected: 退出码为 0；用户确认真实变量仅存在于平台网页后合并 PR，平台从 `main` 自动发布。

- [ ] **Step 3: 发布后检查**

Run: `curl.exe -fsS https://YOUR_RAILWAY_DOMAIN/api/v1/health`

Expected: `{"status":"ok"}`，然后重复 Task 3 Step 4。若失败，只记录失败步骤与 HTTP 状态，不删除线上数据库或资源。
