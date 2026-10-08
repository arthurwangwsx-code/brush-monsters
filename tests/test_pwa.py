"""PWA service worker / offline acceptance on real Chromium HTTP origin."""
from playwright.sync_api import sync_playwright

URL = "http://127.0.0.1:8765/pwa/"
checks = []


def ok(name, condition):
    if not condition:
        raise AssertionError(name)
    checks.append(name)
    print("PASS", name, flush=True)


with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    context = browser.new_context(
        viewport={"width": 393, "height": 852},
        device_scale_factor=3,
        has_touch=True,
        is_mobile=True,
        service_workers="allow",
    )
    page = context.new_page()
    console_errors = []
    page.on("pageerror", lambda err: console_errors.append(str(err)))
    page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
    response = page.goto(URL, wait_until="networkidle")
    ok("完整 PWA 网页 HTTP 200", response.status == 200)
    ok("脚本、样式均成功加载", page.locator("[data-action=start]").count() == 1)
    registration = page.evaluate(
        "() => Promise.race([navigator.serviceWorker.ready.then(r=>({scope:r.scope,active:!!r.active})),new Promise(res=>setTimeout(()=>res(null),9000))])"
    )
    ok("Service Worker 注册并激活", bool(registration and registration["active"]))
    keys = page.evaluate("() => caches.keys()")
    ok("v2 离线缓存安装成功", "brush-monsters-offline-v2" in keys)
    page.reload(wait_until="domcontentloaded")
    ok("页面由 Service Worker 控制", page.evaluate("!!navigator.serviceWorker.controller"))
    context.set_offline(True)
    page.reload(wait_until="domcontentloaded", timeout=15000)
    ok("断网状态仍然可以打开游戏", page.locator("[data-action=start]").count() == 1)
    page.locator("[data-action=start]").click()
    ok("断网状态仍可正常开始游戏", page.locator(".game-title").inner_text() == "刷你的右上牙！")
    page.locator("[data-action=pause]").first.click()
    page.reload(wait_until="domcontentloaded")
    ok("断网刷新也保留未完成进度", page.locator("[data-action=resume]").count() == 1)
    ok("没有未处理的浏览器脚本错误", not console_errors)
    print("TOTAL", len(checks), "PWA CHECKS PASSED", flush=True)
    context.close()
    browser.close()
