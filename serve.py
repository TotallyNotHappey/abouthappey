"""Toggle the HappeyOS local server (same-Wi-Fi phone testing).

Double-click to start, double-click again to stop.
Serves this folder at http://<your-lan-ip>:8000
"""
import os
import socket
import subprocess
import sys
import time
import urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
PIDFILE = os.path.join(ROOT, ".serve.pid")
PORT = 8000


def lan_ip():
    cands = []
    try:
        for fam, _, _, _, addr in socket.getaddrinfo(
                socket.gethostname(), None, socket.AF_INET):
            ip = addr[0]
            if ip.startswith("127.") or ip.startswith("169.254."):
                continue
            if ip not in cands:
                cands.append(ip)
    except OSError:
        pass
    for ip in cands:
        if ip.startswith("192.168."):
            return ip
    for ip in cands:
        if ip.startswith("10."):
            return ip
    if cands:
        return cands[0]
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except OSError:
        return "localhost"


def pid_running(pid):
    try:
        out = subprocess.run(
            ["tasklist", "/FI", "PID eq %d" % pid],
            capture_output=True, text=True,
        ).stdout
        return "python" in out.lower()
    except OSError:
        return False


def read_pid():
    try:
        with open(PIDFILE, encoding="utf-8") as f:
            return int(f.read().strip())
    except (OSError, ValueError):
        return None


def run_server():
    import functools
    from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

    class H(SimpleHTTPRequestHandler):
        def end_headers(self):
            self.send_header("Cache-Control", "no-store")
            super().end_headers()

        def log_message(self, *a):
            pass

    handler = functools.partial(H, directory=ROOT)
    ThreadingHTTPServer(("0.0.0.0", PORT), handler).serve_forever()


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--serve":
        run_server()
        return
    pid = read_pid()
    if pid and pid_running(pid):
        subprocess.run(["taskkill", "/F", "/PID", str(pid)],
                       capture_output=True)
        try:
            os.remove(PIDFILE)
        except OSError:
            pass
        print("[HappeyOS] server stopped.")
        return
    if pid:
        try:
            os.remove(PIDFILE)
        except OSError:
            pass
    proc = subprocess.Popen(
        [sys.executable, os.path.abspath(__file__), "--serve"],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=getattr(subprocess, "DETACHED_PROCESS", 0),
    )
    with open(PIDFILE, "w", encoding="utf-8") as f:
        f.write(str(proc.pid))
    time.sleep(1)
    url = "http://%s:%d" % (lan_ip(), PORT)
    ok = False
    try:
        with urllib.request.urlopen("http://127.0.0.1:%d/" % PORT, timeout=5) as r:
            ok = r.status == 200
    except Exception:
        ok = False
    if ok:
        print("[HappeyOS] serving this folder  ->  %s" % url)
        print("On your phone (same Wi-Fi), open that URL. Run again to stop.")
    else:
        print("[HappeyOS] started (pid %d) but the localhost check failed." % proc.pid)
        print("If your phone can't connect, allow TCP %d in Windows Firewall:" % PORT)
        print("  New-NetFirewallRule -DisplayName HappeyOS -Direction Inbound -LocalPort %d -Protocol TCP -Action Allow" % PORT)


if __name__ == "__main__":
    main()
    try:
        input("Press Enter to close... ")
    except EOFError:
        pass
