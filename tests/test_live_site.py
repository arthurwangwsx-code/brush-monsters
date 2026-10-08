"""Real public HTTPS GitHub Pages smoke + PWA offline/record persistence.

Never use mocked storage. This test starts from a clean Chrome browser profile.
"""

from playwright.sync_api import sync_playwright

URL = "https://arthurwangwsx-code.github.io/brush-monsters/"
count = 0


def check(label, condition):
    global count
    if not condition:
        raise AssertionError(label)
    count += 1
    print("PASS", label, flush=True)


with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    context = browser.new_context(
        viewport={"width": 393, "height": 852},
        device_scale_factor=3,
        is_mobile=True,
        has_touch=True,
        service_workers="allow",
        timezone_id="Asia/Kuala_Lumpur",
    )
    page = context.new_page()
    page.clock.install()
    errors = []
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)
    response = page.goto(URL, wait_until="networkidle", timeout=40000)
    check("公网网站HTTPS成功响应", response.status == 200 and page.evaluate("isSecureContext"))
    check("公网游戏已离开加载页面", page.locator("[data-action=start]").count() == 1)
    check("手机视口无横向滚动", page.evaluate("document.documentElement.scrollWidth <= innerWidth"))
    manifest = page.evaluate("() => fetch('./manifest.webmanifest').then(r => r.json())")
    check("公网PWA清单可读取", manifest["display"] == "standalone")
    sw = page.evaluate("() => Promise.race([navigator.serviceWorker.ready.then(reg=>!!reg.active), new Promise(r=>setTimeout(()=>r(false),10000))])")
    check("公网Service Worker已安装", sw)
    page.reload(wait_until="domcontentloaded")
    check("公网Service Worker接管页面", page.evaluate("!!navigator.serviceWorker.controller"))
    context.set_offline(True)
    page.reload(wait_until="domcontentloaded", timeout=15000)
    check("公网安装后断网仍能重新打开", page.locator("[data-action=start]").count() == 1)
    page.locator("[data-action=start]").click()
    check("断网状态可开始游戏", page.locator(".mouth-area.active").inner_text().strip() == "右上")
    page.clock.fast_forward(15000)
    page.clock.run_for(150)
    check("断网状态游戏计时仍推进", int(page.locator("#secondsRemaining").inner_text()) < 30)
    page.reload(wait_until="domcontentloaded")
    check("断网刷新继续刷牙按钮存在", page.locator("[data-action=resume]").count() == 1)
    page.locator("[data-action=resume]").click()
    check("断网续刷仍保留已刷时间", int(page.locator("#secondsRemaining").inner_text()) < 30)
    check("没有未处理的公网JavaScript错误", not errors)
    print("TOTAL", count, "PUBLIC HTTPS CHECKS PASSED", flush=True)
    context.close()
    browser.close()
