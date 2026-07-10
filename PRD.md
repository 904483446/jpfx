# PRD：AI 产品经理竞品分析平台

## 1. 项目概述

### 项目名称

AI Competitor Intelligence Workspace

中文暂定名：竞品智研台

### 项目定位

面向国内 AI 产品经理的竞品分析工作台。

本项目不是普通竞品分析工具，而是结合以下能力的正式前后端产品：

- 用户私有知识库 RAG
- 国内公开竞品情报搜索与资料抓取
- 多 Agent 分析工作流
- 中文结构化竞品分析报告
- 历史报告沉淀与复用

### 目标用户

- AI 产品经理
- 正在转型 AI PM 的学习者
- 创业团队产品负责人
- 需要做赛道研究和竞品拆解的个人开发者
- 希望用 GitHub 项目展示 AI 产品能力的求职者

### 核心价值

帮助用户把公司资料、产品文档、市场资料、竞品网页资料整合起来，生成适合 AI 产品经理使用的结构化竞品分析报告。

核心价值包括：

- 降低竞品资料收集成本
- 让内部资料参与竞品分析
- 让竞品报告有来源、有证据、有不确定性提示
- 沉淀历史报告，形成长期知识资产
- 展示 RAG、Agent、多模型接入、用户数据隔离等 AI 应用能力

### 典型使用场景

示例场景选择“企业知识库 Copilot”。

1. 用户准备研究“企业知识库 Copilot”赛道。
2. 用户注册登录后创建一个产品空间：企业知识库 Copilot。
3. 用户上传公司已有产品文档、市场调研资料、竞品资料。
4. 系统解析文档并建立私有知识库。
5. 用户发起竞品分析任务，输入行业、产品方向、关键词，也可以输入已知竞品。
6. 系统基于用户输入补充候选竞品，并用国内搜索服务验证。
7. 系统结合公开资料和私有知识库生成中文竞品分析报告。
8. 用户在线查看报告，后续版本支持导出 PDF 和 Word。

## 2. 项目目标

### 业务目标

构建一个真实可用的 AI PM 竞品分析平台，而不是一次性 Demo。

第一阶段目标是完成一个可以在 GitHub 展示、可以本地运行、可以部署公开 Demo、可以让其他用户试用的 MVP。

### 产品目标

MVP 需要形成完整闭环：

- 用户注册登录
- 创建产品空间
- 上传私有资料
- 文档解析与知识库索引
- RAG 检索
- 新建竞品分析任务
- 半自动补充竞品
- 多 Agent 分析
- 生成中文结构化报告
- 查看历史报告

### 技术目标

- 使用正式前后端架构
- 支持用户数据隔离
- 支持用户自带大模型 API Key
- 默认推荐 DeepSeek
- 支持 OpenAI-compatible 模型接口
- 使用 PostgreSQL + pgvector 存储业务数据和向量数据
- 使用 Supabase 数据库与文件存储
- 使用独立 FastAPI 后端，避免 Serverless 长任务限制
- 代码结构适合 GitHub 开源展示

### GitHub 开源展示目标

README 需要清楚展示：

- 项目背景
- 核心功能
- 技术架构
- RAG 流程
- 多 Agent 工作流
- 本地启动方式
- 环境变量配置
- 页面截图
- 示例报告
- Roadmap

## 3. MVP 范围

### MVP 必须实现

#### 用户系统

- 用户注册
- 用户登录
- 用户退出
- 当前用户信息
- 登录态保护

#### 产品空间

- 用户可以创建产品空间
- 每个产品空间对应一个产品方向或分析项目
- 每个空间默认拥有一个知识库
- 空间内包含文档、分析任务和报告

#### 私有知识库

- 用户可以在产品空间内上传文档
- 支持 PDF、DOCX、TXT、Markdown
- 系统保存文档记录
- 系统显示文档处理状态

#### 文档处理

- 文档解析
- 文本清洗
- 文本切分
- 生成 embedding
- 写入向量索引
- 记录处理失败原因

#### RAG 检索

- 基于用户私有知识库进行检索
- 检索必须限制在当前用户和当前产品空间内
- 返回引用片段、来源文档和相似度

#### 竞品分析任务

- 用户输入行业、产品方向、关键词
- 用户可以输入 0-3 个已知竞品
- 默认采用半自动补充竞品模式
- 如果用户不知道竞品，可以跳过竞品输入，由系统自动发现
- 每个任务最多分析 3 个竞品
- 任务有状态：待运行、运行中、完成、失败

#### 多 Agent 分析流程

MVP 使用固定流水线，不做完全自治 Agent。

包含：

- 需求理解 Agent
- 私有知识库检索 Agent
- 公开资料收集 Agent
- 竞品分析 Agent
- 产品策略建议 Agent
- 报告生成 Agent
- 质量检查 Agent

#### 报告生成

报告默认使用中文。

报告至少包含：

- 竞品定位
- 核心功能
- 目标用户
- 商业模式
- AI 能力
- 产品优劣势
- 差异化机会
- 可落地产品建议
- 风险与不确定性
- 信息来源

#### 历史报告

- 查看历史报告列表
- 查看报告详情
- 按产品空间筛选报告
- 报告和任务关联

#### 模型设置

- 用户可以配置自己的 DeepSeek API Key
- 默认 Provider 为 DeepSeek
- 默认模型为 `deepseek-chat`
- 同时兼容 OpenAI-compatible 接口
- API Key 加密保存
- 前端只展示脱敏信息

## 4. 非 MVP / 暂不实现范围

第一阶段不做：

- 团队协作
- 组织空间
- 成员邀请
- 复杂 RBAC 权限系统
- 付费系统
- 用量计费
- 浏览器插件
- 实时协同编辑
- 企业级审计日志
- 大规模爬虫平台
- 自动定时监控竞品
- 移动端 App
- 管理员后台
- 多知识库组合检索
- 报告模板市场
- 强保证生成内容准确性

## 5. 用户角色与权限

### 未登录用户

可以：

- 访问公开首页
- 访问登录页
- 访问注册页

不能：

- 创建产品空间
- 上传文档
- 发起分析任务
- 查看报告
- 配置模型 API Key

### 已登录用户

可以：

- 创建和管理自己的产品空间
- 上传自己的知识库文档
- 配置自己的模型 API Key
- 发起竞品分析任务
- 查看自己的任务进度
- 查看自己的历史报告
- 导出自己的报告

不能：

- 访问其他用户的数据
- 查看其他用户的文档
- 使用其他用户的模型配置
- 查看其他用户的报告

### 管理员

MVP 暂不实现管理员后台。

数据库可以预留 `is_admin` 字段，但第一阶段不提供管理员页面和管理员功能。

## 6. 核心用户流程

### 注册 / 登录流程

1. 用户访问注册页。
2. 输入邮箱、昵称、密码。
3. 系统校验邮箱是否重复。
4. 系统哈希保存密码。
5. 注册成功后跳转登录或自动登录。
6. 登录成功后进入 Dashboard。

### 上传知识库文档流程

1. 用户进入某个产品空间。
2. 打开知识库管理页。
3. 上传 PDF、DOCX、TXT 或 Markdown 文件。
4. 系统检查文件类型和大小。
5. 系统保存原始文件。
6. 系统创建文档记录，状态为处理中。
7. 系统解析文档文本。
8. 系统切分文本 chunk。
9. 系统调用 embedding 模型生成向量。
10. 系统写入 `document_chunks`。
11. 文档状态更新为已索引。
12. 如果失败，记录失败原因并展示给用户。

### 创建竞品分析任务流程

1. 用户进入产品空间。
2. 点击新建竞品分析任务。
3. 输入行业、产品方向、关键词。
4. 可选输入已知竞品；如果不知道竞品，可以跳过。
5. 系统检查用户是否已配置 DeepSeek API Key。
6. 系统创建分析任务。
7. LLM 补充候选竞品。
8. Search Provider 验证候选竞品和公开资料来源。
9. 系统启动多 Agent 工作流。
10. 用户进入任务进度页查看执行状态。

### 查看报告流程

1. 分析任务完成。
2. 系统生成报告。
3. 用户进入报告详情页。
4. 查看报告正文、结构化摘要、证据来源和风险提示。
5. 后续版本支持导出 PDF / Word。

### 查看历史记录流程

1. 用户进入历史报告页。
2. 系统展示当前用户的报告列表。
3. 用户按产品空间、关键词、时间筛选。
4. 用户点击报告进入详情页。

## 7. 功能需求

### 7.1 用户系统

功能说明：提供基础账号体系和登录态管理。

输入：

- 邮箱
- 昵称
- 密码

输出：

- 用户信息
- 登录状态
- 会话 Cookie 或 JWT

关键规则：

- 密码必须哈希保存
- API 返回不包含 `password_hash`
- 未登录用户不能访问业务接口
- 错误提示使用中文

异常情况：

- 邮箱已注册
- 密码错误
- 用户不存在
- 会话过期
- 未授权访问

### 7.2 产品空间模块

功能说明：用户可以创建多个产品空间。每个空间代表一个产品方向、赛道或竞品分析项目。

输入：

- 空间名称
- 行业
- 产品方向
- 描述

输出：

- 产品空间列表
- 产品空间详情

关键规则：

- 每个空间必须属于一个用户
- 空间名称不能为空
- MVP 中每个空间默认只有一个知识库
- 删除空间时优先软删除

异常情况：

- 空间不存在
- 无权限访问
- 名称为空
- 重复提交

### 7.3 知识库模块

功能说明：管理产品空间内的私有资料集合。

输入：

- 产品空间 ID
- 知识库名称
- 描述

输出：

- 知识库详情
- 文档数量
- 索引状态汇总

关键规则：

- MVP 每个产品空间默认一个知识库
- 知识库不能跨用户访问
- 知识库用于 RAG 检索

异常情况：

- 知识库不存在
- 无权限访问
- 关联空间不存在

### 7.4 文档处理模块

功能说明：上传、解析、切分和索引用户文档。

输入：

- PDF
- DOCX
- TXT
- Markdown

输出：

- 文档记录
- 文档状态
- chunk 记录
- 索引结果

关键规则：

- 单文件默认最大 20MB
- MVP 每个用户最多 100 个文档
- 支持格式：PDF、DOCX、TXT、MD
- 不支持扫描版 PDF OCR
- 文档处理失败必须记录错误信息

异常情况：

- 文件过大
- 文件格式不支持
- 文本为空
- 解析失败
- embedding 服务失败
- 数据库写入失败

### 7.5 RAG 检索模块

功能说明：从当前用户当前产品空间的私有知识库中检索相关资料。

输入：

- 查询文本
- `user_id`
- `space_id`
- `top_k`

输出：

- chunk 内容
- 来源文档
- 相似度
- chunk metadata

关键规则：

- 必须按 `user_id` 过滤
- 必须按 `space_id` 过滤
- 默认 `top_k` 为 8
- 报告中引用的私有资料必须能追溯到文档和 chunk

异常情况：

- 当前空间没有文档
- 文档尚未完成索引
- 没有相关结果
- embedding 调用失败

### 7.6 竞品分析任务模块

功能说明：创建和管理竞品分析任务。

输入：

- 产品空间 ID
- 行业
- 产品方向
- 关键词
- 已知竞品
- 是否自动补充竞品

输出：

- 任务 ID
- 任务状态
- Agent 运行进度
- 报告 ID

关键规则：

- 用户必须登录
- 用户必须配置 DeepSeek API Key
- 每个任务最多分析 3 个竞品
- 默认使用半自动补充竞品模式
- 如果用户不输入竞品，系统可以全自动发现候选竞品
- 自动补充的竞品必须通过公开搜索结果验证
- 任务失败需要显示失败原因

异常情况：

- 未配置模型 API Key
- 竞品数量超过限制
- 搜索服务失败
- 模型服务失败
- 任务超时

### 7.7 多 Agent 分析模块

功能说明：通过多个角色明确的 Agent 完成竞品分析。

输入：

- 分析任务
- 用户知识库检索结果
- 公开资料
- 模型配置

输出：

- Agent 运行记录
- 中间分析结果
- 最终报告

关键规则：

- MVP 使用固定工作流
- 每个 Agent 的输入输出都要记录
- Agent 失败不能静默吞掉
- 报告生成前必须经过质量检查

异常情况：

- Agent 输出格式错误
- 上游结果为空
- 模型返回超时
- 质量检查不通过

### 7.8 公开资料搜索与抓取模块

功能说明：为竞品分析收集公开资料。

输入：

- 行业
- 产品方向
- 关键词
- 已知竞品
- LLM 补充候选竞品

输出：

- 已验证竞品列表
- 搜索结果
- 网页正文或网页摘要
- 来源 URL

关键规则：

- 第一版默认搜索服务为博查 AI Search API
- 百度千帆百度搜索 API 作为备选
- 抓取优先使用后端网页正文解析
- 网页抓取失败时使用搜索摘要兜底
- 第一阶段不做大规模爬虫平台

异常情况：

- 搜索无结果
- 候选竞品无法验证
- 网页无法访问
- 网页正文解析失败

### 7.9 报告生成模块

功能说明：生成中文结构化竞品分析报告。

输入：

- 竞品公开资料
- 私有知识库引用
- Agent 分析结果

输出：

- Markdown 报告
- 结构化 JSON
- 证据来源
- 置信度或风险提示

关键规则：

- 报告默认中文
- 必须区分事实、引用和推断
- 必须展示信息来源
- 不确定内容必须标注不确定性
- 报告字段必须完整

异常情况：

- 模型输出不完整
- JSON 解析失败
- 缺少核心字段
- 证据不足

### 7.10 历史报告模块

功能说明：保存和管理历史竞品分析报告。

输入：

- 产品空间 ID
- 报告 ID
- 筛选条件

输出：

- 报告列表
- 报告详情
- 证据列表

关键规则：

- 用户只能查看自己的报告
- 报告和任务关联
- 删除报告不删除原始文档
- 报告详情保留生成时间和任务输入

异常情况：

- 报告不存在
- 无权限访问
- 导出失败

### 7.11 系统设置模块

功能说明：用户配置模型 Provider 和 API Key。

输入：

- Provider 名称
- Base URL
- 默认模型名
- API Key

输出：

- 模型配置状态
- 脱敏后的 Key 信息

关键规则：

- 优先支持 DeepSeek
- 默认模型为 `deepseek-chat`
- 同时支持 OpenAI-compatible 接口
- API Key 必须加密保存
- 前端不能显示明文 Key
- 代码仓库不能包含真实 Key

异常情况：

- API Key 为空
- Base URL 无效
- 模型调用失败
- 加密密钥缺失

## 8. 推荐技术栈

### 前端

推荐：Next.js + React + TypeScript + Tailwind CSS + shadcn/ui

选择原因：

- 适合正式前端项目
- 页面路由和布局管理清晰
- 适合部署到 Vercel
- TypeScript 有利于维护接口类型
- shadcn/ui 适合构建 SaaS 工作台
- GitHub 展示效果比 Streamlit 更专业

不优先选择纯 React/Vite 的原因：

- Vite 更轻，但认证、路由、部署和应用结构需要自行组合
- 对这个项目的正式前后端作品集目标来说，Next.js 更合适

### 后端

推荐：FastAPI + Pydantic + SQLAlchemy + Alembic

选择原因：

- Python 更适合 RAG、LLM、Agent 和文档解析
- FastAPI 自动生成接口文档
- Pydantic 适合定义请求和响应 Schema
- SQLAlchemy 适合正式数据库建模
- Alembic 适合管理数据库迁移

不优先选择 Node.js 的原因：

- Node.js 可以做，但文档解析、RAG 和 Agent 编排相关 Python 生态更成熟
- 学习和开源展示时，FastAPI + AI 应用更直观

### 数据库

推荐：Supabase PostgreSQL

选择原因：

- 适合用户、空间、文档、任务、报告等结构化数据
- 可通过 Supabase 快速部署
- 后续扩展能力强

### 向量数据库

推荐：pgvector

选择原因：

- 直接使用 PostgreSQL 存储向量
- 减少额外服务
- Supabase 支持 pgvector
- MVP 运维成本低

不优先选择 Chroma 的原因：

- Chroma 更适合本地 Demo
- 正式多用户系统中持久化、权限和部署需要额外设计

不优先选择 Qdrant 的原因：

- Qdrant 更专业，但第一版会增加一个独立服务
- 对初学者和 GitHub 展示来说复杂度偏高

### 鉴权

推荐：FastAPI 自建鉴权 + JWT/httpOnly Cookie

选择原因：

- 学习价值更高
- 用户数据隔离逻辑更清楚
- 与独立 FastAPI 后端职责一致
- 避免把核心用户系统完全交给第三方

### LLM

推荐：DeepSeek 优先 + OpenAI-compatible Provider 抽象

选择原因：

- DeepSeek 更适合国内用户
- 用户自行配置自己的 API Key
- 兼容接口可以覆盖 OpenAI、Kimi、通义、智谱等模型
- 后续切换模型不需要重写业务逻辑

### Embedding

推荐：通义 DashScope `text-embedding-v4`

选择原因：

- 更适合中文 RAG 场景
- 国内可用性较好
- 与项目国内用户定位一致

### 搜索与抓取

推荐：

- 搜索：博查 AI Search API
- 备选：百度千帆百度搜索 API
- 抓取：后端网页解析，失败时使用搜索摘要兜底

选择原因：

- 博查面向 AI 搜索和 Agent 场景
- 百度千帆更适合作为国内中文搜索备选
- 自建大规模爬虫不适合 MVP

### 文件存储

推荐：

- 本地开发：本地 storage 目录
- 线上部署：Supabase Storage

选择原因：

- 本地开发简单
- 线上部署容易
- 不需要第一版自建 MinIO

### 部署

推荐：

- 前端：Vercel
- 数据库：Supabase PostgreSQL
- 文件：Supabase Storage
- 后端：Render 部署 FastAPI

原因：

- Vercel 适合前端
- Supabase 适合数据库、Storage、pgvector
- Render 更适合独立 FastAPI 后端和后续后台任务

## 9. 系统架构

### 前端架构

Next.js 前端包括：

- 公开页面：首页、登录、注册
- 应用页面：Dashboard、产品空间、知识库、分析任务、报告、设置
- API Client：统一封装后端接口请求
- Auth Guard：保护需要登录的页面
- UI Components：表单、表格、状态标签、报告渲染组件

公开首页只做产品介绍，不重点展示技术栈。

### 后端架构

FastAPI 后端分层：

- `routers`：API 路由
- `schemas`：请求和响应结构
- `models`：数据库模型
- `services`：业务逻辑
- `agents`：Agent 工作流
- `providers`：模型、搜索、抓取、存储等外部能力抽象
- `workers`：文档处理和分析任务后台执行
- `core`：配置、安全、数据库连接、错误处理

### 数据库架构

PostgreSQL 保存：

- 用户
- 产品空间
- 模型配置
- 知识库
- 文档
- 文档 chunk
- 分析任务
- Agent 运行记录
- 报告
- 报告证据

pgvector 保存 `document_chunks` 的向量。

### RAG 架构

流程：

1. 文档上传
2. 文本解析
3. 文本切分
4. 生成 embedding
5. 写入 `document_chunks`
6. 查询时生成 query embedding
7. 使用 pgvector 相似度检索
8. 按 `user_id` 和 `space_id` 过滤
9. 返回可追溯引用片段

### 多 Agent 架构

MVP 不做完全自治 Agent，而是固定流程：

1. 需求理解
2. 私有知识库检索
3. 公开资料收集
4. 竞品分析
5. 产品策略建议
6. 报告生成
7. 质量检查

### 文件处理流程

上传文件 -> 保存原文件 -> 创建 `documents` 记录 -> 解析文本 -> 切分 chunk -> 生成 embedding -> 写入 `document_chunks` -> 更新状态。

### 报告生成流程

任务输入 -> Agent 分析 -> 生成结构化 JSON -> 生成 Markdown 报告 -> 质量检查 -> 保存报告 -> 前端展示。

## 10. 数据模型初稿

### users

作用：保存用户账号信息。

主要字段：

- `id`
- `email`
- `password_hash`
- `display_name`
- `is_admin`
- `created_at`
- `updated_at`

### spaces

作用：保存用户的产品空间。

主要字段：

- `id`
- `user_id`
- `name`
- `industry`
- `product_direction`
- `description`
- `created_at`
- `updated_at`
- `deleted_at`

### model_configs

作用：保存用户模型配置。

主要字段：

- `id`
- `user_id`
- `provider_name`
- `base_url`
- `default_model`
- `encrypted_api_key`
- `api_key_hint`
- `is_active`
- `created_at`
- `updated_at`

### knowledge_bases

作用：保存产品空间的知识库。

主要字段：

- `id`
- `user_id`
- `space_id`
- `name`
- `description`
- `created_at`
- `updated_at`

### documents

作用：保存上传文档记录。

主要字段：

- `id`
- `user_id`
- `space_id`
- `knowledge_base_id`
- `filename`
- `file_type`
- `file_size`
- `storage_path`
- `status`
- `error_message`
- `created_at`
- `updated_at`

### document_chunks

作用：保存文档切片和向量。

主要字段：

- `id`
- `user_id`
- `space_id`
- `document_id`
- `chunk_index`
- `content`
- `embedding`
- `metadata`
- `created_at`

### analysis_tasks

作用：保存竞品分析任务。

主要字段：

- `id`
- `user_id`
- `space_id`
- `title`
- `industry`
- `product_direction`
- `keywords`
- `known_competitors`
- `final_competitors`
- `discovery_mode`
- `status`
- `error_message`
- `created_at`
- `completed_at`

### agent_runs

作用：保存 Agent 执行记录。

主要字段：

- `id`
- `task_id`
- `agent_name`
- `status`
- `input_json`
- `output_json`
- `error_message`
- `started_at`
- `finished_at`

### competitor_reports

作用：保存竞品分析报告。

主要字段：

- `id`
- `user_id`
- `space_id`
- `task_id`
- `title`
- `markdown_content`
- `structured_json`
- `confidence_score`
- `created_at`
- `updated_at`

### report_evidence

作用：保存报告证据来源。

主要字段：

- `id`
- `report_id`
- `source_type`
- `source_title`
- `source_url`
- `document_id`
- `chunk_id`
- `quote`
- `created_at`

## 11. API 模块初稿

接口前缀：`/api/v1`

### auth

- `POST /auth/register`：注册
- `POST /auth/login`：登录
- `POST /auth/logout`：退出
- `GET /auth/me`：获取当前用户

### users

- `GET /users/me`：获取个人资料
- `PATCH /users/me`：更新个人资料

### spaces

- `GET /spaces`：获取产品空间列表
- `POST /spaces`：创建产品空间
- `GET /spaces/{id}`：获取空间详情
- `PATCH /spaces/{id}`：更新空间
- `DELETE /spaces/{id}`：删除空间

### model-configs

- `GET /model-configs`：获取模型配置
- `POST /model-configs`：创建模型配置
- `PATCH /model-configs/{id}`：更新模型配置
- `DELETE /model-configs/{id}`：删除模型配置
- `POST /model-configs/{id}/test`：测试模型连接

### knowledge-bases

- `GET /spaces/{space_id}/knowledge-base`：获取空间默认知识库
- `PATCH /knowledge-bases/{id}`：更新知识库信息

### documents

- `POST /spaces/{space_id}/documents`：上传文档
- `GET /spaces/{space_id}/documents`：获取文档列表
- `GET /documents/{id}`：获取文档详情
- `DELETE /documents/{id}`：删除文档
- `POST /documents/{id}/reindex`：重新索引文档

### retrieval

- `POST /spaces/{space_id}/retrieval/search`：执行 RAG 检索

### analysis-tasks

- `POST /spaces/{space_id}/analysis-tasks`：创建分析任务
- `GET /spaces/{space_id}/analysis-tasks`：获取任务列表
- `GET /analysis-tasks/{id}`：获取任务详情
- `POST /analysis-tasks/{id}/run`：运行任务
- `POST /analysis-tasks/{id}/retry`：重试失败任务

### reports

- `GET /spaces/{space_id}/reports`：获取报告列表
- `GET /reports/{id}`：获取报告详情
- `GET /reports/{id}/evidence`：获取报告证据
- `GET /reports/{id}/export/pdf`：导出 PDF
- `GET /reports/{id}/export/docx`：导出 Word

## 12. 页面规划

### 公开首页

核心内容：

- 平台是做什么的
- 适合谁使用
- 可以上传私有资料
- 可以结合公开竞品信息
- 可以生成 AI 产品经理可用的竞品分析报告

主要操作：

- 注册
- 登录

### 登录页

核心内容：

- 邮箱输入
- 密码输入
- 登录按钮
- 注册入口

主要操作：

- 登录
- 跳转注册页

### 注册页

核心内容：

- 昵称输入
- 邮箱输入
- 密码输入
- 确认密码

主要操作：

- 注册
- 跳转登录页

### Dashboard

核心内容：

- 产品空间列表
- 最近分析任务
- 最近报告
- 知识库状态摘要

主要操作：

- 新建产品空间
- 进入产品空间
- 新建竞品分析任务

### 知识库管理页

核心内容：

- 当前空间文档列表
- 文档状态
- 文档大小
- 上传时间
- 索引状态

主要操作：

- 上传文档
- 删除文档
- 重新索引文档

### 文档上传页

核心内容：

- 上传区域
- 支持格式说明
- 文件大小限制
- 上传进度
- 处理状态

主要操作：

- 选择文件
- 上传文件
- 查看失败原因

### 新建竞品分析任务页

核心内容：

- 行业
- 产品方向
- 关键词
- 已知竞品
- 自动补充竞品开关
- 知识库选择

主要操作：

- 创建任务
- 启动分析

### 分析任务进度页

核心内容：

- 任务状态
- Agent 步骤列表
- 每个 Agent 的运行状态
- 错误信息

主要操作：

- 查看进度
- 重试失败任务
- 跳转报告详情

### 报告详情页

核心内容：

- 报告标题
- 结构化摘要
- Markdown 正文
- 证据来源
- 风险与不确定性

主要操作：

- 查看报告
- 查看证据
- 导出 PDF
- 导出 Word

### 历史报告页

核心内容：

- 报告列表
- 产品空间筛选
- 时间筛选
- 关键词搜索

主要操作：

- 打开报告详情
- 删除报告

### 用户设置页

核心内容：

- 用户资料
- 模型 Provider
- Base URL
- 默认模型
- API Key 脱敏展示

主要操作：

- 更新资料
- 保存模型配置
- 测试模型连接

## 13. 多 Agent 工作流

### 需求理解 Agent

职责：

- 理解用户输入
- 标准化行业、产品方向、关键词
- 判断是否需要自动补充竞品
- 生成后续检索问题

输入：

- 用户任务表单
- 产品空间信息

输出：

- 任务计划 JSON
- 搜索关键词
- RAG 查询问题
- 报告结构

### 私有知识库检索 Agent

职责：

- 根据任务计划检索用户私有知识库
- 找到与产品方向、竞品、市场资料相关的内部片段

输入：

- 任务计划
- `user_id`
- `space_id`
- `knowledge_base_id`

输出：

- 私有知识库引用片段
- 来源文档
- chunk ID
- 相似度

### 公开资料收集 Agent

职责：

- 收集竞品公开资料
- 验证自动补充的候选竞品
- 整理官网、产品页、价格页、帮助文档、新闻稿等来源

输入：

- 竞品名称
- 行业
- 产品方向
- 搜索关键词

输出：

- 公开资料摘要
- 来源 URL
- 证据列表

### 竞品分析 Agent

职责：

- 分析竞品定位
- 总结核心功能
- 判断目标用户
- 梳理商业模式
- 分析 AI 能力

输入：

- 公开资料
- 私有知识库引用
- 任务计划

输出：

- 竞品结构化分析 JSON

### 产品策略建议 Agent

职责：

- 从 AI PM 视角生成产品机会判断
- 提出差异化策略
- 给出可落地产品建议
- 标注风险

输入：

- 竞品分析结果
- 私有知识库引用
- 产品空间背景

输出：

- 差异化机会
- 产品建议
- 风险与不确定性

### 报告生成 Agent

职责：

- 生成中文竞品分析报告
- 输出 Markdown 和结构化 JSON

输入：

- 上游 Agent 结果

输出：

- 报告 Markdown
- 报告 JSON

### 质量检查 Agent

职责：

- 检查报告字段完整性
- 检查是否有来源证据
- 检查是否存在过度推断
- 检查不确定性是否标注

输入：

- 报告草稿
- 证据列表

输出：

- 最终报告
- 质量检查结果
- 置信度提示

## 14. 版本规划

### V0.1：项目骨架与基础用户系统

目标：

- 搭建正式前后端项目结构
- 完成用户注册登录

交付内容：

- Next.js 前端骨架
- FastAPI 后端骨架
- PostgreSQL 数据库连接
- 用户注册、登录、退出
- Dashboard 基础页面

验收标准：

- 用户可以注册
- 用户可以登录
- 用户可以进入 Dashboard
- 未登录用户不能访问应用页面

### V0.2：知识库与文档上传

目标：

- 完成产品空间和文档上传能力

交付内容：

- 产品空间 CRUD
- 默认知识库
- 文档上传
- 文档列表
- 文档状态展示

验收标准：

- 用户可以创建产品空间
- 用户可以上传文档
- 文档记录能保存到数据库
- 用户不能访问其他用户的文档

### V0.3：RAG 检索

目标：

- 完成私有知识库检索闭环

交付内容：

- 文档解析
- 文本切分
- embedding 生成
- pgvector 存储
- RAG 检索接口

验收标准：

- 文档可以被索引
- 查询可以返回相关 chunk
- 检索结果只来自当前用户当前空间

### V0.4：竞品分析任务与报告生成

目标：

- 完成竞品分析主流程

交付内容：

- 新建分析任务
- 基础多 Agent 流程
- 博查 Search Provider
- 半自动补充竞品
- 中文报告生成
- 报告详情页
- 历史报告页

验收标准：

- 用户可以创建竞品分析任务
- 系统可以生成结构化中文报告
- 报告包含核心字段和来源信息
- 自动补充的竞品有搜索证据

### V0.5：多 Agent 工作流优化

目标：

- 提升报告质量和可解释性

交付内容：

- Agent 运行日志
- 质量检查 Agent
- 失败重试
- 证据列表
- PDF / Word 导出
- 必要时引入 Render Worker + Redis

验收标准：

- 用户可以看到 Agent 执行进度
- 报告可以追溯来源
- 报告可导出 PDF 和 Word

### V1.0：GitHub 可展示版本

目标：

- 完成可开源展示版本
- 提供公开 Demo

交付内容：

- README
- 架构图
- 页面截图
- 示例数据
- “企业知识库 Copilot”示例报告
- 本地启动说明
- 部署说明
- 环境变量模板

验收标准：

- 新用户可以根据 README 本地启动项目
- GitHub 页面能清楚展示项目价值
- 示例流程能完整跑通
- 公开 Demo 支持用户自带 API Key 试用

## 15. 项目边界与约束

- 第一阶段不做企业级复杂功能
- 第一阶段不做团队协作
- 第一阶段不做付费系统
- 不追求大规模爬虫能力
- 不保证生成内容完全准确
- 报告必须标注信息来源和不确定性
- 用户数据必须隔离
- API Key 不能明文保存
- API Key、数据库密码、加密密钥不能写入代码仓库
- 代码结构必须适合 GitHub 开源展示
- MVP 优先保证主流程闭环，不追求功能数量

## 16. 风险与应对

### RAG 效果不稳定

风险：

- 检索不到关键内容
- 检索结果和任务不相关

应对：

- 控制 chunk 大小
- 保留 chunk 来源
- 默认 `top_k` 为 8
- 后续加入关键词 + 向量混合检索和 rerank

### 文档解析质量不稳定

风险：

- PDF 解析乱码
- DOCX 格式复杂
- 扫描版 PDF 无法读取

应对：

- MVP 明确不支持 OCR
- 解析失败展示错误原因
- 优先支持文本型 PDF、DOCX、TXT、MD

### 公开信息来源不可靠

风险：

- 搜索结果不准确
- 网页内容过时
- 模型产生错误总结

应对：

- 报告中展示来源 URL
- 区分事实、引用和推断
- 质量检查 Agent 标注不确定性

### 多 Agent 流程过度复杂

风险：

- 实现成本过高
- 调试困难
- 任务失败率高

应对：

- MVP 使用固定流水线
- 每个 Agent 输入输出落库
- 失败时可定位具体步骤

### 成本过高

风险：

- 文档 embedding 成本高
- 报告生成 token 成本高
- 多 Agent 多次调用模型

应对：

- 限制单文件 20MB
- 限制每任务最多 3 个竞品
- 限制 `top_k`
- 控制每个 Agent 输出长度
- 用户使用自己的模型 API Key

### 项目范围膨胀

风险：

- 功能越做越多
- 无法按期形成 GitHub 展示版本

应对：

- 严格按 V0.1 到 V1.0 推进
- V1.0 前不做团队、付费、插件、实时协作、大规模爬虫
- 每个版本都有明确验收标准

## 17. 已确认决策

- 用户偏国内。
- 公开首页只做产品介绍，不重点展示技术栈。
- 示例空间和示例报告围绕“企业知识库 Copilot”。
- 默认模型推荐 DeepSeek。
- 用户自行配置 DeepSeek API Key。
- 模型接口兼容 OpenAI-compatible Provider。
- 默认 embedding 使用通义 DashScope `text-embedding-v4`。
- 默认搜索服务使用博查 AI Search API。
- 百度千帆百度搜索 API 作为备选。
- 竞品输入采用半自动补充模式。
- 用户可输入已知竞品，也可以跳过，由系统全自动发现候选竞品。
- 每个产品空间默认一个知识库。
- PDF / Word 导出后置到 V0.5。
- MVP 暂不做管理员后台。
- 部署采用 Vercel 前端 + Supabase 数据/Storage + Render FastAPI 后端。
- 文档保留 `PRD.md`、`TECH_SPEC.md`、`TASK_BREAKDOWN.md`、`README.md` 四类核心文档。
