"""Verify network-first updates and cache namespace isolation with a real Chrome SW.

Uses an in-process HTTP server with a mutable probe response; app files are never
rewritten during the test.
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent / "pwa"
probe = {"value": "release-one"}


class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/probe.txt":
            content = probe["value"].encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return
        if self.path == "/seed":
            content = b"<!doctype html><title>seed</title>"
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            return
        return super().do_GET()

    def log_message(self, *_):
        pass


server = ThreadingHTTPServer(("127.0.0.1", 0), partial(Handler, directory=str(ROOT)))
Thread(target=server.serve_forever, daemon=True).start()
url = f"http://127.0.0.1:{server.server_address[1]}/"


def passed(message, condition):
    if not condition:
        raise AssertionError(message)
    print("PASS", message, flush=True)


try:
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        context = browser.new_context(service_workers="allow")
        page = context.new_page()
        page.goto(url + "seed")
        page.evaluate("""async () => {
            await caches.open('unrelated-app-cache');
            await caches.open('brush-monsters-offline-v1');
        }""")
        page.goto(url, wait_until="networkidle")
        page.evaluate("() => navigator.serviceWorker.ready")
        page.reload()
        keys = page.evaluate("() => caches.keys()")
        passed("清理旧版本刷牙缓存", "brush-monsters-offline-v1" not in keys)
        passed("不删除同一域名其他应用缓存", "unrelated-app-cache" in keys)
        passed("已安装v2 Service Worker", "brush-monsters-offline-v2" in keys and page.evaluate("!!navigator.serviceWorker.controller"))
        first = page.evaluate("() => fetch('./probe.txt').then(r=>r.text())")
        passed("首次联网取得新资源", first == "release-one")
        probe["value"] = "release-two"
        second = page.evaluate("() => fetch('./probe.txt').then(r=>r.text())")
        passed("联网时不被旧缓存挡住更新", second == "release-two")
        context.set_offline(True)
        third = page.evaluate("() => fetch('./probe.txt').then(r=>r.text())")
        passed("断网时提供最近的更新版本", third == "release-two")
        context.close()
        browser.close()
    print("TOTAL 6 PWA UPDATE CHECKS PASSED", flush=True)
finally:
    server.shutdown()
