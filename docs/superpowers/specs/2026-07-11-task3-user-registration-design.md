# Task 3 用户注册设计

## 目标

实现 `POST /api/v1/auth/register`，将通过校验的用户写入 PostgreSQL，并以 Argon2id 哈希保存密码。Task 3 只完成注册，不实现登录态、Cookie、JWT、当前用户或默认产品空间。

## API 契约

请求：

```json
{
  "email": "user@example.com",
  "password": "example-password",
  "display_name": "示例用户"
}
```

字段规则：

- `email`：合法邮箱；去除首尾空格后统一转为小写；数据库保存规范化结果。
- `password`：长度 8–128 字符；不强制大小写、数字或特殊字符组合。
- `display_name`：去除首尾空格后长度 1–100 字符。

成功响应使用 HTTP `201 Created`：

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

响应不得包含 `password` 或 `password_hash`。

重复邮箱返回 HTTP `409 Conflict`：

```json
{
  "error": {
    "code": "EMAIL_ALREADY_REGISTERED",
    "message": "该邮箱已注册",
    "details": {}
  }
}
```

字段校验错误继续使用现有 HTTP 422 统一结构，外层中文消息为“请求参数校验失败”。

## 模块边界

- `schemas/auth.py`：定义注册请求和用户响应 Schema，只负责输入规范化、字段校验与输出脱敏。
- `core/security.py`：封装 `pwdlib` 的 Argon2id 密码哈希与校验接口，不记录或返回明文密码。
- `services/auth_service.py`：负责邮箱唯一性检查、密码哈希、用户写入、事务提交和唯一约束冲突转换。
- `api/v1/auth.py`：声明 HTTP 路由，注入数据库 Session，调用服务并返回响应。
- `core/errors.py`：增加可复用的业务异常类型及处理器，保持统一错误结构。

路由不直接访问 SQLAlchemy 查询细节，Schema 不执行数据库操作，密码工具不依赖 FastAPI 或数据库。

## 注册数据流

1. FastAPI/Pydantic 解析请求并执行字段校验。
2. Schema 去除邮箱与昵称首尾空格；邮箱转为小写。
3. 路由通过 `get_db_session` 获取同步 SQLAlchemy Session。
4. 服务查询规范化邮箱是否存在；存在则抛出业务异常。
5. 安全模块使用 Argon2id 生成密码哈希。
6. 服务创建 `User`，执行 `commit` 并刷新数据库生成字段。
7. 响应 Schema 从 ORM 实例生成脱敏响应。

## 并发与错误处理

注册使用“预查询 + 数据库唯一约束”双层保护。预查询提供正常情况下的快速中文错误；如果两个请求同时通过预查询，后提交者会触发 `uq_users_email`，服务捕获 `IntegrityError`、回滚事务并返回同样的 `409 EMAIL_ALREADY_REGISTERED`。

非邮箱唯一约束导致的 `IntegrityError` 不伪装成重复邮箱错误，应回滚后继续抛出，由现有 500 处理器记录并返回安全的统一响应。判断依据使用 PostgreSQL 约束名 `uq_users_email`，不解析本地化数据库错误文本。

业务异常处理器只向客户端返回明确的状态码、错误代码、中文消息和安全详情，不记录密码、请求体或 Cookie。

## 密码安全

- 使用 `pwdlib[argon2]` 的推荐 Argon2id 配置。
- 明文密码只在请求处理和哈希调用期间存在，不写入模型、日志或响应。
- `password_hash` 长度必须适配现有 `VARCHAR(255)`。
- 安全模块同时提供 `hash_password` 和 `verify_password`，后者供 Task 4 登录复用。

## 测试设计

遵循 TDD，使用真实 PostgreSQL 隔离测试库和事务回滚：

- 成功注册返回 201，并保存规范化邮箱和去空格昵称。
- 数据库保存值不是明文密码，且 Argon2id 校验成功。
- 响应中不存在 `password` 和 `password_hash`。
- 已存在邮箱返回中文 409。
- 不同大小写或首尾空格的同一邮箱视为重复。
- 通过模拟唯一约束竞争验证 `IntegrityError` 被转换并回滚。
- 空邮箱、非法邮箱、短密码、超长密码、空昵称和超长昵称返回统一 422。
- 现有健康检查、迁移、数据库约束测试继续通过。
- Ruff lint、Ruff format、pytest、pip check 和 Alembic 漂移检查全部通过。

## 依赖与范围

新增运行依赖：

- `pwdlib[argon2]`：Argon2id 密码哈希。
- `email-validator`：Pydantic 邮箱格式校验。

明确不在 Task 3 实现：

- 登录、退出、httpOnly Cookie、JWT。
- `GET /auth/me` 和鉴权依赖。
- 注册后自动登录。
- 默认产品空间或知识库创建。
- 前端注册页面。
- 邮件验证、验证码、密码找回、限流或风控。
