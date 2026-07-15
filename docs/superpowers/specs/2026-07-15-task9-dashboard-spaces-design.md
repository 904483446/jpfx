# V0.1 Task 9：Dashboard 产品空间列表与创建设计

**日期：** 2026-07-15  
**状态：** 待用户审阅  
**范围：** V0.1 Task 9；仅在已登录的 `/app` 中展示当前用户、列出其产品空间、以弹窗创建空间，并提供创建后的空间详情占位路由。

## 目标与已确认交互

在 Task 8 已完成的 httpOnly Cookie 会话与 `/auth/me` 鉴权之上，实现最小产品空间前端闭环：

1. 用户访问 `/app` 时，先沿用既有 `GET /auth/me` 鉴权流程。
2. 鉴权成功后，Dashboard 显示当前用户昵称和邮箱，并通过 `GET /spaces` 显示该用户的产品空间卡片列表。
3. 用户点击“新建产品空间”打开弹窗；名称必填，行业、产品方向、描述选填。
4. 表单成功调用 `POST /spaces` 后关闭弹窗，并跳转到 `/app/spaces/[spaceId]`。
5. 详情路由在 Task 9 仅显示“产品空间详情将在后续任务实现”的非数据占位内容；不在此路由提前接入文档、知识库、RAG、竞品分析或报告。

采用用户已确认的方案 A：Dashboard 空间卡片列表 + “新建产品空间”弹窗。不会提供编辑、删除、筛选、分页、搜索、排序控制或侧栏真实导航。

## 接口与安全边界

前端只复用既有 API Client，并且只调用已存在的三个产品空间接口中的以下两个：

- `GET /api/v1/spaces`：Dashboard 加载当前用户的空间列表；空列表按 `[]` 渲染。
- `POST /api/v1/spaces`：弹窗提交创建请求，成功时接收返回的 `SpaceResponse` 并使用其 `id` 跳转。

`GET /api/v1/spaces/{space_id}` 已存在，但 Task 9 的详情页为占位页，不发起该请求；该接口留给后续真正的详情功能复用。不会新增、改写或代理后端接口。

所有请求继续由 `apiRequest` 发出，保留 `credentials: "include"`。前端不读取、输出、存储或拼接 Cookie、JWT、密钥、Token 或 `.env` 内容。用户隔离仍由后端从 Cookie 会话识别当前用户并在 spaces 查询中按 `user_id` 过滤；前端不接收或发送 `user_id`。

后端既有统一错误信封会继续由 `ApiClientError` 解析。服务端返回的中文 `message` 可直接显示；网络、配置缺失或非预期错误仅显示已有通用中文错误，不展示原始响应、请求内容或敏感状态。

## 前端结构与职责

在不改变 Task 8 路由结构的前提下，采用如下边界：

| 文件/单元 | 职责 |
| --- | --- |
| `apps/web/lib/spaces.ts` | 定义与后端 `SpaceResponse` 对齐的前端类型、`listSpaces()` 和 `createSpace()`；将 camelCase 表单输入明确映射到 `name`、`industry`、`product_direction`、`description` JSON 字段。 |
| `apps/web/components/app/authenticated-app.tsx` | 保持 Task 8 的 `/auth/me` 加载、401 跳转和非 401 重试边界；仅在当前用户确定后渲染 Dashboard 内容。 |
| `apps/web/components/app/dashboard-spaces.tsx` | 渲染欢迎信息、空间加载/空/错误/成功状态和空间卡片；仅在已鉴权状态下请求列表。 |
| `apps/web/components/app/space-create-dialog.tsx` | 管理受控弹窗、字段校验、提交中状态、错误显示和成功回调；不承担列表查询或路由页面职责。 |
| `apps/web/app/app/page.tsx` | 继续作为 `/app` 的静态路由组合入口，并保留 `AppShell`。 |
| `apps/web/app/app/spaces/[spaceId]/page.tsx` | 新增可访问的详情占位页；只显示路由已进入的确认文案和回到 Dashboard 的入口，不请求空间数据。 |

不新增全局状态库、Server Actions、middleware、前端 API Route、后端改动或第三方弹窗依赖。弹窗使用现有 React、Tailwind 与基础 UI 组件实现，并具备可见标题、关闭操作、`role="dialog"`、`aria-modal` 与合理的焦点/键盘关闭行为。

## Dashboard 状态与用户流程

```text
/app
  -> GET /auth/me
     -> UNAUTHORIZED：replace('/login')
     -> 其他失败：显示“重试”，不跳转
     -> 成功：显示用户信息并 GET /spaces
        -> 加载中：显示非敏感加载状态
        -> []：显示空状态和“新建产品空间”入口
        -> 成功：按 API 返回顺序显示空间卡片
        -> UNAUTHORIZED：跳转 /login
        -> 其他失败：显示中文错误和仅重试列表的入口

“新建产品空间”
  -> 打开弹窗
  -> 前端最小校验名称
  -> POST /spaces
     -> 成功：关闭弹窗，replace('/app/spaces/{id}')
     -> 失败：保留已输入的非敏感字段，显示中文错误，可再次提交
```

每张空间卡片展示 `name`，并仅在字段有值时展示 `industry`、`product_direction` 与 `description` 的简要信息。卡片可进入 `/app/spaces/[spaceId]`。不显示 `user_id`、默认知识库信息、删除状态或任何其他用户数据。

创建成功后直接进入详情占位页，而不是先在列表中乐观插入、重复请求或保留弹窗状态；用户返回 `/app` 后再由正常列表加载获得服务端真实数据。

## 表单规则与错误处理

- `name`：必填。客户端提交前执行 `trim()`；空白值显示“请填写产品空间名称”，不发请求。服务端仍负责 1–200 字符等最终校验。
- `industry`、`productDirection`、`description`：选填。客户端将空白输入规范为 `undefined`/未设置，再映射为后端可接受的可选字段；不增加与后端不一致的长度限制。
- 提交期间禁用“创建产品空间”和取消/关闭会导致重复状态的操作；按钮显示明确提交中状态。
- 用户可通过关闭按钮、遮罩或 Escape 取消弹窗；取消不触发网络请求，重新打开时使用干净表单状态。
- 获取列表或创建时若收到 `UNAUTHORIZED`，只跳转 `/login`；其余错误保留在当前上下文并显示 `ApiClientError.message` 或统一网络错误提示。

## 测试与验收

先新增失败测试，再实现最小代码。测试覆盖：

- `spaces` 请求层准确调用 `GET /spaces` 与 `POST /spaces`，并正确映射 `productDirection -> product_direction`。
- `/app` 在 `/auth/me` 成功后显示用户昵称与邮箱，再加载空间列表；未鉴权时仍仅跳转 `/login`。
- 加载态、空状态、空间卡片及非 401 列表错误的“重试”行为可观察且不会误跳转。
- 卡片链接到对应 `/app/spaces/[spaceId]`。
- 点击“新建产品空间”显示可访问弹窗；名称空白时不调用创建 API；选填字段可以留空。
- 提交中防重复；后端中文错误显示且保留输入；成功创建关闭弹窗并跳转到返回 `id` 对应的详情路由。
- 新增详情占位路由存在，路由检查继续通过。

实现阶段的自动化验证将使用现有前端命令：`npm.cmd run test`、`npm.cmd run check:routes`、`npm.cmd exec tsc -- --noEmit`、`npm.cmd run lint` 与 `npm.cmd run build`。浏览器烟雾验证只在用户已自行配置本地非敏感环境并启动前后端时执行；否则如实记录未验证，不读取 `.env` 补足环境。

## 非目标

- 不改后端 spaces、认证、Cookie、CORS、数据库、迁移或错误模型。
- 不实现空间编辑、删除、软删除、权限管理、默认知识库展示或详情数据加载。
- 不实现文档上传、知识库、RAG、竞品分析、任务、报告、模型配置、退出登录、部署或 V0.2+ 功能。
