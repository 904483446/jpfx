# V0.1 Task 4：用户登录与退出设计

## 目标

实现 `POST /api/v1/auth/login` 和 `POST /api/v1/auth/logout`。用户使用邮箱和密码登录后，后端签发 7 天有效的 JWT，并通过 httpOnly Cookie 保存登录态；退出时清除该 Cookie。

本任务只建立登录态的签发与清除能力。Cookie 解析、当前用户查询和受保护接口依赖留到 Task 5。

## 已确认决策

- 使用无状态 JWT，不新增数据库会话表。
- JWT 使用 HS256，`sub` 保存用户 UUID，并包含 `iat` 和 `exp`。
- 登录态有效期为 7 天。
- Cookie 名称为 `access_token`。
- Cookie 使用 `HttpOnly=true`、`SameSite=Lax`、`Path=/`。
- 本地开发默认 `Secure=false`，生产环境通过配置设置为 `true`。
- 邮箱不存在与密码错误统一返回相同的 401 错误，避免邮箱枚举。
- 登出保持幂等，无论 Cookie 是否存在或有效都返回 204。
- JWT 使用成熟的 PyJWT 实现，不自行实现加密或签名算法。

## 接口契约

### 登录

`POST /api/v1/auth/login`

请求：

```json
{
  "email": "user@example.com",
  "password": "valid-password"
}
```

邮箱在校验前去除首尾空格并转为小写。密码长度限制与注册保持一致，为 8–128 字符。

成功时返回 HTTP 200 和用户公开信息：

```json
{
  "id": "00000000-0000-0000-0000-000000000000",
  "email": "user@example.com",
  "display_name": "示例用户",
  "is_admin": false,
  "created_at": "2026-07-11T00:00:00Z",
  "updated_at": "2026-07-11T00:00:00Z"
}
```

响应不得包含密码、密码哈希或 JWT 正文。JWT 只写入 Cookie。

邮箱不存在或密码错误时统一返回 HTTP 401：

```json
{
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "邮箱或密码错误",
    "details": {}
  }
}
```

请求字段不合法时沿用统一 HTTP 422 `VALIDATION_ERROR` 响应。

### 退出

`POST /api/v1/auth/logout`

无请求体。始终返回 HTTP 204，不返回响应体。响应通过相同 Cookie 名和 `Path=/` 清除 `access_token`。

## 组件设计

### 配置

在 Settings 中增加：

- `jwt_secret: str | None = None`
- `access_token_expire_days: int = 7`
- `auth_cookie_name: str = "access_token"`
- `auth_cookie_secure: bool = False`

`.env.example` 保留安全占位值和配置名，不提交真实 JWT 密钥。只有签发 Token 时才要求 `JWT_SECRET` 存在，避免健康检查无条件依赖鉴权配置。

### Schema

新增 `LoginRequest`，负责邮箱规范化、合法邮箱校验以及密码长度边界。登录响应复用现有 `UserResponse`。

### 安全模块

现有密码哈希与验证函数保持不变。新增 JWT 签发函数，其输入为用户 UUID 和可测试的当前时间，输出 HS256 Token。Token 包含：

- `sub`：用户 UUID 字符串
- `iat`：签发时间
- `exp`：签发时间加 7 天

缺少 `JWT_SECRET` 时抛出明确的运行时配置错误，不使用默认生产密钥。

### 服务层

新增认证函数：

1. 按规范化邮箱查询用户。
2. 用户不存在时返回统一 `INVALID_CREDENTIALS`。
3. 用户存在时使用 Argon2 验证密码。
4. 密码不匹配时返回相同的 `INVALID_CREDENTIALS`。
5. 成功时返回用户，由路由负责签发 Token 和设置 Cookie。

服务层不读取或写入 Cookie，保持 HTTP 与业务逻辑边界清晰。

### 路由层

登录路由调用认证服务，签发 JWT，并通过 FastAPI Response 设置 Cookie：

- `httponly=True`
- `samesite="lax"`
- `secure=settings.auth_cookie_secure`
- `path="/"`
- `max_age=604800`

登出路由使用相同 Cookie 名和路径调用 `delete_cookie`，返回 204。

## 安全边界

- 不区分用户不存在与密码错误的公开响应。
- 密码、密码哈希、JWT 和 Cookie 内容不得进入日志或错误响应。
- 不把真实 JWT 密钥写入代码、`.env.example` 或 Git。
- HS256 只使用服务端密钥签名；客户端无法读取 httpOnly Cookie。
- `SameSite=Lax` 降低跨站请求携带 Cookie 的风险。
- 生产部署必须将 `AUTH_COOKIE_SECURE=true`，确保 Cookie 仅通过 HTTPS 发送。

## 测试策略

按 TDD 的 RED→GREEN 顺序覆盖：

- JWT 使用 HS256，包含正确的 `sub`、`iat`、`exp` 和 7 天有效期。
- 缺少 `JWT_SECRET` 时拒绝签发 Token。
- 正确邮箱密码认证成功。
- 登录邮箱支持大小写和首尾空格规范化。
- 不存在邮箱和错误密码返回完全相同的 401。
- 登录成功返回公开用户字段，不包含敏感字段。
- 登录 Cookie 包含 HttpOnly、SameSite=Lax、Path、Max-Age，并覆盖 Secure 配置。
- 登出返回 204 并清除 Cookie。
- 未登录调用登出仍成功。
- 使用真实 PostgreSQL 测试数据库验证登录查询与密码校验。
- 最终运行 Ruff、格式检查、完整 pytest、pip check、Alembic 漂移检查和真实 Uvicorn 登录/退出冒烟验证。

## 不在本任务范围

- `GET /api/v1/auth/me`
- `get_current_user`
- 受保护业务接口
- Refresh Token
- Token 黑名单或主动撤销已签发 JWT
- 多设备会话管理
- 登录限流、验证码、找回密码
- 前端登录页面

这些内容分别由 Task 5 或后续任务处理，不在 Task 4 提前实现。
