# Hermes Status Light 🚦

实时显示 Hermes Agent 工作状态的红绿灯指示器。

[English](#english) | [中文](#中文)

---

## 中文

### 这是什么？

一个小型 Web 服务器，在浏览器中显示一个红绿灯，实时反映 Hermes Agent 的当前状态：

- 🔴 **红灯** — Agent 正在执行任务（写代码、搜索等）
- 🟡 **黄灯** — Agent 正在等待用户确认
- 🟢 **绿灯** — 任务完成，等待下一个任务
- ⚫ **灭灯** — 待机

### 快速开始

```bash
# 启动服务器（会自动打开浏览器）
python3 status_light.py start

# 浏览器访问
# http://127.0.0.1:19876
```

### API

| 命令 | 说明 |
|------|------|
| `python3 status_light.py start` | 启动服务器 + 自动打开浏览器 |
| `python3 status_light.py red` | 🔴 设为编程中 |
| `python3 status_light.py yellow` | 🟡 设为请求权限 |
| `python3 status_light.py green` | 🟢 设为任务完成 |
| `python3 status_light.py off` | ⚫ 设为待机 |
| `python3 status_light.py status` | 查看当前状态 |
| `python3 status_light.py stop` | 停止服务器 |

### 作为 Hermes Skill 安装

1. 将 `SKILL.md` 和 `status_light.py` 放入 `~/.hermes/skills/devops/hermes-status-light/`
2. 加载 skill 后 Hermes Agent 会自动启动服务器

### 技术细节

- 地址: `http://127.0.0.1:19876`
- 状态 API: `GET /state`
- 通信方式: 文件写入（CLI → JSON）+ HTTP 轮询（浏览器 ← 服务器）
- 依赖: Python 3 标准库（无第三方依赖）
- 自动刷新: 浏览器每 500ms 轮询一次状态

---

## English

### What is this?

A tiny web server that displays a traffic light in your browser, showing Hermes Agent's real-time working status:

- 🔴 **Red** — Agent is working (coding, searching, etc.)
- 🟡 **Yellow** — Agent is waiting for user confirmation
- 🟢 **Green** — Task complete, waiting for next task
- ⚫ **Off** — Idle

### Quick Start

```bash
# Start the server (auto-opens browser)
python3 status_light.py start

# Open in browser
# http://127.0.0.1:19876
```

### API

| Command | Description |
|---------|-------------|
| `python3 status_light.py start` | Start server + auto-open browser |
| `python3 status_light.py red` | 🔴 Set to Working |
| `python3 status_light.py yellow` | 🟡 Set to Requesting |
| `python3 status_light.py green` | 🟢 Set to Done |
| `python3 status_light.py off` | ⚫ Set to Idle |
| `python3 status_light.py status` | Show current state |
| `python3 status_light.py stop` | Stop server |

### Install as Hermes Skill

1. Place `SKILL.md` and `status_light.py` into `~/.hermes/skills/devops/hermes-status-light/`
2. Hermes Agent will auto-start the server when the skill is loaded

### Tech Details

- Address: `http://127.0.0.1:19876`
- State API: `GET /state`
- Communication: File write (CLI → JSON) + HTTP polling (Browser ← Server)
- Dependencies: Python 3 stdlib only
- Auto-refresh: Browser polls every 500ms

---

## License

MIT
