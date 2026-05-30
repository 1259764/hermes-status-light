---
name: hermes-status-light
description: 工作状态红绿灯指示器 — 小窗口显示 Hermes Agent 当前状态：🔴编程中 / 🟡请求权限 / 🟢任务完成。浏览器自动打开，每次会话自动启动。
version: 1.2.0
---

# Hermes 工作状态红绿灯

一个独立小窗口，用 CSS 红绿灯显示 Hermes Agent 的实时工作状态。

## ⚡ 自动启动

当 Hermes Agent 加载本 skill 时，**立即检查并启动红绿灯服务器**（如果未运行），并尝试自动打开浏览器：

```bash
python3 ~/.hermes/skills/devops/hermes-status-light/status_light.py start
```

`start` 命令是幂等的（重复执行无副作用），且会自动尝试打开浏览器窗口。

## 状态含义

| 颜色 | 含义 | 触发时机 |
|------|------|---------|
| 🔴 红 | 编程中 | Hermes 正在执行任务、写代码、搜索 |
| 🟡 黄 | 请求权限 | Hermes 等待用户确认 |
| 🟢 绿 | 任务完成 | 回复已生成，等待下一个任务 |
| ⚫ 灭 | 待机 | 空闲 |

## Hermes Agent 使用规范

**每次回复周期必须按以下节奏更新红绿灯：**

1. **收到用户消息，开始处理** → 立即执行 `red`
2. **需要用户确认** → 执行 `yellow`
3. **回复完成，发送给用户前** → 执行 `green`

命令：
```bash
python3 ~/.hermes/skills/devops/hermes-status-light/status_light.py red
python3 ~/.hermes/skills/devops/hermes-status-light/status_light.py yellow
python3 ~/.hermes/skills/devops/hermes-status-light/status_light.py green
```

## 手动使用

```bash
# 首次启动（自动打开浏览器小窗口）
python3 ~/.hermes/skills/devops/hermes-status-light/status_light.py start

# 切换状态
python3 ~/.hermes/skills/devops/hermes-status-light/status_light.py red     # 🔴 编程中
python3 ~/.hermes/skills/devops/hermes-status-light/status_light.py yellow  # 🟡 请求权限
python3 ~/.hermes/skills/devops/hermes-status-light/status_light.py green   # 🟢 任务完成
python3 ~/.hermes/skills/devops/hermes-status-light/status_light.py off     # ⚫ 关闭

# 查询当前状态
python3 ~/.hermes/skills/devops/hermes-status-light/status_light.py status

# 停止服务器
python3 ~/.hermes/skills/devops/hermes-status-light/status_light.py stop
```

## 技术细节

- 地址: http://127.0.0.1:19876
- 状态API: GET /state
- 状态文件: /tmp/hermes_status_light.json
- PID文件: /tmp/hermes_status_light.pid
- 通信方式: 文件写入（CLI → /tmp/hermes_status_light.json）+ HTTP轮询（浏览器 ← 服务器）
- 依赖: Python 3 标准库（无第三方依赖）
- 自动刷新: 浏览器每 500ms 轮询，无需手动刷新
