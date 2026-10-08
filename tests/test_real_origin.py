"""Real Chrome / real HTTP origin acceptance, no localStorage mock.

Run: python3 tests/test_real_origin.py
The static server should be running at http://127.0.0.1:8765.
"""
import datetime
import json
import re
from pathlib import Path

from playwright.sync_api import sync_playwright

URL = "http://127.0.0.1:8765/"
KEY = "yaya-brush-monsters:v1"
CHECKS = []


def ok(name, predicate):
    if not predicate:
        raise AssertionError(name)
    CHECKS.append(name)
    print("PASS", name, flush=True)


def data(page):
    return json.loads(page.evaluate("(k) => localStorage.getItem(k)", KEY))


def rush_zones(page, first_remaining_ms=30100):
    """Jump to each zone boundary; only 1.05s transitions need stepped timers."""
    for zone in range(4):
        page.clock.fast_forward(first_remaining_ms if zone == 0 else 30200)
        page.clock.run_for(200)
        if zone < 3:
            page.clock.run_for(1300)
            assert data(page)["session"]["zoneIndex"] == zone + 1


with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    context = browser.new_context(
        viewport={"width": 393, "height": 852},
        device_scale_factor=3,
        is_mobile=True,
        has_touch=True,
        timezone_id="Asia/Shanghai",
        accept_downloads=True,
    )
    page = context.new_page()
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.on("console", lambda m: errors.append("console: " + m.text) if m.type == "error" else None)
    page.clock.install(time=datetime.datetime(2026, 10, 8, 0, 0, tzinfo=datetime.timezone.utc))
    response = page.goto(URL, wait_until="domcontentloaded")
    ok("HTTP 200 and real origin", response.status == 200 and page.evaluate("location.origin") == "http://127.0.0.1:8765")
    ok("真实 localStorage，无模拟替身", bool(page.evaluate(f"localStorage.getItem('{KEY}')")))
    ok("默认早上/四区30秒", page.locator("button.slot.selected").inner_text().startswith("☀") and data(page)["settings"]["durations"] == [30, 30, 30, 30])
    ok("393px 竖屏无横向溢出", page.evaluate("document.documentElement.scrollWidth <= innerWidth"))
    page.screenshot(path=str(Path(__file__).resolve().parent.parent / "acceptance-home.png"))
    page.locator("[data-action=start]").click()
    ok("开始后右上区域高亮", page.locator(".mouth-area.active").inner_text().strip() == "右上")
    ok("游戏不超过852px高度", page.evaluate("document.documentElement.scrollHeight <= innerHeight"))
    page.clock.fast_forward(12500)
    page.clock.run_for(150)
    mid = data(page)
    print("TIMER EVIDENCE", mid["session"]["elapsedMs"], page.locator("#hpFill").evaluate("(e)=>e.style.width"), flush=True)
    ok("真实计时、血条递减", 12000 <= mid["session"]["elapsedMs"] <= 15000 and float(page.locator("#hpFill").evaluate("(e)=>parseFloat(e.style.width)")) < 65)
    page.screenshot(path=str(Path(__file__).resolve().parent.parent / "acceptance-game.png"))
    page.reload(wait_until="domcontentloaded")
    paused = data(page)
    ok("真实刷新保留已刷12秒，自动暂停", paused["session"]["phase"] == "paused" and paused["session"]["elapsedMs"] >= 12000 and page.locator("[data-action=resume]").count() == 1)
    page.locator("[data-action=resume]").click()
    ok("恢复后倒计时没有归零", int(page.locator("#secondsRemaining").inner_text()) < 30)
    rush_zones(page, first_remaining_ms=19000)
    first = data(page)
    ok("四个区自动完成并产生一颗早星", page.locator(".victory").count() == 1 and first["records"]["2026-10-08"].get("morning") and not first["records"]["2026-10-08"].get("evening"))
    ok("完成后没有残留进度，四只普通怪兽收录", first["session"] is None and len(first["unlocked"]) == 4)
    page.reload(wait_until="domcontentloaded")
    persisted = data(page)
    ok("真实刷新后星星和图鉴持久保留", bool(persisted["records"]["2026-10-08"]["morning"]) and len(persisted["unlocked"]) == 4)
    page.locator("[data-action=select-slot][data-slot=evening]").click()
    page.locator("[data-action=start]").click()
    rush_zones(page)
    second = data(page)
    ok("早晚分开计星", len(second["records"]["2026-10-08"]) == 2)
    page.locator("[data-action=home]").first.click()
    page.locator("[data-action=start]").click()
    rush_zones(page)
    repeat = data(page)
    ok("同一时段不能重复奖励星星", len(repeat["records"]["2026-10-08"]) == 2 and "又赢啦" in page.locator(".victory h1").inner_text())
    page.locator("[data-action=home]").first.click()
    gate = page.locator("#parentGate")
    gate.dispatch_event("pointerdown", {"button": 0, "pointerType": "touch"})
    page.clock.run_for(1000)
    gate.dispatch_event("pointerup", {"button": 0, "pointerType": "touch"})
    page.clock.run_for(1500)
    ok("短按不进入家长专区", page.locator("#gateForm").count() == 0)
    gate.dispatch_event("pointerdown", {"button": 0, "pointerType": "touch"})
    page.clock.run_for(2300)
    ok("长按2200毫秒才出现家长门禁", page.locator("#gateForm").count() == 1)
    q = page.locator(".gate-equation").inner_text()
    a, b = map(int, re.findall(r"\d+", q))
    page.locator("#gateAnswer").fill("1")
    page.locator("#gateForm button").click()
    ok("错误乘法答案无法进入", "再检查" in page.locator("#gateError").inner_text())
    page.locator("#gateAnswer").fill(str(a * b))
    page.locator("#gateForm button").click()
    ok("正确答案进入家长中心", "家长中心" in page.locator("h1").inner_text())
    ok("30天晨晚表及计数", page.locator(".history-row").count() == 31 and page.locator(".parent-stat strong").first.inner_text() == "2")
    page.locator("[data-action=adjust][data-index='0'][data-step='5']").click()
    ok("逐区设置30→35秒落盘", data(page)["settings"]["durations"] == [35, 30, 30, 30])
    with page.expect_download() as info:
        page.locator("[data-action=export]").click()
    download = info.value
    export_path = Path(__file__).resolve().parent.parent / "acceptance-backup.json"
    download.save_as(export_path)
    backed = json.loads(export_path.read_text())
    ok("下载JSON备份包含记录和设置", backed["records"] == data(page)["records"] and backed["settings"]["durations"][0] == 35)
    page.locator("[data-action=adjust][data-index='0'][data-step='5']").click()
    context.on("dialog", lambda dlg: dlg.accept())
    page.locator("#importFile").set_input_files(str(export_path))
    page.wait_for_timeout(300)
    ok("导入备份后恢复原设置及记录", data(page)["settings"]["durations"][0] == 35 and len(data(page)["records"]["2026-10-08"]) == 2)
    page.reload(wait_until="domcontentloaded")
    ok("设置和记录经历再次刷新仍保留", data(page)["settings"]["durations"][0] == 35 and len(data(page)["records"]["2026-10-08"]) == 2)
    ok("更改区域时长后总时长02:05", "02:05" in page.locator(".btn-caption").inner_text())
    ok("所有测试无未处理JS异常", not errors)
    print(f"\nTOTAL {len(CHECKS)} REAL-ORIGIN CHECKS PASSED", flush=True)
    context.close()
    browser.close()
