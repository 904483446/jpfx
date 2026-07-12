# Task 7：前端 Next.js 骨架设计

**日期：** 2026-07-12  
**状态：** 已完成
**范围：** V0.1 Task 7，仅创建可运行、可浏览的 Next.js 前端骨架。

## 1. 目标

在 `apps/web` 建立正式的 Next.js App Router 项目，使用 TypeScript、Tailwind CSS 与 shadcn/ui，提供以下静态页面：

- `/`：公开产品介绍首页。
- `/login`：登录页面。
- `/register`：注册页面。
- `/app`：应用壳占位页。

该骨架应复用统一的视觉语言，并为 Task 8 的认证联调和 Task 9 的空间工作台留下明确的组件与路由边界。

## 2. 已确认的产品与视觉决策

- 整体风格采用已确认的 B2B SaaS 工作台方向：深海军蓝为主色、明亮蓝为主要操作色、白色与浅灰为内容背景，辅以克制的青绿色强调色。
- 首页突出“把竞品洞察变成可验证的决策”，只描述产品价值与“整理资料、分析竞品、输出报告”三步流程，不展示技术栈。
- 首页导航含“产品介绍、登录、注册”；主按钮为“登录”，次按钮为“注册”。
- `/login` 与 `/register` 使用同一认证页面结构。登录页提供“还未注册？立即注册”静态跳转；注册页提供“已有账号？立即登录”静态跳转。
- `/app` 使用左侧深色导航与内容区的应用壳。其内容只显示静态占位，明确标注后续由 Task 8 接入当前用户、Task 9 展示空间；不展示真实空间、新建空间或数据列表。

## 3. 页面与导航边界

### 3.1 静态页面跳转

Task 7 的链接只做客户端页面导航：

| 来源 | 目标 |
| --- | --- |
| 首页“登录”及导航登录 | `/login` |
| 首页“注册”及导航注册 | `/register` |
| 登录页“立即注册” | `/register` |
| 注册页“立即登录” | `/login` |

`/app` 可以直接访问，仅用于检验应用布局。它不在本任务中读取 Cookie、请求 `/api/v1/auth/me` 或执行未登录跳转。

### 3.2 明确不做

Task 7 不实现以下行为：

- 登录或注册表单提交、前端校验、错误提示与后端认证请求。
- Cookie 读取、当前用户查询、路由守卫或退出登录。
- 产品空间列表、创建空间、知识库、文档、RAG、Agent、报告或设置业务功能。
- 真实 API 数据渲染、状态管理库、服务端代理或部署配置。

## 4. 技术与文件设计

### 4.1 项目基础

- 在 `apps/web` 使用 Next.js App Router、React、TypeScript、Tailwind CSS。
- 使用 npm（Windows 命令为 `npm.cmd`）。
- 配置 shadcn/ui，并实际复用其 `Button` 与 `Input` 组件；页面布局和专有展示组件使用 Tailwind 编写。
- 使用本机无衬线字体栈，不依赖 `next/font` 或外部字体下载，保证离线构建可用。

### 4.2 建议模块边界

- `app/layout.tsx`：根布局、全局字体和元数据。
- `app/page.tsx`：公开首页，组合导航、主视觉与三步流程卡片。
- `app/login/page.tsx`、`app/register/page.tsx`：复用认证页外壳，只渲染静态输入框与跳转链接。
- `app/app/page.tsx`：组合应用顶栏、侧栏和静态空状态。
- `components/brand-mark.tsx`：统一产品名称与标记。
- `components/auth/auth-shell.tsx`：登录、注册共用外壳，接收标题、说明、底部跳转内容与表单子元素。
- `components/app-shell.tsx`：只负责应用导航与内容容器，不包含鉴权或数据读取。
- `components/landing/steps.tsx`：首页三步流程展示。
- `components/ui/*`：由 shadcn/ui 生成的基础组件。
- `lib/api-client.ts`：集中读取 API 基地址、构造请求 URL、默认设置 `credentials: "include"`，并将后端 `{error:{code,message,details}}` 解析为可复用的 `ApiClientError`。本任务不导出具体的认证或空间 API 调用函数。

### 4.3 环境变量

前端 API 基地址只从 `NEXT_PUBLIC_API_BASE_URL` 读取。开发示例使用 `http://127.0.0.1:8000/api/v1`，但真实 `.env.local` 不提交。应提供前端环境变量示例，并确保 `.env.local` 被 Git 忽略。

## 5. 错误处理与安全边界

- API Client 缺少 `NEXT_PUBLIC_API_BASE_URL` 时抛出明确的配置错误，不静默改用生产地址。
- Client 请求默认带 `credentials: "include"`，以便 Task 8 使用后端 httpOnly Cookie；前端不读取、存储或打印 Cookie/JWT。
- API 错误消息遵从后端中文错误结构；无法解析的响应使用通用中文网络错误，不泄露响应正文。
- 本任务的静态表单不收集、提交或记录密码。

## 6. 验证与验收

实施采用先验证再完善的最小循环：先创建可失败的配置/模块检查，再补齐实现并运行验证。

必需验证：

1. `npm.cmd run lint` 通过。
2. `npm.cmd run build` 通过。
3. 使用本地开发服务器实际访问 `/`、`/login`、`/register`、`/app`。
4. 检查首页、登录页与注册页的静态链接目标正确。
5. 检查 `/app` 只呈现应用壳和静态占位，不发起认证或空间 API 请求。
6. 检查 API Client 对基地址配置、Cookie 请求选项和后端中文错误响应的纯函数行为。

## 7. 完成标准

- `apps/web` 可在 Windows 上通过 `npm.cmd` 安装依赖、启动、lint 和 build。
- 四个既定路径均可访问，视觉方向与已确认预览一致。
- 静态跳转正确，且没有任何真实认证或空间业务行为。
- API Client 和环境变量边界可供 Task 8、Task 9 直接复用。
- README 在 Task 7 实现完成后更新为下一步 Task 8；设计阶段不提前修改 README。
