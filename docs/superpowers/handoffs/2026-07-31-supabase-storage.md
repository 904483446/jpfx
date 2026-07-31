# Supabase Storage 交接

## 已完成的文档边界

- `.env.example` 只提供变量名和占位值：`SUPABASE_URL`、`SUPABASE_SERVICE_ROLE_KEY`、`SUPABASE_STORAGE_BUCKET`。
- 生产存储使用 Supabase 私有 bucket `jpfx-documents`；服务角色密钥仅允许配置在 Railway Variables，不得提交、返回给前端、写入日志或文档。
- 未配置上述 Supabase 变量时，本地开发继续使用本地资料目录。

## 本地验证状态

- 已完成离线、无需真实 Supabase 凭据的定向存储测试。
- 完整 `pytest` 尚未验证：当前 worktree 的 `TEST_DATABASE_URL` 未经确认，因此不能把完整测试结果表述为已通过。
- Docker、真实 Supabase 和 Railway 均未验证。

## 合并后的线上验收（用户执行）

1. 在 Supabase Dashboard 创建私有（非 public）bucket：`jpfx-documents`。
2. 在 Railway Variables 配置 `SUPABASE_URL`、`SUPABASE_SERVICE_ROLE_KEY` 和 `SUPABASE_STORAGE_BUCKET=jpfx-documents`；只填写真实值，不在仓库、日志或交接记录中保存它们。
3. 重新部署 Railway 服务。
4. 上传一个不含敏感信息的 TXT 文件，刷新页面确认资料状态与列表可见。
5. 再次重新部署 Railway 服务后，执行该资料的索引并删除，确认对象和资料记录均可正常处理。
6. 记录每一步的成功/失败和 HTTP 状态，不记录任何真实变量值、密钥、Cookie 或 Token。

## 未覆盖范围

- 本次没有进行真实 Supabase API 调用、Railway 发布或 Docker 验证。
- 本地离线测试不能证明生产 bucket 权限、Railway 变量注入或跨重部署的上传、索引、删除流程。
