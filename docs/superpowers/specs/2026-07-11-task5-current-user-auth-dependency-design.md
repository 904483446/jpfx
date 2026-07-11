# V0.1 Task 5：当前用户与鉴权依赖设计

## 目标

实现 `GET /api/v1/auth/me` 和可复用的 `get_current_user` FastAPI 依赖。依赖从 Task 4 签发的 httpOnly JWT Cookie 解析用户身份，供当前用户接口和后续业务接口复用。

## 已确认决策

- Cookie 名称沿用 Settings 的 `auth_cookie_name`，默认 `access_token`。
- 仅接受 HS256 JWT，并使用现有 `JWT_SECRET` 验证签名与过期时间。
- JWT 的 `sub` 必须是 UUID；解析后按用户主键查询数据库。
- Token 缺失、过期、签名无效、格式错误、`sub` 缺失或非法、用户已删除均返回同一公开错误。
- 未授权公开响应固定为 HTTP 401：

```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "登录状态无效或已过期",
    "details": {}
  }
}
```

- `/auth/me` 成功时复用 `UserResponse`，不返回密码、密码哈希或 JWT。
- 无效 Cookie 不在 `/auth/me` 中主动清除；依赖仅负责身份解析，客户端可调用既有 `/auth/logout` 清除 Cookie。
- 缺失或弱 `JWT_SECRET` 沿用 Task 4 的服务端配置错误，不伪装成 401。

## 接口契约

### 获取当前用户

`GET /api/v1/auth/me`

成功时返回 HTTP 200：

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

未授权时返回上述统一 HTTP 401 响应。

## 组件设计

### 业务异常

在鉴权模块中集中构造 `unauthorized()` 业务异常，避免路由、依赖和后续受保护接口产生不同的 401 错误格式。

### 鉴权依赖

新增 `app/api/deps.py`：

1. 从请求 Cookie 读取 `settings.auth_cookie_name`。
2. Cookie 缺失时抛出 `UNAUTHORIZED`。
3. 使用 `jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])` 验证 Token。
4. 捕获 PyJWT 的解码、签名、过期与声明异常，统一抛出 `UNAUTHORIZED`。
5. 将 `sub` 解析为 UUID；缺失或非法时统一抛出 `UNAUTHORIZED`。
6. 使用同步 SQLAlchemy Session 查询 `User.id`。
7. 用户不存在时统一抛出 `UNAUTHORIZED`。
8. 返回完整 `User` ORM 实例，仅供后续服务或路由使用。

依赖不写 Cookie、不提交事务、不记录 Token 内容。

### 路由

在现有 auth router 增加 `/me`，通过 `Depends(get_current_user)` 获取 User，再以 `UserResponse.model_validate()` 输出公开字段。

## 安全边界

- 解码显式固定为 HS256，禁止算法降级或由 Token Header 选择算法。
- `sub` 只作为用户查询标识，最终身份以数据库仍存在的用户记录为准。
- 所有无效登录态得到相同公开错误，避免暴露 Token 或用户存在性细节。
- 依赖不打印 Cookie、JWT 或密码。
- 后续业务路由必须通过该依赖取得当前用户，并用其 `id` 过滤查询。

## 测试策略

按 TDD 的 RED→GREEN 顺序覆盖：

- 有效登录 Cookie 返回当前用户公开字段。
- 响应不包含密码、密码哈希或 Cookie Token。
- 缺失 Cookie、篡改签名、过期 Token、无 `sub`、非 UUID `sub`、用户不存在均返回完全相同的 401。
- 使用测试探针路由证明后续受保护接口可复用 `get_current_user`。
- 真实 PostgreSQL 测试数据库验证身份查询。
- 最终运行 Ruff、格式检查、完整 pytest、pip check、Alembic 漂移检查和 Uvicorn 冒烟验证。

## 不在本任务范围

- 产品空间或其他真实业务路由
- Token 刷新、黑名单、数据库会话表
- 使无效 Cookie 自动失效的响应策略
- 前端页面、路由守卫或 API Client
- 角色权限和管理员功能

这些内容由后续 Task 6 及前端任务处理。
