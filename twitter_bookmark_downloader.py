#!/usr/bin/env python3
"""
Twitter/X Bookmark Video Batch Downloader
Downloads videos from your Twitter/X bookmarks using logged-in browser data

Twitter/X 书签视频批量下载脚本
使用已登录的 Chrome/Edge 浏览器数据下载书签中的视频
"""

import os
import re
import json
import asyncio
import time
import requests
import argparse
import platform
from pathlib import Path
from typing import List, Optional, Set
from urllib.parse import urlparse

try:
    from playwright.async_api import async_playwright, Page, Browser
except ImportError:
    print("Please install playwright first / 请先安装 playwright:")
    print("  pip install playwright")
    print("  python -m playwright install chromium")
    exit(1)


# Default configuration
DEFAULT_OUTPUT_DIR = "./twitter_videos"
DEFAULT_BROWSER_PROFILE = "./browser_profile"
DEFAULT_MAX_TWEETS = 999999
DEFAULT_MAX_SCROLLS = 999999
DEFAULT_MAX_SIZE_MB = 1500
DEFAULT_LOCALE = 'en-US'
DEFAULT_HEADLESS = False
DEFAULT_DOWNLOAD_DELAY = 0.5


def get_chrome_user_data_dir():
    """Get Chrome user data directory based on OS / 获取 Chrome 用户数据目录"""
    system = platform.system()
    if system == 'Windows':
        return os.path.expandvars(r'%LOCALAPPDATA%\Google\Chrome\User Data')
    elif system == 'Darwin':  # macOS
        return os.path.expanduser('~/Library/Application Support/Google/Chrome')
    else:  # Linux
        return os.path.expanduser('~/.config/google-chrome')


def get_edge_user_data_dir():
    """Get Edge user data directory based on OS / 获取 Edge 用户数据目录"""
    system = platform.system()
    if system == 'Windows':
        return os.path.expandvars(r'%LOCALAPPDATA%\Microsoft\Edge\User Data')
    elif system == 'Darwin':
        return os.path.expanduser('~/Library/Application Support/Microsoft Edge')
    else:
        return os.path.expanduser('~/.config/microsoft-edge')


def get_chrome_executable_path() -> Optional[str]:
    """Get Chrome executable path based on OS / 获取 Chrome 可执行文件路径"""
    system = platform.system()
    paths = []

    if system == 'Windows':
        paths = [
            os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        ]
    elif system == 'Darwin':  # macOS
        paths = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        ]
    else:  # Linux
        paths = [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
            "/usr/bin/chromium",
            "/usr/bin/chromium-browser",
            "/snap/bin/chromium",
        ]

    for path in paths:
        if os.path.exists(path):
            return path
    return None


def get_edge_executable_path() -> Optional[str]:
    """Get Edge executable path based on OS / 获取 Edge 可执行文件路径"""
    system = platform.system()
    paths = []

    if system == 'Windows':
        paths = [
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Edge\Application\msedge.exe"),
        ]
    elif system == 'Darwin':  # macOS
        paths = [
            "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        ]
    else:  # Linux
        paths = [
            "/usr/bin/microsoft-edge",
            "/usr/bin/microsoft-edge-stable",
            "/snap/bin/microsoft-edge",
        ]

    for path in paths:
        if os.path.exists(path):
            return path
    return None


class TwitterBookmarkDownloader:
    """Twitter/X Bookmark Video Downloader Class"""

    def __init__(
        self,
        output_dir: str = DEFAULT_OUTPUT_DIR,
        browser_profile: str = DEFAULT_BROWSER_PROFILE,
        headless: bool = DEFAULT_HEADLESS,
        max_size_mb: float = DEFAULT_MAX_SIZE_MB,
        locale: str = DEFAULT_LOCALE,
        download_delay: float = DEFAULT_DOWNLOAD_DELAY,
        use_system_browser: bool = True,
        browser_type: str = 'auto'
    ):
        """
        Initialize the bookmark downloader

        Args:
            output_dir: Directory to save downloaded videos
            browser_profile: Directory for browser profile data
            headless: Run browser in headless mode
            max_size_mb: Maximum video file size in MB
            locale: Browser locale setting
            download_delay: Delay between downloads in seconds
            use_system_browser: Use installed Chrome/Edge if available
            browser_type: Browser type to use ('chrome', 'edge', 'auto')
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.browser_profile = browser_profile
        self.headless = headless
        self.max_size_mb = max_size_mb
        self.locale = locale
        self.download_delay = download_delay
        self.use_system_browser = use_system_browser
        self.browser_type = browser_type
        self.downloaded_ids: Set[str] = set()

        # Load download history
        self.record_file = self.output_dir / ".downloaded.json"
        self._load_record()

    def _load_record(self):
        """Load downloaded tweet records / 加载已下载的推文记录"""
        if self.record_file.exists():
            try:
                with open(self.record_file, 'r', encoding='utf-8') as f:
                    self.downloaded_ids = set(json.load(f))
                print(f"Loaded download history / 已加载下载记录: {len(self.downloaded_ids)} tweets / 个")
            except:
                pass

    def _save_record(self):
        """Save download records / 保存下载记录"""
        with open(self.record_file, 'w', encoding='utf-8') as f:
            json.dump(list(self.downloaded_ids), f)

    def extract_tweet_id(self, url: str) -> Optional[str]:
        """Extract tweet ID from URL / 从 URL 提取 tweet ID"""
        patterns = [
            r'twitter\.com/\w+/status/(\d+)',
            r'x\.com/\w+/status/(\d+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    async def get_video_url_via_api(self, tweet_id: str) -> Optional[str]:
        """Get video URL via FXTwitter API / 通过 FXTwitter API 获取视频 URL"""
        api_url = f"https://api.fxtwitter.com/status/{tweet_id}"

        try:
            response = requests.get(api_url, timeout=15)
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 200:
                    tweet = data.get('tweet', {})
                    media = tweet.get('media', {})
                    if isinstance(media, dict):
                        videos = media.get('videos', [])
                        if videos:
                            return videos[0].get('url')
        except Exception as e:
            print(f"    API request failed / API 请求失败: {e}")

        return None

    async def download_video(self, video_url: str, tweet_id: str) -> bool:
        """Download video file / 下载视频文件"""
        output_path = self.output_dir / f"{tweet_id}.mp4"

        if output_path.exists():
            print(f"   ✅ 已经下载过了，跳过")
            return True

        try:
            print(f"   📥 正在获取视频信息...")
            # Send HEAD request first to get file size
            head_response = requests.head(video_url, timeout=30, allow_redirects=True)
            total_size = int(head_response.headers.get('content-length', 0))
            total_size_mb = total_size / (1024 * 1024)

            # Check file size
            if total_size > 0 and total_size_mb > self.max_size_mb:
                print(f"   ⏭️ 文件太大 ({total_size_mb:.1f}MB > {self.max_size_mb}MB)，跳过")
                return False

            size_info = f" ({total_size_mb:.1f}MB)" if total_size > 0 else ""
            print(f"   📥 正在下载{size_info}...")
            response = requests.get(video_url, stream=True, timeout=120)
            response.raise_for_status()

            if total_size == 0:
                total_size = int(response.headers.get('content-length', 0))

            downloaded = 0

            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size:
                            progress = (downloaded / total_size) * 100
                            print(f"\r   📊 进度: {progress:.0f}%", end='', flush=True)

            print(f"\n   ✅ 下载完成！保存为: {output_path.name}")
            self.downloaded_ids.add(tweet_id)
            return True

        except Exception as e:
            print(f"\n   ❌ 下载失败: {e}")
            return False

    async def scroll_and_collect_bookmarks(
        self,
        page: Page,
        max_tweets: int = DEFAULT_MAX_TWEETS,
        max_scrolls: int = DEFAULT_MAX_SCROLLS
    ) -> List[str]:
        """Scroll bookmark page and collect tweet links / 滚动书签页面并收集推文链接"""
        tweet_urls = []  # Use list to maintain order
        tweet_ids_seen = set()  # For deduplication
        scroll_count = 0
        no_new_count = 0

        print(f"\n📖 正在扫描你的书签...")
        print(f"   （最多 {max_tweets} 条，最多滚动 {max_scrolls} 次）")
        print()

        while scroll_count < max_scrolls and len(tweet_urls) < max_tweets:
            await asyncio.sleep(2)

            links = await page.locator('a[href*="/status/"]').all()

            prev_count = len(tweet_urls)

            for link in links:
                try:
                    href = await link.get_attribute('href')
                    if href and '/status/' in href:
                        if href.startswith('/'):
                            href = f"https://x.com{href}"
                        tweet_id = self.extract_tweet_id(href)
                        if tweet_id and tweet_id not in tweet_ids_seen:
                            tweet_ids_seen.add(tweet_id)
                            tweet_urls.append(href)
                except:
                    continue

            current_count = len(tweet_urls)
            print(f"   📋 已找到 {current_count} 条推文（第 {scroll_count + 1} 次滚动）")

            if current_count == prev_count:
                no_new_count += 1
                if no_new_count >= 3:
                    print(f"\n   ✓ 没有更多了，停止扫描")
                    break
            else:
                no_new_count = 0

            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            scroll_count += 1
            await asyncio.sleep(1.5)

        print(f"\n✓ 扫描完成！共找到 {len(tweet_urls)} 条书签推文")
        return tweet_urls

    async def run(
        self,
        max_tweets: int = DEFAULT_MAX_TWEETS,
        max_scrolls: int = DEFAULT_MAX_SCROLLS
    ):
        """Main run function / 主运行函数"""
        print(f"\n{'─'*50}")
        print("🔖 书签视频下载器")
        print(f"{'─'*50}")
        print(f"📁 保存位置: {self.output_dir.absolute()}")
        print(f"🌐 浏览器: {self.browser_type}")
        print()

        async with async_playwright() as p:
            print("🚀 正在启动浏览器...")

            executable_path = None
            browser_found = False

            if self.use_system_browser:
                # Auto-detect or use specified browser
                if self.browser_type in ['chrome', 'auto']:
                    chrome_path = get_chrome_executable_path()
                    if chrome_path:
                        executable_path = chrome_path
                        print(f"   找到 Chrome")
                        browser_found = True

                if not browser_found and self.browser_type in ['edge', 'auto']:
                    edge_path = get_edge_executable_path()
                    if edge_path:
                        executable_path = edge_path
                        print(f"   找到 Edge")
                        browser_found = True

            # Launch browser
            if not executable_path:
                print("   使用内置 Chromium")
                print("   如果需要登录，请在浏览器窗口中登录")

            try:
                launch_options = {
                    'user_data_dir': self.browser_profile,
                    'headless': self.headless,
                    'viewport': {'width': 1280, 'height': 900},
                    'locale': self.locale,
                    'args': ['--disable-blink-features=AutomationControlled']
                }
                if executable_path:
                    launch_options['executable_path'] = executable_path

                context = await p.chromium.launch_persistent_context(**launch_options)
            except Exception as e:
                print(f"❌ 启动失败: {e}")
                print("   尝试使用默认 Chromium...")
                context = await p.chromium.launch_persistent_context(
                    user_data_dir=self.browser_profile,
                    headless=self.headless,
                    viewport={'width': 1280, 'height': 900},
                    locale=self.locale,
                )

            page = context.pages[0] if context.pages else await context.new_page()

            # Visit bookmark page
            print("\n📖 正在打开书签页面...")
            print("   （如果超时，请检查网络/VPN）")

            try:
                await page.goto('https://x.com/i/bookmarks', wait_until='domcontentloaded', timeout=120000)
            except Exception as e:
                print(f"\n❌ 访问失败: {e}")
                print("\n可能的原因:")
                print("   1. 没开 VPN")
                print("   2. 网络问题")
                print("   3. Twitter 访问受限")
                print("\n请检查网络后重试")
                await context.close()
                return

            await asyncio.sleep(5)

            # Check if login is required
            current_url = page.url
            page_content = await page.content()

            if 'login' in current_url or 'Log in' in page_content or await page.locator('input[name="text"]').count() > 0:
                print(f"\n{'─'*50}")
                print("⚠️ 需要登录 Twitter！")
                print("   请在弹出的浏览器窗口中登录")
                print("   登录完成后，回到这里按回车继续...")
                print(f"{'─'*50}")
                input()

                await page.goto('https://x.com/i/bookmarks', wait_until='domcontentloaded', timeout=120000)
                await asyncio.sleep(3)

            # Collect bookmark tweets
            tweet_urls = await self.scroll_and_collect_bookmarks(
                page,
                max_tweets=max_tweets,
                max_scrolls=max_scrolls
            )

            if not tweet_urls:
                print("\n❌ 没有找到任何书签推文")
                await context.close()
                return

            # Process each tweet
            print(f"\n{'─'*50}")
            print(f"🔍 开始检查 {len(tweet_urls)} 条推文...")
            print(f"{'─'*50}")
            success_count = 0
            video_count = 0

            for i, url in enumerate(tweet_urls, 1):
                tweet_id = self.extract_tweet_id(url)
                print(f"\n【{i}/{len(tweet_urls)}】检查推文 {tweet_id}")

                if tweet_id in self.downloaded_ids:
                    print("   ⏭️ 之前下载过，跳过")
                    continue

                video_url = await self.get_video_url_via_api(tweet_id)

                if video_url:
                    video_count += 1
                    print("   🎬 找到视频")
                    if await self.download_video(video_url, tweet_id):
                        success_count += 1
                        self._save_record()
                else:
                    print("   📷 没有视频")

                await asyncio.sleep(self.download_delay)

            # Summary
            print(f"\n{'─'*50}")
            print("🎉 下载完成！")
            print(f"{'─'*50}")
            print(f"   📊 统计信息:")
            print(f"      扫描推文: {len(tweet_urls)} 条")
            print(f"      包含视频: {video_count} 个")
            print(f"      成功下载: {success_count} 个")
            print(f"   📁 保存位置: {self.output_dir.absolute()}")
            print(f"{'─'*50}\n")

            await context.close()


async def main():
    parser = argparse.ArgumentParser(
        description='Twitter/X Bookmark Video Batch Downloader / Twitter/X 书签视频批量下载工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples / 使用示例:
  # Download all bookmark videos / 下载所有书签视频
  python twitter_bookmark_downloader.py

  # Specify output directory / 指定输出目录
  python twitter_bookmark_downloader.py -o ./my_videos

  # Limit number of tweets / 限制推文数量
  python twitter_bookmark_downloader.py -n 100

  # Use headless mode / 使用无头模式
  python twitter_bookmark_downloader.py --headless

  # Use specific browser / 使用特定浏览器
  python twitter_bookmark_downloader.py --browser chrome
  python twitter_bookmark_downloader.py --browser edge
"""
    )
    parser.add_argument('-o', '--output', default=DEFAULT_OUTPUT_DIR,
                        help=f'Output directory / 输出目录 (default: {DEFAULT_OUTPUT_DIR})')
    parser.add_argument('-p', '--profile', default=DEFAULT_BROWSER_PROFILE,
                        help=f'Browser profile directory / 浏览器配置目录 (default: {DEFAULT_BROWSER_PROFILE})')
    parser.add_argument('-n', '--max-tweets', type=int, default=DEFAULT_MAX_TWEETS,
                        help=f'Max tweets to process / 最大处理推文数 (default: unlimited / 无限制)')
    parser.add_argument('-s', '--max-scrolls', type=int, default=DEFAULT_MAX_SCROLLS,
                        help=f'Max scroll count / 最大滚动次数 (default: unlimited / 无限制)')
    parser.add_argument('--headless', action='store_true', default=DEFAULT_HEADLESS,
                        help='Run in headless mode / 无头模式运行')
    parser.add_argument('--max-size', type=float, default=DEFAULT_MAX_SIZE_MB,
                        help=f'Max video size in MB / 最大视频大小MB (default: {DEFAULT_MAX_SIZE_MB})')
    parser.add_argument('--locale', default=DEFAULT_LOCALE,
                        help=f'Browser locale / 浏览器语言设置 (default: {DEFAULT_LOCALE})')
    parser.add_argument('--delay', type=float, default=DEFAULT_DOWNLOAD_DELAY,
                        help=f'Delay between downloads / 下载间隔秒数 (default: {DEFAULT_DOWNLOAD_DELAY})')
    parser.add_argument('--no-system-browser', action='store_true',
                        help='Do not use installed Chrome/Edge, use built-in Chromium / 不使用已安装的浏览器')
    parser.add_argument('--browser', choices=['chrome', 'edge', 'auto'], default='auto',
                        help='Browser type to use / 使用的浏览器类型 (default: auto)')

    args = parser.parse_args()

    downloader = TwitterBookmarkDownloader(
        output_dir=args.output,
        browser_profile=args.profile,
        headless=args.headless,
        max_size_mb=args.max_size,
        locale=args.locale,
        download_delay=args.delay,
        use_system_browser=not args.no_system_browser,
        browser_type=args.browser
    )

    await downloader.run(
        max_tweets=args.max_tweets,
        max_scrolls=args.max_scrolls
    )


if __name__ == '__main__':
    asyncio.run(main())
