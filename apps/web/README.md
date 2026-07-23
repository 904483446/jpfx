# JPFX Web

JPFX 的 Next.js 前端，提供公开首页、认证、产品空间、文档与检索、竞品分析任务、报告详情及模型设置页面。应用通过 Cookie 会话调用 FastAPI；浏览器端不读取、保存或展示 JWT 与 API Key。

## 本地启动

```powershell
cd apps/web
# 创建 .env.local，只设置 NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000/api/v1
npm.cmd ci
npm.cmd run dev
```

打开 `http://127.0.0.1:3000`。完整的环境变量、安全边界与后端启动步骤请参阅仓库根目录的 [README](../../README.md)。

## 质量门禁

```powershell
npm.cmd test
npm.cmd run check:routes
npx.cmd tsc --noEmit
npm.cmd run lint
npm.cmd run build
```

生产部署目标为 Vercel；部署与公开 Demo 属于 V1.0 工作，尚未在本仓库完成验证。
