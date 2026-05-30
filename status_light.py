#!/usr/bin/env python3
"""
Hermes Status Light — 工作状态红绿灯指示器

A tiny web server that displays Hermes Agent's real-time working status
using a traffic light UI (Red/Yellow/Green).

Usage:
  python3 status_light.py start        # Start server + auto-open browser
  python3 status_light.py red          # 🔴 Working
  python3 status_light.py yellow       # 🟡 Waiting for user
  python3 status_light.py green        # 🟢 Done
  python3 status_light.py off          # ⚫ Idle
  python3 status_light.py status       # Show current state
  python3 status_light.py stop         # Stop server

Server: http://127.0.0.1:19876
"""
import http.server
import json
import os
import signal
import sys
import time
import webbrowser
import threading

PORT = 19876
STATE_FILE = "/tmp/hermes_status_light.json"
PID_FILE = "/tmp/hermes_status_light.pid"

HTML = r"""<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Hermes 工作状态</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    background: #0d1117;
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
    font-family: 'Segoe UI', system-ui, sans-serif;
    user-select: none;
  }
  .container { display: flex; flex-direction: column; align-items: center; gap: 6px; }
  .light-box {
    background: #161b22; border-radius: 24px; padding: 20px 30px;
    display: flex; flex-direction: column; gap: 14px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.5);
  }
  .light { width: 80px; height: 80px; border-radius: 50%; transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1); }
  .light-red    { background: #2d1515; box-shadow: inset 0 4px 12px rgba(0,0,0,0.4); }
  .light-yellow { background: #2d2510; box-shadow: inset 0 4px 12px rgba(0,0,0,0.4); }
  .light-green  { background: #2d1520; box-shadow: inset 0 4px 12px rgba(0,0,0,0.4); }
  .light-red.on    { background: #ff3333; box-shadow: 0 0 40px #ff3333, 0 0 80px #ff222288, inset 0 2px 8px rgba(255,255,255,0.2); }
  .light-yellow.on { background: #ffaa00; box-shadow: 0 0 40px #ffaa00, 0 0 80px #ff880088, inset 0 2px 8px rgba(255,255,255,0.2); }
  .light-green.on  { background: #33ff55; box-shadow: 0 0 40px #33ff55, 0 0 80px #22ff4488, inset 0 2px 8px rgba(255,255,255,0.2); }
  .label { text-align: center; font-size: 13px; color: #8b949e; margin-top: 2px; min-width: 100px; }
  .label .active { color: #e6edf3; font-weight: bold; }
  .footer { font-size: 11px; color: #484f58; margin-top: 12px; }
  .status-text { font-size: 12px; color: #484f58; margin-top: 6px; }
</style>
</head>
<body>
<div class="container">
  <div class="light-box">
    <div class="light light-red" id="red"></div>
    <div class="label"><span id="red-label">编程中</span></div>
    <div class="light light-yellow" id="yellow"></div>
    <div class="label"><span id="yellow-label">请求权限</span></div>
    <div class="light light-green" id="green"></div>
    <div class="label"><span id="green-label">任务完成</span></div>
  </div>
  <div class="status-text" id="status">&#x26ab; 待机</div>
  <div class="footer">Hermes Status Light</div>
</div>
<script>
  let current = 'off';
  async function poll() {
    try {
      const r = await (await fetch('/state')).json();
      if (r.state === current) return;
      document.querySelectorAll('.light').forEach(e=>e.classList.remove('on'));
      document.querySelectorAll('.label span').forEach(e=>e.classList.remove('active'));
      if (r.state && r.state !== 'off') {
        document.getElementById(r.state)?.classList.add('on');
        document.getElementById(r.state+'-label')?.classList.add('active');
      }
      const info = {red:'\u{1f534} 编程中', yellow:'\u{1f7e1} 请求权限', green:'\u{1f7e2} 任务完成', off:'\u26ab 待机'};
      document.getElementById('status').textContent = (info[r.state]||r.state) + (r.timestamp?' \u00b7 '+r.timestamp:'');
      document.title = (info[r.state]||r.state) + ' - Hermes';
      current = r.state;
    } catch(e) {}
  }
  setInterval(poll, 500);
  poll();
</script>
</body>
</html>"""


def read_state():
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except Exception:
        return {"state": "off", "timestamp": ""}


def write_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump({"state": state, "timestamp": time.strftime("%H:%M:%S")}, f)


class Handler(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def do_GET(self):
        if self.path == '/state':
            body = json.dumps(read_state(), ensure_ascii=False).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            body = HTML.encode()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Cache-Control', 'no-store')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    def log_message(self, *args):
        pass


def is_running():
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.5)
    try:
        s.connect(('127.0.0.1', PORT))
        s.close()
        return True
    except Exception:
        return False


def start_server():
    if is_running():
        print(f"Already running: http://127.0.0.1:{PORT}")
        return

    write_state("off")
    server = http.server.HTTPServer(('127.0.0.1', PORT), Handler)
    server.allow_reuse_address = True

    with open(PID_FILE, 'w') as f:
        f.write(str(os.getpid()))

    # Auto-open browser (fails gracefully on headless/WSL)
    def _open():
        try:
            webbrowser.open(f"http://127.0.0.1:{PORT}")
        except Exception:
            pass
    threading.Thread(target=_open, daemon=True).start()

    print(f"Traffic Light Server: http://127.0.0.1:{PORT}", flush=True)
    server.serve_forever()


def stop_server():
    if os.path.exists(PID_FILE):
        try:
            with open(PID_FILE) as f:
                os.kill(int(f.read().strip()), signal.SIGTERM)
            os.remove(PID_FILE)
            print("Server stopped")
            return
        except Exception:
            pass
    print("No running server found")


def set_state(state):
    write_state(state)
    emoji = {"red": "🔴", "yellow": "🟡", "green": "🟢", "off": "⚫"}
    name = {"red": "Working", "yellow": "Requesting", "green": "Done", "off": "Idle"}
    print(f"{emoji[state]} {name[state]}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    cmd = sys.argv[1].lower()

    if cmd == 'start':
        start_server()
    elif cmd == 'stop':
        stop_server()
    elif cmd == 'status':
        s = read_state()
        emoji = {"red": "🔴", "yellow": "🟡", "green": "🟢", "off": "⚫"}
        name = {"red": "Working", "yellow": "Requesting", "green": "Done", "off": "Idle"}
        print(f"{emoji.get(s['state'], '?')} {name.get(s['state'], s['state'])} ({s.get('timestamp', '')})")
    elif cmd in ('red', 'yellow', 'green', 'off'):
        set_state(cmd)
    else:
        print(f"Unknown command: {cmd}")


if __name__ == '__main__':
    main()
