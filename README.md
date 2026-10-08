# 刷牙打怪兽 · PersonalAI Chrome 验收工程

源码和自动化测试保存在 PersonalAI Mac 上，可复验、继续迭代；
`pwa/` 子目录同步发布为 GitHub Pages 的 HTTPS 公网游戏。

**在线版本：** https://arthurwangwsx-code.github.io/brush-monsters/

线上网站由 GitHub Pages 托管，公开的仅是游戏前端代码和静态资源。
孩子的刷牙记录不会上传到 GitHub，存储在打开网站的设备浏览器中。
建议在 iPhone Safari 打开在线网址，分享菜单中选择“添加到主屏幕”。

请注意：ChatGPT 对 HTML 附件的预览可能禁用脚本；不要把 HTML 文件下载链接当成在线体验网址。
如预览页停在“正在起飞”，应点击页面中的“打开在线游戏”链接。

部署时，GitHub Pages 的根目录使用仓库中 `pwa/` 子树对应的 `gh-pages` 分支，
而非指向单文件的 `main` 分支。更新步骤：

```bash
git branch -f gh-pages "$(git subtree split --prefix=pwa)"
git push origin main gh-pages
```

首次创建公开 Pages 项目后已经配置了 `gh-pages` / 根目录；
日后执行上述命令前须先运行并通过测试，不应直接发布未经验证的分支。

运行本地静态站点（一个终端）：`python3 -m http.server 8765 --bind 127.0.0.1`

随后运行：

- `python3 tests/test_real_origin.py`：单文件网页 25 项真实 HTTP/本地存储验收。
- `python3 tests/test_pwa.py`：PWA 注册、缓存、离线启动与恢复 9 项。
- `python3 tests/test_pwa_update.py`：带临时 HTTP Server 的缓存更新验证 6 项。
- `python3 tests/test_file_preview.py`：模拟文件预览禁用 JS 的情况，检查可见兜底链接。
- `python3 tests/test_mobile_webkit.py`：iPhone WebKit 触屏视口，检查倒计时和续刷。
- `python3 tests/test_live_site.py`：对公网 HTTPS 链接进行 Chrome + 离线恢复验收。

2026-10-08 已通过 Chrome 本地源、WebKit iPhone 触屏视口和公网 HTTPS 的测试。
静态站点所有公开资源均响应 200；断网后也能恢复游戏进度。
PWA 的 192/512 图标已由可爱的 SVG 怪兽图标生成，不再是临时白圆圈。

**边界：** WebKit 的 iPhone 模拟视口不等于真实 iPhone Safari；
中文语音是否真正发声、iOS 添加到主屏幕后的交互和 Safari 持久化，仍需真实设备验收。
