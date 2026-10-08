"""Reproduce the iOS file-preview blocked-JavaScript symptom in Chromium."""

from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
PUBLIC_URL = "https://arthurwangwsx-code.github.io/brush-monsters/"

with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    blocked = browser.new_context(viewport={"width": 393, "height": 852}, is_mobile=True, has_touch=True, java_script_enabled=False)
    page = blocked.new_page()
    page.goto((ROOT / "index.html").as_uri())
    assert page.get_by_text("牙牙星球正在起飞", exact=False).is_visible()
    assert page.get_by_text("如果一直停在这里", exact=False).is_visible()
    link = page.get_by_role("link", name="打开在线游戏")
    assert link.is_visible() and link.get_attribute("href") == PUBLIC_URL
    print("PASS 手机文件预览禁用 JavaScript 时，不再只有死加载页")
    blocked.close()
    browser.close()
