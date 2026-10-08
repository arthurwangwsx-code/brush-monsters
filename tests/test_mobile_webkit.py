"""Run the real game in WebKit with iPhone viewport and touch settings.

BRUSH_BASE_URL=https://example.com/ python3 tests/test_mobile_webkit.py
This is a WebKit simulation, not a real iPhone hardware test.
"""

import os
from playwright.sync_api import sync_playwright

URL = os.environ.get('BRUSH_BASE_URL', 'http://127.0.0.1:8765/pwa/')
passed = 0


def check(name, result):
    global passed
    if not result:
        raise AssertionError(name)
    passed += 1
    print('PASS', name, flush=True)


with sync_playwright() as p:
    browser = p.webkit.launch(headless=True)
    device = p.devices['iPhone 13']
    context = browser.new_context(**device, locale='zh-CN', timezone_id='Asia/Kuala_Lumpur')
    page = context.new_page()
    errors = []
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.clock.install()
    resp = page.goto(URL, wait_until='domcontentloaded', timeout=30000)
    check('WebKit HTTPS/HTTP 页面可达', resp.status == 200)
    check('iPhone 宽度中首页可点击', page.locator('[data-action=start]').is_visible())
    check('iPhone 上没有横向溢出', page.evaluate('document.documentElement.scrollWidth <= innerWidth'))
    page.locator('[data-action=start]').tap()
    check('触屏启动右上区域', page.locator('.mouth-area.active').inner_text().strip() == '右上')
    page.clock.fast_forward(15000)
    page.clock.run_for(150)
    check('WebKit 倒计时正在变化', int(page.locator('#secondsRemaining').inner_text()) < 30)
    check('血条随时间减少', float(page.locator('#hpFill').evaluate('(e)=>parseFloat(e.style.width)')) < 70)
    page.reload(wait_until='domcontentloaded')
    check('iPhone 刷新后出现继续刷牙', page.locator('[data-action=resume]').count() == 1)
    page.locator('[data-action=resume]').tap()
    check('继续刷牙保留时间', int(page.locator('#secondsRemaining').inner_text()) < 30)
    check('无未处理 WebKit JavaScript 异常', not errors)
    print('TOTAL',passed,'WEBKIT IPHONE-VIEWPORT CHECKS PASSED',flush=True)
    browser.close()
