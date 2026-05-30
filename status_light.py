#!/usr/bin/env python3
"""Hermes Status Light — 自动监控版。服务器独立检测 Agent 状态。"""
import http.server
import json
import os
import signal
import subprocess
import sys
import threading
import time

PORT = 19876
STATE_FILE = "/tmp/hermes_status_light.json"
PID_FILE = "/tmp/hermes_status_light.pid"

# 用单独文件存 HTML，避免长字符串出问题
HTML_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")
_HTML_CACHE = None


def get_html():
    global _HTML_CACHE
    if _HTML_CACHE:
        return _HTML_CACHE
    if os.path.exists(HTML_PATH):
        with open(HTML_PATH, encoding='utf-8') as f:
            _HTML_CACHE = f.read()
        return _HTML_CACHE
    return "<h1>Status Light</h1>"


def read_state():
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except Exception:
        return {"state": "green", "timestamp": ""}


def write_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump({"state": state, "timestamp": time.strftime("%H:%M:%S")}, f)


def find_hermes_pids():
    try:
        r = subprocess.run(
            ['ps', '-eo', 'pid,args', '--no-headers'],
            capture_output=True, text=True, timeout=3
        )
        pids = []
        for line in r.stdout.splitlines():
            parts = line.strip().split(None, 1)
            if len(parts) >= 2:
                if 'hermes-agent' in parts[1] and 'status_light' not in parts[1]:
                    pids.append(int(parts[0]))
        return pids
    except Exception:
        return []


def get_cpu_seconds(pids):
    try:
        pid_list = ','.join(str(p) for p in pids)
        r = subprocess.run(
            ['ps', '-p', pid_list, '-o', 'pid,time', '--no-headers'],
            capture_output=True, text=True, timeout=3
        )
        cpu = {}
        for line in r.stdout.splitlines():
            parts = line.strip().split()
            if len(parts) >= 2:
                pid = int(parts[0])
                t = parts[1].split(':')
                secs = int(t[-1]) + int(t[-2]) * 60
                if len(t) > 2:
                    secs += int(t[-3]) * 3600
                cpu[pid] = secs
        return cpu
    except Exception:
        return {}


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/state':
            body = json.dumps(read_state(), ensure_ascii=False).encode()
            ctype = 'application/json'
        else:
            body = get_html().encode()
            ctype = 'text/html; charset=utf-8'
        self.send_response(200)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):
        pass


def monitor_loop():
    prev_cpu = {}
    idle_count = 0
    while True:
        try:
            pids = find_hermes_pids()
            if not pids:
                if read_state().get('state') != 'off':
                    write_state('off')
                time.sleep(2)
                continue

            cpu_now = get_cpu_seconds(pids)
            active = False
            for pid in pids:
                now = cpu_now.get(pid, 0)
                prev = prev_cpu.get(pid, now)
                prev_cpu[pid] = now
                if now > prev:
                    active = True

            current = read_state()
            if active:
                if current.get('state') != 'red':
                    write_state('red')
                idle_count = 0
            else:
                idle_count += 1
                if idle_count >= 3 and current.get('state') != 'green':
                    write_state('green')

            prev_cpu = {k: v for k, v in prev_cpu.items() if k in pids}
        except Exception:
            pass
        time.sleep(2)


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

    write_state("green")

    threading.Thread(target=monitor_loop, daemon=True).start()
    time.sleep(0.1)  # let monitor init

    srv = http.server.HTTPServer(('127.0.0.1', PORT), Handler)
    srv.allow_reuse_address = True

    with open(PID_FILE, 'w') as f:
        f.write(str(os.getpid()))

    print(f"Traffic Light (auto): http://127.0.0.1:{PORT}", flush=True)
    srv.serve_forever()


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
        print(f"{emoji.get(s['state'],'?')} {s.get('state')} ({s.get('timestamp','')})")
    else:
        print(f"Unknown: {cmd}")


if __name__ == '__main__':
    main()
