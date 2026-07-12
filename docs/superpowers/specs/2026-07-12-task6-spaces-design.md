# V0.1 Task 6：产品空间基础接口设计

## 目标

实现当前登录用户的产品空间最小闭环：列出空间、创建空间、查看单个空间。创建空间时自动创建一个默认知识库，为后续文档、任务和报告功能建立可靠的用户与空间隔离边界。

## 已确认范围

本任务只实现以下接口：

- `GET /api/v1/spaces`
- `POST /api/v1/spaces`
- `GET /api/v1/spaces/{space_id}`

不实现 `PATCH`、`DELETE`、前端页面、文档上传、RAG、Agent、报告、分页、排序参数、空间成员、角色权限或管理员功能。

## 数据与字段

复用现有 `Space` 和 `KnowledgeBase` 模型，不增加迁移。

### 创建空间请求

```json
{
  "name": "企业知识库 Copilot",
  "industry": "企业服务",
  "product_direction": "AI 知识库",
  "description": "面向内部知识问答的产品空间"
}
```

- `name` 必填，先去除首尾空白，再校验长度为 1–200。
- `industry`、`product_direction` 为可选字符串，提供时先去除首尾空白，空白结果规范为 `null`，最大长度为 200。
- `description` 为可选字符串，提供时先去除首尾空白，空白结果规范为 `null`。
- `user_id` 不从请求体接收，始终使用 `get_current_user` 返回的当前用户主键。

### 空间响应

列表、创建和详情均复用同一个公开空间响应模型：

```json
{
  "id": "00000000-0000-0000-0000-000000000000",
  "name": "企业知识库 Copilot",
  "industry": "企业服务",
  "product_direction": "AI 知识库",
  "description": "面向内部知识问答的产品空间",
  "created_at": "2026-07-12T00:00:00Z",
  "updated_at": "2026-07-12T00:00:00Z"
}
```

响应不暴露 `user_id`、`deleted_at` 或默认知识库详情。

## 接口契约

### `GET /api/v1/spaces`

- 成功：HTTP 200，返回当前用户拥有且 `deleted_at IS NULL` 的空间数组。
- 排序：按 `created_at` 倒序。
- 空列表：返回 `[]`。
- 未登录：由 `get_current_user` 统一返回 HTTP 401 `UNAUTHORIZED`。

### `POST /api/v1/spaces`

- 成功：HTTP 201，返回新建空间的公开字段。
- 同一事务内创建：
  1. `Space(user_id=current_user.id, ...)`
  2. `KnowledgeBase(user_id=current_user.id, space_id=space.id, name="默认知识库", description=None)`
- 空间或默认知识库任一步写入失败时回滚整个事务，不留下半成品空间或孤立知识库。
- 请求字段校验失败：统一 HTTP 422 `VALIDATION_ERROR`。
- 未登录：统一 HTTP 401 `UNAUTHORIZED`。

### `GET /api/v1/spaces/{space_id}`

- 成功：HTTP 200，返回当前用户拥有且未软删除的空间。
- 路径 UUID 无法解析：FastAPI 统一 HTTP 422 `VALIDATION_ERROR`。
- 空间不存在、已软删除或不属于当前用户：一律返回 HTTP 404：

```json
{
  "error": {
    "code": "SPACE_NOT_FOUND",
    "message": "产品空间不存在",
    "details": {}
  }
}
```

- 不先按 ID 查询再返回 403；查询条件始终同时包含 `Space.id == space_id`、`Space.user_id == current_user.id` 和 `Space.deleted_at.is_(None)`，避免泄露其他用户空间是否存在。

## 分层设计

- `app/api/v1/spaces.py`：路由定义、`get_current_user` 与数据库会话注入、Schema 序列化。
- `app/schemas/space.py`：`SpaceCreateRequest` 和 `SpaceResponse`，集中字段规范化与响应字段白名单。
- `app/services/space_service.py`：空间查询、隔离过滤、原子创建默认知识库与业务错误工厂。
- `app/core/errors.py`：新增复用的 `space_not_found()` 工厂，保持统一中文错误结构。
- `app/main.py`：注册 spaces router，使用既有 `/api/v1` 前缀。

路由不直接编写 ORM 查询；服务层不解析 Cookie、不签发 Token、不写 Cookie。

## 测试策略

使用现有真实隔离 PostgreSQL 夹具和 Task 5 的 Cookie JWT 认证方式。

- 未登录访问列表、创建、详情统一返回 `UNAUTHORIZED`。
- 用户可创建带完整可选字段的空间，响应不含 `user_id` 与 `deleted_at`。
- 创建后数据库中存在与空间同属当前用户、名称为“默认知识库”的唯一知识库。
- 可选字段规范化：去除首尾空白；空白字符串持久化并响应为 `null`。
- 名称为空白、名称超过 200、可选短字段超过 200 返回 `VALIDATION_ERROR`。
- 空列表返回 `[]`；多个空间按创建时间倒序。
- 当前用户可获取自己的空间详情。
- 用户 A 的列表不含用户 B 的空间；A 请求 B 的空间得到完全固定的 `SPACE_NOT_FOUND` 404。
- 随机不存在 UUID 与已软删除空间同样返回 `SPACE_NOT_FOUND`。
- 以受控数据库写入错误验证原子性：默认知识库创建失败后，空间也不持久化。

最终串行运行 Ruff、格式检查、完整 pytest、pip check、Alembic `command.check()` 与真实 Uvicorn Cookie 会话冒烟验证；pytest 与 Alembic 检查不并行。

## 验收标准

- 登录用户能创建、列出和查看自己的产品空间。
- 每个成功创建的空间恰有一个默认知识库，且空间和知识库的 `user_id` 一致。
- 任意空间查询都通过当前用户 `id` 隔离；用户之间不能枚举对方空间。
- 所有错误使用现有统一中文错误信封。
- 本任务不扩展到更新、删除或任何后续产品能力。
