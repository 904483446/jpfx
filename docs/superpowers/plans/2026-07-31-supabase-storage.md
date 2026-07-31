# Supabase Storage 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 让生产资料文件存入 Supabase 私有 bucket，同时保持本地目录开发模式。

**Architecture:** `DocumentStorage` 协议统一本地与 Supabase 对象存储。配置完整时注入 `SupabaseDocumentStorage`，否则注入 `LocalDocumentStorage`；资料服务与检索服务不再直接依赖本地 `Path`。

**Tech Stack:** FastAPI、httpx、Pydantic Settings、Supabase Storage HTTP API、pytest、httpx.MockTransport。

---

### Task 1: 定义存储协议与严格配置选择

**Files:**
- Modify: `services/api/app/core/config.py`
- Modify: `services/api/app/services/document_storage.py`
- Create: `services/api/tests/test_document_storage_config.py`
- Modify: `services/api/tests/test_config.py`

- [ ] **Step 1: 写失败测试**

```python
def test_incomplete_supabase_storage_configuration_is_rejected():
    with pytest.raises(ValidationError, match="SUPABASE_URL 与 SUPABASE_SERVICE_ROLE_KEY"):
        Settings(_env_file=None, supabase_url="https://example.supabase.co")

def test_storage_factory_uses_local_storage_without_supabase_configuration(tmp_path):
    settings = Settings(_env_file=None, document_storage_root=tmp_path)
    assert isinstance(create_document_storage(settings), LocalDocumentStorage)
```

- [ ] **Step 2: 运行并确认失败**

Run: `cd services/api; .\.venv\Scripts\python.exe -m pytest tests/test_document_storage_config.py -q`

Expected: FAIL，因配置字段与工厂函数尚不存在。

- [ ] **Step 3: 实现最小协议和配置**

```python
class DocumentStorage(Protocol):
    def save(self, user_id: UUID, space_id: UUID, filename: str, content: bytes) -> StoredDocument: ...
    async def save_upload(self, user_id: UUID, space_id: UUID, filename: str, upload: UploadFile) -> StoredDocument: ...
    def read(self, relative_path: str) -> bytes: ...
    def delete(self, relative_path: str) -> None: ...

def create_document_storage(settings: Settings) -> DocumentStorage:
    if settings.supabase_url is None:
        return LocalDocumentStorage(settings.document_storage_root)
    return SupabaseDocumentStorage(settings.supabase_url, settings.supabase_service_role_key, settings.supabase_storage_bucket)
```

- [ ] **Step 4: 验证并提交**

Run: `cd services/api; .\.venv\Scripts\python.exe -m pytest tests/test_document_storage_config.py tests/test_config.py -q`

Expected: PASS。

```powershell
git add services/api/app/core/config.py services/api/app/services/document_storage.py services/api/tests/test_document_storage_config.py services/api/tests/test_config.py
git commit -m "feat: select document storage from configuration"
```

### Task 2: 实现可测试的 Supabase 私有对象存储

**Files:**
- Modify: `services/api/app/services/document_storage.py`
- Create: `services/api/tests/test_supabase_document_storage.py`
- Modify: `services/api/pyproject.toml`

- [ ] **Step 1: 写失败测试**

```python
def test_supabase_storage_uploads_under_owned_path_and_downloads_bytes():
    transport = MockTransport(handler)
    storage = SupabaseDocumentStorage("https://project.supabase.co", "service-key", "jpfx-documents", transport=transport)
    stored = storage.save(user_id, space_id, "brief.pdf", b"pdf")
    assert stored.relative_path.startswith(f"{user_id}/{space_id}/")
    assert storage.read(stored.relative_path) == b"pdf"
```

- [ ] **Step 2: 运行并确认失败**

Run: `cd services/api; .\.venv\Scripts\python.exe -m pytest tests/test_supabase_document_storage.py -q`

Expected: FAIL，因 `SupabaseDocumentStorage` 尚不存在。

- [ ] **Step 3: 实现最小 HTTP 客户端**

```python
headers = {"Authorization": f"Bearer {service_role_key}", "apikey": service_role_key}
upload_url = f"{base_url}/storage/v1/object/{bucket}/{relative_path}"
download_url = upload_url
```

所有请求设置有限超时；上传使用 `POST`，下载使用 `GET`，删除使用 `DELETE`。非 2xx 响应抛出通用应用错误，消息不含密钥、完整 URL 或响应正文。

- [ ] **Step 4: 覆盖失败与清理路径**

```python
def test_supabase_storage_rejects_invalid_content_before_network_call(): ...
def test_supabase_storage_raises_safe_error_for_non_success_response(): ...
async def test_supabase_storage_streams_upload_and_deletes_partial_object_when_too_large(): ...
```

- [ ] **Step 5: 验证并提交**

Run: `cd services/api; .\.venv\Scripts\python.exe -m pytest tests/test_document_storage.py tests/test_supabase_document_storage.py -q`

Expected: PASS。

```powershell
git add services/api/app/services/document_storage.py services/api/tests/test_supabase_document_storage.py services/api/pyproject.toml
git commit -m "feat: store documents in private Supabase Storage"
```

### Task 3: 接入资料 API、补偿删除与 RAG 索引

**Files:**
- Modify: `services/api/app/api/v1/documents.py`
- Modify: `services/api/app/services/document_service.py`
- Modify: `services/api/app/services/retrieval_service.py`
- Modify: `services/api/tests/test_documents.py`
- Modify: `services/api/tests/test_retrieval_service.py`

- [ ] **Step 1: 写失败测试**

```python
def test_upload_uses_injected_storage_and_deletes_object_when_database_commit_fails(): ...
def test_index_reads_document_bytes_from_injected_storage(): ...
```

- [ ] **Step 2: 运行并确认失败**

Run: `cd services/api; .\.venv\Scripts\python.exe -m pytest tests/test_documents.py tests/test_retrieval_service.py -q`

Expected: FAIL，因 API 和检索服务仍直接构造本地存储或读取 `Path`。

- [ ] **Step 3: 最小接入**

将 `create_document_storage(settings)` 注入上传、删除和索引路径；检索服务从 `storage.read(document.storage_path)` 获得字节。数据库提交失败时保留现有对象删除补偿；删除对象不存在时不阻断资料删除。

- [ ] **Step 4: 验证并提交**

Run: `cd services/api; .\.venv\Scripts\python.exe -m pytest tests/test_documents.py tests/test_retrieval_service.py tests/test_document_storage.py tests/test_supabase_document_storage.py -q`

Expected: PASS。

```powershell
git add services/api/app/api/v1/documents.py services/api/app/services/document_service.py services/api/app/services/retrieval_service.py services/api/tests/test_documents.py services/api/tests/test_retrieval_service.py
git commit -m "feat: route document workflows through storage adapter"
```

### Task 4: 更新非敏感配置说明并进行发布前验证

**Files:**
- Modify: `.env.example`
- Modify: `README.md`
- Create: `docs/superpowers/handoffs/2026-07-31-supabase-storage.md`

- [ ] **Step 1: 写入仅名称级别的配置说明**

```text
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=replace-with-railway-service-variable
SUPABASE_STORAGE_BUCKET=jpfx-documents
```

- [ ] **Step 2: 执行门禁**

```powershell
cd services/api
.\.venv\Scripts\python.exe -m ruff check --no-cache .
.\.venv\Scripts\python.exe -m ruff format --check --no-cache .
.\.venv\Scripts\python.exe -m pytest -q
cd ../../apps/web
npm.cmd test
npm.cmd run check:routes
npx.cmd tsc --noEmit
npm.cmd run lint
npm.cmd run build
```

Expected: 所有本地可运行命令退出码为 0；不把该结果表述为真实 Supabase、Railway 或 Provider 验证。

- [ ] **Step 3: 合并后用户执行线上验收**

1. Supabase Dashboard 创建私有 bucket `jpfx-documents`。
2. Railway Variables 添加 `SUPABASE_URL`、`SUPABASE_SERVICE_ROLE_KEY`、`SUPABASE_STORAGE_BUCKET=jpfx-documents`。
3. Railway 重新部署后上传无敏感 TXT，刷新并再次部署后索引和删除该资料。
4. 记录成功步骤与 HTTP 状态，不记录任何真实变量值。

- [ ] **Step 4: 提交**

```powershell
git add .env.example README.md docs/superpowers/handoffs/2026-07-31-supabase-storage.md
git commit -m "docs: document Supabase Storage deployment"
```
