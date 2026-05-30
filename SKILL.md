---
name: hermes-status-light
description: 工作状态红绿灯指示器 — 自动监控 Hermes Agent 进程活动：🔴工作中 / 🟢空闲。浏览器打开即用，每次会话自动启动。
version: 2.0.0
---

# Hermes 工作状态红绿灯（自动监控版）

一个独立小窗口，通过监控 Hermes Agent 进程的 CPU 活动，自动判断工作状态并以红绿灯显示。

## ⚡ 自动启动

当 Hermes Agent 加载本 skill 时，**立即检查并启动红绿灯服务器**（如果未运行）：

```bash
python3 ~/.hermes/skills/devops/hermes-status-light/status_light.py start
```

`start` 命令是幂等的（重复执行无副作用）。

## 工作原理

服务器后台线程每 2 秒通过 `ps` 命令检查 Hermes Agent 进程的 CPU 累计时间：

- **CPU 时间增长** → 🔴 红灯（Agent 正在干活）
- **连续 6 秒无增长** → 🟢 绿灯（Agent 空闲等待）
- **进程未运行** → ⚫ 灭灯

> **无需 Agent 手动设置状态，服务器独立监控。**

## 状态含义

| 颜色 | 含义 | 触发条件 |
|------|------|---------|
| 🔴 红 | 编程中 | Hermes 进程 CPU 活跃 |
| 🟢 绿 | 任务完成 | Hermes 进程空闲（≥6秒） |
| ⚫ 灭 | 离线 | Hermes 进程未运行 |

## 手动使用

```bash
# 启动服务器
python3 ~/.hermes/skills/devops/hermes-status-light/status_light.py start

# 查询当前状态
python3 ~/.hermes/skills/devops/hermes-status-light/status_light.py status

# 停止服务器
python3 ~/.hermes/skills/devops/hermes-status-light/status_light.py stop
```

## 技术细节

- 地址: http://127.0.0.1:19876
- 状态API: GET /state
- 进程检测: `ps` 命令（兼容 WSL）
- 依赖: Python 3 标准库（无第三方依赖）
- 浏览器刷新: 每 500ms 自动轮询
