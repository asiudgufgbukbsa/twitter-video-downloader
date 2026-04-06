# Twitter/X Video Downloader 🎬

[中文文档](#中文文档) | [English](#english)

---

<a name="english"></a>
## English

A beautiful, user-friendly Twitter/X video downloader with GUI. Download videos from URLs or your bookmarks with just a few clicks!

![GUI Preview](https://via.placeholder.com/800x500?text=Beautiful+GUI+Preview)

### ✨ Features

- **🎨 Beautiful GUI** - Warm, cute design with Chinese/English support
- **📹 Video Downloader** - Download from URLs without login
- **🔖 Bookmark Downloader** - Batch download all your bookmarked videos
- **🌐 Bilingual** - One-click language toggle (EN/中文)
- **📱 Scrollable UI** - Works perfectly on any screen size
- **🚀 Easy to Use** - Just double-click to start!

### 🚀 Quick Start

**Windows:**
1. Install [Python 3.8+](https://www.python.org/downloads/) (check "Add Python to PATH")
2. Double-click `start.bat`
3. Done! Dependencies auto-install on first run.

**macOS/Linux:**
```bash
chmod +x start.sh && ./start.sh
```

### 📖 How to Use

#### Video Download Tab
1. Paste tweet URLs (one per line)
2. Click "Start Download"
3. Videos saved to `twitter_videos/` folder

#### Bookmark Download Tab
1. Click "Start Download" - browser opens automatically
2. Login to Twitter if needed
3. All bookmarked videos download automatically!

### 🔧 Advanced Usage

<details>
<summary>Command Line Options (click to expand)</summary>

```bash
# Download single video
python twitter_video_downloader.py 'https://x.com/user/status/123456789'

# Download multiple
python twitter_video_downloader.py 'url1' 'url2'

# From file
python twitter_video_downloader.py -f urls.txt

# Bookmark downloader
python twitter_bookmark_downloader.py -n 100  # limit to 100 tweets
```

</details>

### ❓ FAQ

**Q: "Python not found" error?**
A: Reinstall Python and check "Add Python to PATH"

**Q: Browser won't start?**
A: Close all Chrome/Edge windows before running

**Q: Can't access Twitter?**
A: Make sure your VPN is working

### 📄 License

MIT License - Free to use, modify, and distribute.

---

<a name="中文文档"></a>
## 中文文档

一个美观、易用的 Twitter/X 视频下载器，支持图形界面。只需点击几下即可下载视频或书签！

### ✨ 功能特点

- **🎨 精美界面** - 温暖可爱的米色主题，支持中英文切换
- **📹 视频下载** - 无需登录，粘贴链接即可下载
- **🔖 书签下载** - 一键下载所有收藏书签视频
- **🌐 双语支持** - 点击右上角切换中英文
- **📱 自适应界面** - 支持滚动，适合各种屏幕
- **🚀 简单易用** - 双击即可启动！

### 🚀 快速开始

**Windows 用户：**
1. 安装 [Python 3.8+](https://www.python.org/downloads/)（安装时勾选 "Add Python to PATH"）
2. 双击 `start.bat`
3. 完成！首次运行会自动安装依赖

**macOS/Linux 用户：**
```bash
chmod +x start.sh && ./start.sh
```

### 📖 使用方法

#### 视频下载
1. 粘贴推文链接（每行一个）
2. 点击「开始下载」
3. 视频保存到 `twitter_videos/` 文件夹

#### 书签下载
1. 点击「开始下载」- 浏览器自动打开
2. 如未登录，在浏览器中登录即可
3. 所有书签视频自动下载！

### ❓ 常见问题

**Q: 提示找不到 Python？**
A: 重装 Python 时勾选 "Add Python to PATH"

**Q: 浏览器启动失败？**
A: 运行前先关闭所有 Chrome/Edge 窗口

**Q: 无法访问 Twitter？**
A: 确保你的 VPN 正常工作

### 📄 许可证

MIT 许可证 - 免费使用、修改和分发。

---

### ⭐ Star History

如果这个项目对你有帮助，请给个 Star ⭐

如果这个项目对你有帮助，请考虑给它一个星标！⭐
