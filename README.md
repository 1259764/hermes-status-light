# Hermes Status Light 🚦

实时显示 Hermes Agent 工作状态的红绿灯指示器 — **自动检测模式**。

[English](#english) | [中文](#中文)

---

## 中文

### 这是什么？

一个小型 Web 服务器，通过监控 Hermes Agent 进程的 CPU 活动，自动判断当前状态并在浏览器中显示红绿灯：

- 🔴 **红灯** — Agent 正在执行任务（CPU 活跃）
- 🟢 **绿灯** — 任务完成，等待下一个任务
- ⚫ **灭灯** — Agent 未运行

> **自动检测**：无需 Agent 手动设置，服务器独立监控进程活动，自动切换状态。

### 快速开始

```bash
# 启动服务器
python3 status_light.py start

# 浏览器访问
# http://127.0.0.1:19876
```

### 工作原理

```
┌─────────────┐     ps 监控      ┌──────────────┐     HTTP 轮询     ┌──────────┐
│ Hermes Agent │ ──CPU 活动──→  │  status_light │ ──JSON 状态──→  │  浏览器   │
│   (进程)     │                 │   (监控线程)   │   (每 500ms)    │  (红绿灯) │
└─────────────┘                  └──────────────┘                  └──────────┘
```

- 监控线程每 **2 秒** 检查 Hermes 进程的 CPU 时间
- CPU 时间增长 → 🔴 红灯
- 连续 6 秒无增长 → 🟢 绿灯
- 浏览器每 **500ms** 轮询状态，自动刷新

### API

| 命令 | 说明 |
|------|------|
| `python3 status_light.py start` | 启动服务器 |
| `python3 status_light.py stop` | 停止服务器 |
| `python3 status_light.py status` | 查看当前状态 |

### 作为 Hermes Skill 安装

1. 将 `SKILL.md`、`status_light.py`、`index.html` 放入 `~/.hermes/skills/devops/hermes-status-light/`
2. 加载 skill 后自动启动监控服务器

### 技术细节

- 地址: `http://127.0.0.1:19876`
- 状态 API: `GET /state`
- 进程检测: `ps` 命令（无 `/proc` 扫描，WSL 兼容）
- 依赖: Python 3 标准库（无第三方依赖）

---

## English

### What is this?

A tiny web server that monitors Hermes Agent's CPU activity and displays a traffic light showing its real-time working status:

- 🔴 **Red** — Agent is working (CPU active)
- 🟢 **Green** — Idle, waiting for next task
- ⚫ **Off** — Agent not running

> **Auto-detect**: No manual state setting needed. The server independently monitors process activity.

### Quick Start

```bash
python3 status_light.py start
# Open http://127.0.0.1:19876
```

### How It Works

```
┌─────────────┐    ps polling     ┌──────────────┐    HTTP polling    ┌──────────┐
│ Hermes Agent │ ──CPU usage──→  │  status_light │ ──JSON state──→  │  Browser  │
│  (process)   │   (every 2s)    │  (monitor)    │   (every 500ms)  │ (lights)  │
└─────────────┘                   └──────────────┘                   └──────────┘
```

### API

| Command | Description |
|---------|-------------|
| `python3 status_light.py start` | Start server |
| `python3 status_light.py stop` | Stop server |
| `python3 status_light.py status` | Show current state |

---

## License

MIT
