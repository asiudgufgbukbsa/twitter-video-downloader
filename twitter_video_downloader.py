#!/usr/bin/env python3
"""
Twitter/X Video Batch Downloader
Support downloading videos from share links (no login required)

Twitter/X 视频批量下载脚本
支持从分享链接下载视频 (不需要登录)
"""

import os
import re
import json
import requests
import time
import argparse
from pathlib import Path
from urllib.parse import urlparse
from typing import Optional, List, Tuple

# Default configuration
DEFAULT_OUTPUT_DIR = "./twitter_videos"
DEFAULT_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
DEFAULT_TIMEOUT = 15
DEFAULT_DOWNLOAD_TIMEOUT = 120
DEFAULT_DELAY = 0.5


class TwitterVideoDownloader:
    """Twitter/X Video Downloader Class"""

    def __init__(
        self,
        output_dir: str = DEFAULT_OUTPUT_DIR,
        user_agent: str = DEFAULT_USER_AGENT,
        timeout: int = DEFAULT_TIMEOUT,
        download_timeout: int = DEFAULT_DOWNLOAD_TIMEOUT,
        delay: float = DEFAULT_DELAY
    ):
        """
        Initialize the downloader

        Args:
            output_dir: Directory to save downloaded videos
            user_agent: User-Agent header for HTTP requests
            timeout: Request timeout in seconds
            download_timeout: Download timeout in seconds
            delay: Delay between downloads in seconds
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.timeout = timeout
        self.download_timeout = download_timeout
        self.delay = delay

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        })

    def extract_tweet_id(self, url: str) -> Optional[str]:
        """
        Extract tweet ID from URL

        Args:
            url: Tweet URL

        Returns:
            Tweet ID or None if not found
        """
        patterns = [
            r'twitter\.com/\w+/status/(\d+)',
            r'x\.com/\w+/status/(\d+)',
            r'twitter\.com/\w+/statuses/(\d+)',
            r'x\.com/\w+/statuses/(\d+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    def get_video_info_via_fxtwitter(self, tweet_id: str) -> Optional[dict]:
        """
        Get video info via fxtwitter API (third-party service)

        Args:
            tweet_id: Tweet ID

        Returns:
            Tweet data dictionary or None
        """
        api_url = f"https://api.fxtwitter.com/status/{tweet_id}"

        try:
            response = self.session.get(api_url, timeout=self.timeout)
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 200:
                    return data.get('tweet', {})
        except Exception as e:
            print(f"  FXTwitter API request failed: {e}")
            print(f"  FXTwitter API 请求失败: {e}")

        return None

    def extract_video_url(self, tweet_data: dict) -> List[Tuple[str, str, int]]:
        """
        Extract video URL from tweet data

        Args:
            tweet_data: Tweet data dictionary

        Returns:
            List of (url, quality, size) tuples
        """
        videos = []

        # fxtwitter format
        if 'media' in tweet_data:
            media = tweet_data.get('media', {})
            if isinstance(media, dict):
                for video in media.get('videos', []):
                    url = video.get('url', '')
                    if url:
                        videos.append((url, 'best', 9999999))

        return videos

    def download_video(self, url: str, output_path: str, tweet_id: str) -> bool:
        """
        Download video file

        Args:
            url: Video URL
            output_path: Local path to save video
            tweet_id: Tweet ID for logging

        Returns:
            True if successful, False otherwise
        """
        try:
            print(f"  Downloading... / 正在下载...")
            response = self.session.get(url, stream=True, timeout=self.download_timeout)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0

            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size:
                            progress = (downloaded / total_size) * 100
                            print(f"\r  Progress / 下载进度: {progress:.1f}%", end='', flush=True)

            print(f"\n  ✓ Saved to / 已保存到: {output_path}")
            return True

        except Exception as e:
            print(f"\n  ✗ Download failed / 下载失败: {e}")
            return False

    def download_from_url(self, url: str) -> Optional[str]:
        """
        Download video from a single URL

        Args:
            url: Tweet URL

        Returns:
            Output path if successful, None otherwise
        """
        tweet_id = self.extract_tweet_id(url)
        if not tweet_id:
            print(f"✗ Cannot extract tweet ID from URL / 无法从 URL 提取 tweet ID: {url}")
            return None

        print(f"\nProcessing tweet / 处理推文: {tweet_id}")

        # Get video info
        tweet_data = self.get_video_info_via_fxtwitter(tweet_id)

        if not tweet_data:
            print("  ✗ Cannot get tweet info, may be deleted or private")
            print("  ✗ 无法获取推文信息，可能推文已被删除或设为私密")
            return None

        # Extract video URL
        videos = self.extract_video_url(tweet_data)

        if not videos:
            print("  ✗ No video in this tweet / 该推文没有包含视频")
            return None

        video_url = videos[0][0]

        # Generate output filename
        output_path = self.output_dir / f"{tweet_id}.mp4"

        if output_path.exists():
            print(f"  File exists, skipping / 文件已存在，跳过")
            return str(output_path)

        # Download video
        if self.download_video(video_url, str(output_path), tweet_id):
            return str(output_path)

        return None

    def download_from_urls(self, urls: List[str]):
        """
        Batch download videos from multiple URLs

        Args:
            urls: List of tweet URLs

        Returns:
            List of download results
        """
        results = []
        total = len(urls)

        print(f"\n{'='*60}")
        print(f"Starting batch download / 开始批量下载: {total} tweets / 个推文")
        print(f"{'='*60}")

        for i, url in enumerate(urls, 1):
            print(f"\n[{i}/{total}]", end=' ')
            url = url.strip()
            if not url:
                continue

            result = self.download_from_url(url)
            results.append({
                'url': url,
                'success': result is not None,
                'file': result
            })

            # Avoid rate limiting
            if i < total:
                time.sleep(self.delay)

        # Print summary
        print(f"\n{'='*60}")
        print("Download complete! / 下载完成！汇总:")
        success_count = sum(1 for r in results if r['success'])
        print(f"  Success / 成功: {success_count}/{total}")

        failed = [r for r in results if not r['success']]
        if failed:
            print(f"  Failed / 失败: {len(failed)}")
            for r in failed:
                print(f"    - {r['url']}")

        return results


def read_urls_from_file(filepath: str) -> List[str]:
    """
    Read URL list from file

    Args:
        filepath: Path to file containing URLs (one per line)

    Returns:
        List of URLs
    """
    urls = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and ('twitter.com' in line or 'x.com' in line):
                urls.append(line)
    return urls


def main():
    parser = argparse.ArgumentParser(
        description='Twitter/X Video Batch Downloader / Twitter/X 视频批量下载工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples / 使用示例:
  # Download single video / 下载单个视频
  python twitter_video_downloader.py 'https://x.com/user/status/123456789'

  # Batch download from file / 从文件批量下载
  python twitter_video_downloader.py -f urls.txt

  # Specify output directory / 指定输出目录
  python twitter_video_downloader.py -o ./my_videos 'https://x.com/user/status/123456789'

  # Set custom delay / 设置自定义延迟
  python twitter_video_downloader.py --delay 1.0 'https://x.com/user/status/123456789'
"""
    )
    parser.add_argument('urls', nargs='*', help='Tweet URLs (can provide multiple) / 推文 URL (可以提供多个)')
    parser.add_argument('-f', '--file', help='File containing URLs (one per line) / 包含 URL 列表的文件 (每行一个)')
    parser.add_argument('-o', '--output', default=DEFAULT_OUTPUT_DIR,
                        help=f'Output directory / 输出目录 (default: {DEFAULT_OUTPUT_DIR})')
    parser.add_argument('--user-agent', default=DEFAULT_USER_AGENT,
                        help='Custom User-Agent / 自定义 User-Agent')
    parser.add_argument('--timeout', type=int, default=DEFAULT_TIMEOUT,
                        help=f'Request timeout in seconds / 请求超时秒数 (default: {DEFAULT_TIMEOUT})')
    parser.add_argument('--download-timeout', type=int, default=DEFAULT_DOWNLOAD_TIMEOUT,
                        help=f'Download timeout in seconds / 下载超时秒数 (default: {DEFAULT_DOWNLOAD_TIMEOUT})')
    parser.add_argument('--delay', type=float, default=DEFAULT_DELAY,
                        help=f'Delay between downloads in seconds / 下载间隔秒数 (default: {DEFAULT_DELAY})')

    args = parser.parse_args()

    # Collect all URLs
    urls = list(args.urls)

    if args.file:
        file_urls = read_urls_from_file(args.file)
        urls.extend(file_urls)

    if not urls:
        print("Please provide at least one tweet URL or use -f to specify a URL file")
        print("请提供至少一个推文 URL 或使用 -f 指定 URL 文件")
        print("\nUse --help for more information / 使用 --help 查看更多信息")
        return

    # Create downloader and start downloading
    downloader = TwitterVideoDownloader(
        output_dir=args.output,
        user_agent=args.user_agent,
        timeout=args.timeout,
        download_timeout=args.download_timeout,
        delay=args.delay
    )
    downloader.download_from_urls(urls)


if __name__ == '__main__':
    main()
