# 刷牙打怪兽 · PersonalAI Chrome 验收工程

本项目留在 PersonalAI Mac 上，用于复验和后续迭代，不是公网部署。

**在线版本：** https://arthurwangwsx-code.github.io/brush-monsters/

线上网站由 GitHub Pages 托管，公开的仅是游戏前端代码和静态资源。
孩子的刷牙记录不会上传到 GitHub，存储在打开网站的设备浏览器中。
建议在 iPhone Safari 打开在线网址，分享菜单中选择“添加到主屏幕”。

请注意：ChatGPT 对 HTML 附件的预览可能禁用脚本；不要把 HTML 文件下载链接当成在线体验网址。
如预览页停在“正在起飞”，应点击页面中的“打开在线游戏”链接。

部署时，GitHub Pages 的根目录使用仓库中 `pwa/` 子树对应的 `gh-pages` 分支，
而非指向单文件的 `main` 分支。更新步骤：

```bash
git subtree split --prefix=pwa -b gh-pages
git push origin main gh-pages
```

后续更新分支可以用 `git branch -f gh-pages "$(git subtree split --prefix=pwa)"`
然后 `git push origin main gh-pages`，确保更新测试通过后再发布。

运行本地静态站点（一个终端）：`python3 -m http.server 8765 --bind 127.0.0.1`

随后运行：

- `python3 tests/test_real_origin.py`：单文件网页 25 项真实 HTTP/本地存储验收。
- `python3 tests/test_pwa.py`：PWA 注册、缓存、离线启动与恢复 9 项。
- `python3 tests/test_pwa_update.py`：带临时 HTTP Server 的缓存更新验证 6 项。
- `python3 tests/test_file_preview.py`：模拟文件预览禁用 JS 的情况，检查可见兜底链接。

已在 2026-10-08 运行，全部通过。单文件版本 SHA-256：
`6a8d04fe982800d94b86825b34a3b7ea40528c2b902363346e20056981ee62d8`，
与 ChatGPT 交付的最新 HTML 完全一致。

PWA 目录里的游戏 CSS/JavaScript 与交付包逻辑一致；`icon-192.png`、
`icon-512.png` 是为了让本地 SW 安装测试成功而生成的**测试占位图标**，
并不是交付包中正式图标。最终源代码 ZIP 中有正式的 192/512 PNG 图标。

这些验证不证明 iPhone Safari、实际中文语音或公网 HTTPS 已通过。
