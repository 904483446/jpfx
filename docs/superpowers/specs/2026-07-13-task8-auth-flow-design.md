# Task 8：前端登录注册流程设计

**日期：** 2026-07-13
**状态：** 待用户审阅
**范围：** V0.1 Task 8，仅实现前端注册、登录与当前用户鉴权流程。

## 目标

在既有 Next.js 静态骨架上接入 FastAPI 认证接口，使用户能够注册、登录并访问受保护的 `/app`。前端不读取或存储 Cookie/JWT，认证状态始终由后端 `access_token` httpOnly Cookie 维持。

## 已确认的用户流程

1. 用户在 `/register` 输入昵称、邮箱和密码并提交 `POST /auth/register`。
2. 注册成功后跳转到 `/login`，不自动登录。
3. 用户在 `/login` 输入邮箱和密码并提交 `POST /auth/login`。
4. 后端通过响应写入 httpOnly Cookie；登录成功后前端跳转 `/app`。
5. `/app` 加载时调用 `GET /auth/me`：成功时展示当前用户基本信息与既有静态应用壳；收到 `UNAUTHORIZED` 时跳转 `/login`。

## 架构与文件边界

- 保持 `app/login/page.tsx`、`app/register/page.tsx` 与 `app/app/page.tsx` 为路由入口。
- 新建小型客户端组件承载表单状态、客户端校验、提交中状态、接口调用与跳转；路由入口继续负责组合既有视觉外壳。
- 扩展 `lib/api-client.ts` 的调用方式或补充类型定义，但所有请求必须继续通过该文件，基础地址只能来自 `NEXT_PUBLIC_API_BASE_URL`，且默认 `credentials: "include"`。
- 认证响应只在内存中用于渲染当前用户，不写入 localStorage、sessionStorage 或 JavaScript Cookie。
- `/app` 仅展示当前用户信息与 Task 7 的既有静态应用壳内容；不请求、展示或创建产品空间（Task 9）。

## 表单规则与错误处理

- 注册字段：`display_name`、`email`、`password`；登录字段：`email`、`password`。
- 客户端只做最小校验：必填、邮箱格式、密码 8–128 字符；服务端仍是最终校验来源。
- 提交期间禁用按钮，避免重复请求。
- `ApiClientError` 中的后端中文 `message` 直接展示给用户；配置缺失或网络失败显示 API Client 已定义的通用中文错误，不显示响应正文、Cookie 或原始异常。
- 注册与登录成功后不显示密码，也不记录输入值。

## 路由保护与加载状态

- `/app` 的鉴权检查在客户端进行，检查期间显示非敏感加载状态。
- 仅对 `UNAUTHORIZED` 执行 `router.replace("/login")`；其他错误保留在当前页并显示通用错误和重试入口，避免将服务故障误判为未登录。
- Task 8 不实现 middleware、服务端代理、Server Actions、退出登录或全局状态库。

## 测试与验收

- 先为客户端表单和 `/app` 鉴权行为写失败测试，再完成最小实现。
- 覆盖：注册成功跳转 `/login`、登录成功跳转 `/app`、后端中文错误显示、提交中防重复、`/auth/me` 成功渲染用户、401 跳转 `/login`、非 401 错误不跳转。
- 运行 `npm.cmd run test`、`npm.cmd run check:routes`、`npm.cmd exec tsc -- --noEmit`、`npm.cmd run lint` 和 `npm.cmd run build`。
- 在前后端本地运行时做浏览器烟雾验证：注册、登录、刷新 `/app` 保持会话、未登录直访 `/app` 跳转登录。

## 非目标

- 不改后端认证接口、Cookie 参数、JWT 密钥或数据库模型。
- 不实现空间列表、新建空间、文档、RAG、Agent、报告、退出登录或部署。
