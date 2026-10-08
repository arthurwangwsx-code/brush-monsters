# 刷牙打怪兽 · PersonalAI Chrome 验收工程

本项目留在 PersonalAI Mac 上，用于复验和后续迭代，不是公网部署。

运行本地静态站点（一个终端）：`python3 -m http.server 8765 --bind 127.0.0.1`

随后运行：

- `python3 tests/test_real_origin.py`：单文件网页 25 项真实 HTTP/本地存储验收。
- `python3 tests/test_pwa.py`：PWA 注册、缓存、离线启动与恢复 9 项。
- `python3 tests/test_pwa_update.py`：带临时 HTTP Server 的缓存更新验证 6 项。

已在 2026-10-08 运行，全部通过。单文件版本 SHA-256：
`6a8d04fe982800d94b86825b34a3b7ea40528c2b902363346e20056981ee62d8`，
与 ChatGPT 交付的最新 HTML 完全一致。

PWA 目录里的游戏 CSS/JavaScript 与交付包逻辑一致；`icon-192.png`、
`icon-512.png` 是为了让本地 SW 安装测试成功而生成的**测试占位图标**，
并不是交付包中正式图标。最终源代码 ZIP 中有正式的 192/512 PNG 图标。

这些验证不证明 iPhone Safari、实际中文语音或公网 HTTPS 已通过。
