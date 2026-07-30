# 前端体验优化交接

## 已实现

- 左侧导航按当前路由显示活动状态；服务端 `AppShell` 保持服务端边界，路径判断仅在客户端 `AppNavigation` 执行。
- 首页流程卡明确“研究流程”及可核查来源与研究记录。
- 工作台以“研究总览”为主标题，用户名与下一步说明作为辅助信息，不再在首屏展示邮箱。
- DeepSeek 页面标题统一为“模型设置”；掩码、密码框、保存后清空和既有服务端加密契约未改变。

## 已验证

- `npm.cmd test`：32 文件、117 项通过。
- `npm.cmd run check:routes`：通过。
- `npx.cmd tsc --noEmit`：通过。
- `npm.cmd run lint`：通过。
- `npm.cmd run build`：通过，11 条路由生成成功。
- `git diff --check main...HEAD`：通过。

## 未验证边界

- 未调用真实 DashScope、DeepSeek 或 Bocha Provider。
- 未做生产部署、CI、跨设备视觉验收或公开 Demo。
- 未读取、复制或修改任何真实密钥、Cookie、Token 或环境文件。
