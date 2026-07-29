# 本地真实集成验证记录

基线：`main` 合并提交 `4fe5c1a`；验证在 2026-07-29 的本机环境完成。全程未读取、复制、提交或修改 `.env`、Cookie、Token、密码或 Provider 密钥。

## Docker 与数据库

| 检查 | 命令或状态 | 结果 |
| --- | --- | --- |
| Docker daemon | `docker version --format "{{.Server.Version}}"` | Docker Server `29.3.1`，退出码 0。 |
| Compose 数据库 | `docker compose ps` | `jpfx-db-1`（`db`）已运行且 `healthy`，监听本机 5432。 |
| 服务启动 | 未执行 | `db` 已健康；未执行 `docker compose up`、`down`、`down -v`、`rm` 或 `prune`。 |

## Alembic 与 API

| 检查 | 命令或状态 | 结果 |
| --- | --- | --- |
| 迁移升级 | `services/api/.venv/Scripts/python.exe -m alembic upgrade head` | 退出码 0。 |
| 当前 revision | `services/api/.venv/Scripts/python.exe -m alembic current` | `20260716_0004 (head)`。 |
| FastAPI 健康端点 | `GET http://127.0.0.1:8000/api/v1/health` | HTTP 200，响应 `{"status":"ok"}`。 |

验证时后端尚未运行，随后按 README 的既有 uvicorn 命令启动到 `127.0.0.1:8000`；未执行 downgrade，也未输出数据库连接信息。

## 浏览器 Cookie/CORS 与退出

| 步骤 | 可见结果 |
| --- | --- |
| 已登录工作台 | `/app` 进入已认证应用壳。 |
| 产品空间 | `/app/spaces` 成功完成加载并显示真实的无空间空态。 |
| 分析任务 | `/app/tasks` 成功完成加载并显示“尚无可展示队列”。 |
| 浏览器错误 | 上述受保护页面的浏览器控制台未见 error；未观察到 CORS 或网络错误。 |
| 退出登录 | 点击产品 UI 的“退出登录”后，地址到达 `/login` 并显示登录表单。 |
| 退出后拦截 | 同一浏览器直接访问 `/app` 后，完成认证检查并重定向到 `/login`。 |

为完成退出验收，浏览器会话被主动退出；未读取、导出或手动删除浏览器 Cookie。

## 未验证边界

- 未调用 DashScope、DeepSeek、Bocha 或其他真实外部 Provider。
- 未上传资料、创建产品空间、创建分析任务或生成报告。
- 未验证生产部署、公开 Demo、CI 或视觉适配。
- 本次仅验证现有 Docker、PostgreSQL/pgvector、Alembic、FastAPI 和本地浏览器会话闭环；不等同于生产环境验收。

## 结论与后续

本地 Docker/Alembic/API 与浏览器 Cookie/CORS/退出登录闭环均通过，未发现需要代码修复的问题。前端与后端开发服务为本次验证启动，仍在本机 `127.0.0.1:3000` 和 `127.0.0.1:8000` 运行；如无需继续本地调试，可由用户自行停止。
