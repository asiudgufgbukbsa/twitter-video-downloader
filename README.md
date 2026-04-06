# Twitter/X Video Downloader 🎬

[中文文档](#中文文档) | [English](#english)

---

<a name="english"></a>
## English

A set of Python scripts for downloading videos from Twitter/X. Supports both direct URL downloads and bookmark batch downloads.

### Features ✨

- **Video Downloader**: Download videos from Twitter/X URLs without login
- **Bookmark Downloader**: Batch download all videos from your Twitter/X bookmarks
- **Cross-platform**: Works on Windows, macOS, and Linux
- **Browser Integration**: Uses your existing Chrome/Edge login session
- **Resume Support**: Remembers downloaded videos to avoid duplicates
- **Configurable**: Extensive command-line options for customization
- **Bilingual**: Full English and Chinese output messages

### Installation 📦

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/twitter-video-downloader.git
   cd twitter-video-downloader
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Playwright browsers** (required for bookmark downloader)
   ```bash
   python -m playwright install chromium
   ```

### Usage 🚀

#### Video Downloader (No Login Required)

Download videos from Twitter/X URLs without needing to log in.

```bash
# Download a single video
python twitter_video_downloader.py 'https://x.com/user/status/123456789'

# Download multiple videos
python twitter_video_downloader.py 'https://x.com/user1/status/111' 'https://x.com/user2/status/222'

# Batch download from a file (one URL per line)
python twitter_video_downloader.py -f urls.txt

# Specify output directory
python twitter_video_downloader.py -o ./my_videos 'https://x.com/user/status/123456789'

# Set custom delay between downloads
python twitter_video_downloader.py --delay 1.0 'https://x.com/user/status/123456789'
```

**Options:**
| Option | Description | Default |
|--------|-------------|---------|
| `urls` | Tweet URLs (space-separated) | - |
| `-f, --file` | File containing URLs (one per line) | - |
| `-o, --output` | Output directory | `./twitter_videos` |
| `--user-agent` | Custom User-Agent | Chrome 120 |
| `--timeout` | Request timeout (seconds) | 15 |
| `--download-timeout` | Download timeout (seconds) | 120 |
| `--delay` | Delay between downloads (seconds) | 0.5 |

#### Bookmark Downloader (Login Required)

Batch download videos from your Twitter/X bookmarks.

```bash
# Download all bookmark videos (interactive mode)
python twitter_bookmark_downloader.py

# Specify output directory
python twitter_bookmark_downloader.py -o ./my_bookmarks

# Limit number of tweets to process
python twitter_bookmark_downloader.py -n 100

# Limit scroll count
python twitter_bookmark_downloader.py -s 50

# Use headless mode (no visible browser window)
python twitter_bookmark_downloader.py --headless

# Use specific browser
python twitter_bookmark_downloader.py --browser chrome
python twitter_bookmark_downloader.py --browser edge

# Set maximum video file size (MB)
python twitter_bookmark_downloader.py --max-size 500
```

**Options:**
| Option | Description | Default |
|--------|-------------|---------|
| `-o, --output` | Output directory | `./twitter_videos` |
| `-p, --profile` | Browser profile directory | `./browser_profile` |
| `-n, --max-tweets` | Maximum tweets to process | unlimited |
| `-s, --max-scrolls` | Maximum scroll count | unlimited |
| `--headless` | Run in headless mode | `False` |
| `--max-size` | Maximum video size (MB) | 1500 |
| `--locale` | Browser locale | `en-US` |
| `--delay` | Delay between downloads (seconds) | 0.5 |
| `--no-system-browser` | Use built-in Chromium | `False` |
| `--browser` | Browser type (chrome/edge/auto) | `auto` |

### How It Works 🔧

#### Video Downloader
Uses the [FXTwitter](https://github.com/FixTweet/FixTweet) API to fetch video information without requiring login. Simply provide tweet URLs and the script will download the videos.

#### Bookmark Downloader
1. Launches a browser using your existing Chrome/Edge profile or creates a new profile
2. Navigates to your Twitter/X bookmarks page
3. Scrolls through and collects all tweet links
4. Uses FXTwitter API to check for videos in each tweet
5. Downloads videos that haven't been downloaded before

### Requirements 📋

- Python 3.8+
- Chrome, Edge, or Chromium browser (for bookmark downloader)
- Network access to Twitter/X and FXTwitter API

### Privacy & Security 🔒

- **No credentials stored**: The scripts don't store any passwords
- **Browser profile**: `browser_profile/` contains your login session - add to `.gitignore`
- **Download history**: `.downloaded.json` tracks downloaded videos - add to `.gitignore`
- **API usage**: Uses public FXTwitter API - no rate limit issues typically

### Troubleshooting 🔧

**"Cannot extract tweet ID"**
- Make sure the URL format is correct (e.g., `https://x.com/user/status/123456789`)

**"Cannot get tweet info"**
- The tweet may be deleted or private
- Video may not be available

**Browser won't start**
- Close all Chrome/Edge windows before running the bookmark downloader
- Try `--no-system-browser` flag to use built-in Chromium

**"Access failed" / Timeout**
- Check your VPN/proxy settings
- Twitter/X may be blocked in your region

### License 📄

MIT License - Feel free to use, modify, and distribute.

---

<a name="中文文档"></a>
## 中文文档

一套用于从 Twitter/X 下载视频的 Python 脚本。支持直接 URL 下载和书签批量下载。

### 功能特点 ✨

- **视频下载器**：无需登录即可从 Twitter/X URL 下载视频
- **书签下载器**：批量下载你 Twitter/X 书签中的所有视频
- **跨平台**：支持 Windows、macOS 和 Linux
- **浏览器集成**：使用你现有的 Chrome/Edge 登录会话
- **断点续传**：记住已下载的视频，避免重复下载
- **可配置**：丰富的命令行选项供自定义
- **双语支持**：完整的中英文输出信息

### 安装 📦

1. **克隆仓库**
   ```bash
   git clone https://github.com/YOUR_USERNAME/twitter-video-downloader.git
   cd twitter-video-downloader
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **安装 Playwright 浏览器**（书签下载器需要）
   ```bash
   python -m playwright install chromium
   ```

### 使用方法 🚀

#### 视频下载器（无需登录）

无需登录即可从 Twitter/X URL 下载视频。

```bash
# 下载单个视频
python twitter_video_downloader.py 'https://x.com/user/status/123456789'

# 下载多个视频
python twitter_video_downloader.py 'https://x.com/user1/status/111' 'https://x.com/user2/status/222'

# 从文件批量下载（每行一个 URL）
python twitter_video_downloader.py -f urls.txt

# 指定输出目录
python twitter_video_downloader.py -o ./my_videos 'https://x.com/user/status/123456789'

# 设置下载间隔
python twitter_video_downloader.py --delay 1.0 'https://x.com/user/status/123456789'
```

**参数说明：**
| 参数 | 说明 | 默认值 |
|------|------|--------|
| `urls` | 推文 URL（空格分隔） | - |
| `-f, --file` | 包含 URL 的文件（每行一个） | - |
| `-o, --output` | 输出目录 | `./twitter_videos` |
| `--user-agent` | 自定义 User-Agent | Chrome 120 |
| `--timeout` | 请求超时时间（秒） | 15 |
| `--download-timeout` | 下载超时时间（秒） | 120 |
| `--delay` | 下载间隔（秒） | 0.5 |

#### 书签下载器（需要登录）

批量下载你 Twitter/X 书签中的视频。

```bash
# 下载所有书签视频（交互模式）
python twitter_bookmark_downloader.py

# 指定输出目录
python twitter_bookmark_downloader.py -o ./my_bookmarks

# 限制处理的推文数量
python twitter_bookmark_downloader.py -n 100

# 限制滚动次数
python twitter_bookmark_downloader.py -s 50

# 使用无头模式（无可见浏览器窗口）
python twitter_bookmark_downloader.py --headless

# 使用特定浏览器
python twitter_bookmark_downloader.py --browser chrome
python twitter_bookmark_downloader.py --browser edge

# 设置最大视频文件大小（MB）
python twitter_bookmark_downloader.py --max-size 500
```

**参数说明：**
| 参数 | 说明 | 默认值 |
|------|------|--------|
| `-o, --output` | 输出目录 | `./twitter_videos` |
| `-p, --profile` | 浏览器配置目录 | `./browser_profile` |
| `-n, --max-tweets` | 最大处理推文数 | 无限制 |
| `-s, --max-scrolls` | 最大滚动次数 | 无限制 |
| `--headless` | 无头模式运行 | `False` |
| `--max-size` | 最大视频大小（MB） | 1500 |
| `--locale` | 浏览器语言 | `en-US` |
| `--delay` | 下载间隔（秒） | 0.5 |
| `--no-system-browser` | 使用内置 Chromium | `False` |
| `--browser` | 浏览器类型（chrome/edge/auto） | `auto` |

### 工作原理 🔧

#### 视频下载器
使用 [FXTwitter](https://github.com/FixTweet/FixTweet) API 获取视频信息，无需登录。只需提供推文 URL 即可下载视频。

#### 书签下载器
1. 使用你现有的 Chrome/Edge 配置启动浏览器，或创建新配置
2. 导航到你的 Twitter/X 书签页面
3. 滚动并收集所有推文链接
4. 使用 FXTwitter API 检查每条推文是否包含视频
5. 下载尚未下载过的视频

### 系统要求 📋

- Python 3.8+
- Chrome、Edge 或 Chromium 浏览器（书签下载器需要）
- 可访问 Twitter/X 和 FXTwitter API 的网络

### 隐私与安全 🔒

- **不存储凭证**：脚本不会存储任何密码
- **浏览器配置**：`browser_profile/` 包含你的登录会话 - 请添加到 `.gitignore`
- **下载历史**：`.downloaded.json` 记录已下载视频 - 请添加到 `.gitignore`
- **API 使用**：使用公开的 FXTwitter API - 通常不会有速率限制问题

### 常见问题 🔧

**"无法提取 tweet ID"**
- 确保 URL 格式正确（例如 `https://x.com/user/status/123456789`）

**"无法获取推文信息"**
- 推文可能已被删除或设为私密
- 视频可能不可用

**浏览器无法启动**
- 运行书签下载器前请关闭所有 Chrome/Edge 窗口
- 尝试使用 `--no-system-browser` 标志来使用内置 Chromium

**"访问失败" / 超时**
- 检查你的 VPN/代理设置
- Twitter/X 可能在你所在地区被屏蔽

### 许可证 📄

MIT 许可证 - 欢迎自由使用、修改和分发。

---

### Contributing 🤝

Contributions are welcome! Please feel free to submit a Pull Request.

欢迎贡献代码！请随时提交 Pull Request。

### Star History ⭐

If this project helps you, please consider giving it a star!

如果这个项目对你有帮助，请考虑给它一个星标！
