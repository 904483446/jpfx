# 证据质量门交接

## 交付内容

- 在报告模型调用前校验任务证据：至少一条证据、证据类型受支持、标题非空；网页证据必须为带主机名的 `http` 或 `https` URL；私有知识库证据必须同时关联知识库、文档和分块。
- 校验不通过时以 `EVIDENCE_QUALITY_FAILED` 终止任务，不调用模型，也不创建报告。
- 校验通过后，将计数摘要写入报告 `structured_json.quality_check`。
- 前端将后端 `quality_checking` 阶段显示为“证据质量检查”，置于“模型调用”之前。

## 提交

- `a317ebf docs: define evidence quality gate`
- `80cd450 feat: validate report evidence quality`
- `070f32c feat: gate reports on traceable evidence`
- `f8583af feat: show evidence quality stage`

## 验证记录（2026-07-29）

在本工作树执行，均以退出码 0 完成：

| 区域 | 命令 | 结果 |
| --- | --- | --- |
| 后端 | `python -m ruff check --no-cache .` | 通过 |
| 后端 | `python -m ruff format --check --no-cache .` | 101 个文件已格式化 |
| 后端 | `python -m pytest -q` | 190 passed（20.17s） |
| 前端 | `npm.cmd test` | 29 个测试文件、110 项测试通过 |
| 前端 | `npm.cmd run check:routes` | `STATIC_ROUTE_FILES=ok` |
| 前端 | `npx.cmd tsc --noEmit` | 通过 |
| 前端 | `npm.cmd run lint` | 通过 |
| 前端 | `npm.cmd run build` | Next.js 生产构建通过 |

前端新增阶段测试曾先以预期方式失败：页面原本展示原始值 `quality_checking`，并缺少“证据质量检查”时间线节点；最小 UI 映射后定向测试为 8/8 通过。

## 未验证边界

- 未调用真实 DeepSeek Provider。
- 未执行浏览器端的新报告完整流程，也未验证真实浏览器、跨域和会话行为。
- 未部署到任何环境，未运行 CI。
- 本次没有数据库迁移。
- 本工作树的 `.env` 由用户手动提供用于本地验证；未读取、复制、输出或提交。
