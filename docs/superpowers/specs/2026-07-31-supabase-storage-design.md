# Supabase Storage 私有资料存储设计

## 目标

将生产环境的资料文件从 Railway 临时文件系统迁移到 Supabase 的私有 Storage bucket `jpfx-documents`，使上传的 PDF、DOCX、TXT、Markdown 在 Railway 重新部署后仍可用于列表、删除和 RAG 索引。

## 范围与边界

- 保留本地开发现有的 `LocalDocumentStorage` 行为，不迁移或读取已有本地文件。
- 生产环境通过 Railway 环境变量启用 Supabase Storage；真实 URL、Service Role Key、数据库 URI 和 Provider Key 不进入仓库、测试输出或文档示例。
- 不启用 Supabase Data API，不公开 bucket，不让浏览器直接访问 Supabase Storage。
- 不修改 PostgreSQL/Alembic 模型、资料 API URL、数据库中的 `storage_path` 语义或用户/空间授权规则。
- 不在本阶段验证真实 DashScope、Bocha、DeepSeek 调用。

## 架构

新增一个最小的对象存储协议，包含保存字节、异步保存上传流、读取字节和删除对象四项能力。`LocalDocumentStorage` 与新增的 `SupabaseDocumentStorage` 都实现该协议；资料服务和检索服务依赖协议而不是本地 `Path`。

应用启动时根据 `SUPABASE_URL` 与 `SUPABASE_SERVICE_ROLE_KEY` 是否同时存在选择存储实现：两者均存在时使用 Supabase，否则使用本地存储。两者只存在一个时启动失败并给出中文配置错误，防止生产环境静默写回 Railway 临时磁盘。

对象名继续使用 `user_id/space_id/随机 UUID.扩展名`。该值仍保存到现有 `documents.storage_path`；后端的所有读取、删除和索引操作继续以当前用户与空间授权为入口，因此 bucket 内对象路径不会作为外部可控访问凭据。

## Supabase Storage 交互

- bucket 固定为私有的 `jpfx-documents`，由用户在 Supabase Dashboard 创建。
- Railway 后端使用 `SUPABASE_SERVICE_ROLE_KEY` 调用 Supabase Storage HTTP API；该 Key 只保存在 Railway Variables，绝不发送给前端。
- 上传使用对象路径写入 bucket；已写入但数据库事务失败时删除对象，保持现有补偿语义。
- 索引前下载对象字节，再复用现有 PDF/DOCX/TXT/MD 解析、切分和 pgvector 写入逻辑。
- 删除资料时先删除对象，再删除数据库记录；对象不存在时仍保持删除接口幂等。
- HTTP 客户端必须设定超时，并把 Supabase 非成功响应转换为安全的应用错误，不回显 Key、完整 URL 或响应正文。

## 配置

新增仅服务端读取的环境变量：

```text
SUPABASE_URL=https://PROJECT_REF.supabase.co
SUPABASE_SERVICE_ROLE_KEY=service-role-secret
SUPABASE_STORAGE_BUCKET=jpfx-documents
```

`SUPABASE_STORAGE_BUCKET` 默认值为 `jpfx-documents`。`SUPABASE_URL` 与 `SUPABASE_SERVICE_ROLE_KEY` 必须同时配置或同时缺失。`.env.example` 只列出变量名称和替代值，不包含真实 Project Ref、密钥或数据库密码。

## 测试与验收

- 先为存储选择和不完整配置写失败测试。
- 使用 `httpx.MockTransport` 测试 Supabase 上传、下载、删除、非 2xx 错误及对象路径；不调用真实 Supabase。
- 保留并复跑本地存储测试，确保本地开发没有行为回归。
- 复跑后端 Pytest/Ruff 与前端现有质量门禁；本机 Docker 不可用时明确记录为未验证。
- 合并并部署后，由用户创建私有 bucket，在 Railway 设置三项变量，上传无敏感 TXT，刷新和重新部署后验证文件仍可索引和删除。

## 风险控制

- Service Role Key 权限很高：只放 Railway 服务变量，前端变量和日志中不出现该 Key。
- Supabase bucket 必须保持私有；不创建公开下载 URL。
- 旧 Railway 临时文件不会自动迁移，因为其在当前运行环境中不可靠；线上首次部署前没有可迁移的正式资料。
- 文件持久化验证与模型 Provider 验证是两条独立验收线，不能相互替代。
