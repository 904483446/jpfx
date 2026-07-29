# 本地真实集成验证设计

## 目标

在不读取、复制或修改真实 `.env`、Cookie、Token、密钥的前提下，验证当前 `main`
能否在本机完成 Docker PostgreSQL + pgvector、Alembic、FastAPI 以及浏览器 Cookie/CORS
会话的最小闭环，并将每项结论区分为“通过”“失败”或“未运行”。

## 范围与非目标

本轮只使用现有 Docker Compose、后端代码和前端代码；不修改业务代码、依赖、迁移或
环境文件，不执行 `docker compose down -v`、数据库清空、回滚迁移或其他破坏性操作。

不配置或调用 DashScope、DeepSeek、Bocha 等外部 Provider；不创建演示数据、不上传资料，
也不把浏览器自动化结果夸大为部署或 Provider 验证。

## 验证流程

### 1. Docker 与数据库

先读取 Docker daemon、`docker compose ps` 与 `db` health 状态。只有在 `db` 未运行时，
才执行仓库既有的 `docker compose up -d --wait db`；若 daemon 不可用或凭据被操作系统
拒绝，记录为环境阻塞，不修改项目代码。

不打印容器环境变量、数据库连接串或 `.env` 内容。验证只使用容器健康状态和后续
Alembic 命令的退出码。

### 2. Alembic 与 API

在 `services/api` 使用既有虚拟环境执行：

```powershell
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m alembic current
```

随后仅在 FastAPI 已运行或可由既有命令启动时，访问
`http://127.0.0.1:8000/api/v1/health`。迁移命令只允许向当前 head 升级，不允许
downgrade；健康端点只确认服务可达，不读取业务数据。

### 3. 浏览器 Cookie/CORS 与退出闭环

使用普通本地 Chrome 的既有会话，而非读取浏览器存储。验证顺序为：

1. 打开 `/app`，确认已登录应用壳和凭据携带 API 请求没有网络/CORS 错误。
2. 检查 `/app/spaces` 和 `/app/tasks` 的真实受保护空态或数据态，不读取或截图敏感内容。
3. 点击产品的退出登录控制；确认浏览器到达 `/login`。
4. 在同一浏览器直接打开 `/app`；确认被重定向或拒绝并回到 `/login`。

若没有既有登录会话，暂停浏览器步骤并仅请用户在本机手动登录；不索取邮箱、密码或
任何 Cookie。若 Chrome 自动化本身无法连接本地 API，则记录为自动化环境限制，并以
普通本地 Chrome 的可见结果为准。

## 结果与修复边界

输出会逐项列出命令、退出码或可见浏览器状态。若发现项目缺陷，只报告复现证据、根因
假设和最小修复设计；在用户明确批准前不改代码。若所有项目通过，只新增一份结果记录，
不声称部署、CI 或真实外部 Provider 已验证。
