# Task 8：本地前后端 CORS 补充设计

**日期：** 2026-07-14
**状态：** 已确认，待实施
**范围：** 为 Task 8 的浏览器认证联调补齐最小 FastAPI CORS 配置。

## 问题

开发前端运行在 `http://127.0.0.1:3000`，后端运行在 `http://127.0.0.1:8000`。端口不同属于不同源；浏览器会拦截前端对后端认证接口的凭据请求。Task 7 静态页面不受影响，但 Task 8 的注册、登录和 `/auth/me` 浏览器联调无法完成。

## 决策

采用 FastAPI `CORSMiddleware`，保持前端通过 `NEXT_PUBLIC_API_BASE_URL` 直接访问 `/api/v1` 的既有架构；不采用 Next.js rewrite/proxy。

## 安全边界

- 默认仅允许 `http://127.0.0.1:3000`；允许来源必须由非敏感配置项提供，便于部署环境显式覆盖。
- `allow_credentials=True`，使浏览器可以携带后端设置的 httpOnly `access_token` Cookie。
- 不使用 `allow_origins=["*"]`，因为携带凭据时通配来源不安全且浏览器不接受。
- 只允许认证联调需要的 `GET`、`POST` 与 `OPTIONS` 方法，以及 `Content-Type` 请求头；不放宽到任意来源、任意方法或任意请求头。
- CORS 不读取、返回或存储 Cookie/JWT；Cookie 仍仅由后端 `Set-Cookie` 响应写入。

## 实现边界

- 在 `services/api/app/core/config.py` 增加非敏感的允许来源配置及明确解析规则。
- 在 `services/api/app/main.py` 的应用工厂中注册 `CORSMiddleware`，且在路由处理前生效。
- 新增后端应用级测试：允许源的预检响应含正确 `Access-Control-Allow-Origin` 与 `Access-Control-Allow-Credentials`；未知源不获得允许源响应头。
- 不改认证路由、Cookie 参数、JWT、数据库模型、前端 API Client 或 Next.js 配置。

## 验收

1. 后端自动化测试覆盖允许和拒绝来源的 CORS 响应。
2. 既有后端测试、前端测试、类型检查、lint 与 build 继续通过。
3. 在用户已配置本地环境后，浏览器可以完成注册、登录、刷新 `/app` 保持会话，以及无登录态访问 `/app` 跳转 `/login`。
4. 浏览器不发起 `/spaces` 请求，前端存储中没有 JWT。
