#!/usr/bin/env python3
"""
Twitter/X Video Downloader GUI
A graphical user interface for Twitter/X video and bookmark downloading

Twitter/X 视频下载器图形界面
用于下载 Twitter/X 视频和书签的图形用户界面
"""

import os
import sys
import threading
import asyncio
import queue
import webbrowser
from pathlib import Path
from typing import Optional, List
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

# Import downloader classes
try:
    from twitter_video_downloader import TwitterVideoDownloader, read_urls_from_file
except ImportError:
    print("Error: Cannot import twitter_video_downloader.py")
    print("错误: 无法导入 twitter_video_downloader.py")
    sys.exit(1)

try:
    from twitter_bookmark_downloader import TwitterBookmarkDownloader
except ImportError:
    print("Error: Cannot import twitter_bookmark_downloader.py")
    print("错误: 无法导入 twitter_bookmark_downloader.py")
    sys.exit(1)


class TextRedirector:
    """Redirect stdout/stderr to a tkinter text widget / 将标准输出重定向到 tkinter 文本控件"""

    def __init__(self, text_widget, queue_obj):
        self.text_widget = text_widget
        self.queue = queue_obj

    def write(self, string):
        self.queue.put(string)

    def flush(self):
        pass


class TwitterDownloaderGUI:
    """Main GUI Application / 主图形界面应用"""

    def __init__(self, root):
        self.root = root
        self.root.title("Twitter/X Video Downloader / Twitter/X 视频下载器")
        self.root.geometry("800x700")
        self.root.minsize(700, 600)

        # Output queue for log messages / 日志消息输出队列
        self.log_queue = queue.Queue()

        # Download state / 下载状态
        self.is_downloading = False
        self.download_thread = None

        # Default settings / 默认设置
        self.default_output_dir = str(Path.cwd() / "twitter_videos")

        # Setup UI / 设置界面
        self.setup_ui()

        # Start log update loop / 开始日志更新循环
        self.update_log_display()

    def setup_ui(self):
        """Setup the main user interface / 设置主用户界面"""

        # Create notebook for tabs / 创建标签页笔记本
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Video Downloader Tab / 视频下载标签页
        self.video_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.video_frame, text="  Video Download / 视频下载  ")
        self.setup_video_tab()

        # Bookmark Downloader Tab / 书签下载标签页
        self.bookmark_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.bookmark_frame, text="  Bookmark Download / 书签下载  ")
        self.setup_bookmark_tab()

        # Bottom controls / 底部控件
        self.setup_bottom_controls()

    def setup_video_tab(self):
        """Setup video downloader tab / 设置视频下载标签页"""

        # Main container with padding / 带内边距的主容器
        main_frame = ttk.Frame(self.video_frame, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # URL input section / URL 输入区域
        url_frame = ttk.LabelFrame(main_frame, text="Tweet URLs / 推文链接", padding="10")
        url_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        ttk.Label(url_frame, text="Enter URLs (one per line) / 输入链接（每行一个）:").pack(anchor=tk.W)

        self.url_text = scrolledtext.ScrolledText(url_frame, height=8, wrap=tk.WORD)
        self.url_text.pack(fill=tk.BOTH, expand=True, pady=5)

        # URL file selection / URL 文件选择
        file_frame = ttk.Frame(url_frame)
        file_frame.pack(fill=tk.X, pady=5)

        ttk.Label(file_frame, text="Or load from file / 或从文件加载:").pack(side=tk.LEFT)
        ttk.Button(file_frame, text="Browse / 浏览...", command=self.load_urls_from_file).pack(side=tk.LEFT, padx=10)

        self.url_file_label = ttk.Label(file_frame, text="", foreground="gray")
        self.url_file_label.pack(side=tk.LEFT)

        # Settings section / 设置区域
        settings_frame = ttk.LabelFrame(main_frame, text="Settings / 设置", padding="10")
        settings_frame.pack(fill=tk.X, pady=(0, 10))

        # Output directory / 输出目录
        dir_frame = ttk.Frame(settings_frame)
        dir_frame.pack(fill=tk.X, pady=5)

        ttk.Label(dir_frame, text="Output Directory / 输出目录:").pack(side=tk.LEFT)
        self.video_output_var = tk.StringVar(value=self.default_output_dir)
        ttk.Entry(dir_frame, textvariable=self.video_output_var, width=40).pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        ttk.Button(dir_frame, text="Browse / 浏览...", command=lambda: self.browse_directory(self.video_output_var)).pack(side=tk.LEFT)

        # Delay setting / 延迟设置
        delay_frame = ttk.Frame(settings_frame)
        delay_frame.pack(fill=tk.X, pady=5)

        ttk.Label(delay_frame, text="Delay between downloads (sec) / 下载间隔（秒）:").pack(side=tk.LEFT)
        self.video_delay_var = tk.StringVar(value="0.5")
        ttk.Entry(delay_frame, textvariable=self.video_delay_var, width=10).pack(side=tk.LEFT, padx=10)

        # Start button / 开始按钮
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)

        self.video_start_btn = ttk.Button(btn_frame, text="Start Download / 开始下载", command=self.start_video_download)
        self.video_start_btn.pack(side=tk.LEFT, padx=5)

        self.video_stop_btn = ttk.Button(btn_frame, text="Stop / 停止", command=self.stop_download, state=tk.DISABLED)
        self.video_stop_btn.pack(side=tk.LEFT, padx=5)

    def setup_bookmark_tab(self):
        """Setup bookmark downloader tab / 设置书签下载标签页"""

        # Main container with padding / 带内边距的主容器
        main_frame = ttk.Frame(self.bookmark_frame, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Info section / 信息区域
        info_frame = ttk.LabelFrame(main_frame, text="Instructions / 使用说明", padding="10")
        info_frame.pack(fill=tk.X, pady=(0, 10))

        info_text = """This tool downloads videos from your Twitter/X bookmarks.
此工具从你的 Twitter/X 书签中下载视频。

1. Make sure you are logged into Twitter/X in Chrome or Edge
   确保你已在 Chrome 或 Edge 浏览器中登录 Twitter/X
2. Close all Chrome/Edge windows before starting
   开始前请关闭所有 Chrome/Edge 窗口
3. Click 'Start Download' and wait for the browser to open
   点击"开始下载"，等待浏览器打开
4. If not logged in, login in the browser window and press Enter
   如果未登录，在浏览器窗口中登录后按回车"""

        ttk.Label(info_frame, text=info_text, justify=tk.LEFT).pack(anchor=tk.W)

        # Settings section / 设置区域
        settings_frame = ttk.LabelFrame(main_frame, text="Settings / 设置", padding="10")
        settings_frame.pack(fill=tk.X, pady=(0, 10))

        # Output directory / 输出目录
        dir_frame = ttk.Frame(settings_frame)
        dir_frame.pack(fill=tk.X, pady=5)

        ttk.Label(dir_frame, text="Output Directory / 输出目录:").pack(side=tk.LEFT)
        self.bookmark_output_var = tk.StringVar(value=self.default_output_dir)
        ttk.Entry(dir_frame, textvariable=self.bookmark_output_var, width=40).pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        ttk.Button(dir_frame, text="Browse / 浏览...", command=lambda: self.browse_directory(self.bookmark_output_var)).pack(side=tk.LEFT)

        # Browser type / 浏览器类型
        browser_frame = ttk.Frame(settings_frame)
        browser_frame.pack(fill=tk.X, pady=5)

        ttk.Label(browser_frame, text="Browser / 浏览器:").pack(side=tk.LEFT)
        self.browser_var = tk.StringVar(value="auto")
        ttk.Radiobutton(browser_frame, text="Auto / 自动", variable=self.browser_var, value="auto").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(browser_frame, text="Chrome", variable=self.browser_var, value="chrome").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(browser_frame, text="Edge", variable=self.browser_var, value="edge").pack(side=tk.LEFT, padx=5)

        # Limits frame / 限制设置框架
        limits_frame = ttk.Frame(settings_frame)
        limits_frame.pack(fill=tk.X, pady=5)

        # Max tweets / 最大推文数
        ttk.Label(limits_frame, text="Max tweets / 最大推文数:").pack(side=tk.LEFT)
        self.max_tweets_var = tk.StringVar(value="")
        ttk.Entry(limits_frame, textvariable=self.max_tweets_var, width=8).pack(side=tk.LEFT, padx=5)

        # Max scrolls / 最大滚动次数
        ttk.Label(limits_frame, text="Max scrolls / 最大滚动次数:").pack(side=tk.LEFT, padx=(20, 0))
        self.max_scrolls_var = tk.StringVar(value="")
        ttk.Entry(limits_frame, textvariable=self.max_scrolls_var, width=8).pack(side=tk.LEFT, padx=5)

        # More settings row / 更多设置行
        more_frame = ttk.Frame(settings_frame)
        more_frame.pack(fill=tk.X, pady=5)

        # Max video size / 最大视频大小
        ttk.Label(more_frame, text="Max video size (MB) / 最大视频大小:").pack(side=tk.LEFT)
        self.max_size_var = tk.StringVar(value="1500")
        ttk.Entry(more_frame, textvariable=self.max_size_var, width=8).pack(side=tk.LEFT, padx=5)

        # Headless mode / 无头模式
        self.headless_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(more_frame, text="Headless mode (no browser window) / 无头模式", variable=self.headless_var).pack(side=tk.LEFT, padx=20)

        # Start button / 开始按钮
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)

        self.bookmark_start_btn = ttk.Button(btn_frame, text="Start Download / 开始下载", command=self.start_bookmark_download)
        self.bookmark_start_btn.pack(side=tk.LEFT, padx=5)

        self.bookmark_stop_btn = ttk.Button(btn_frame, text="Stop / 停止", command=self.stop_download, state=tk.DISABLED)
        self.bookmark_stop_btn.pack(side=tk.LEFT, padx=5)

    def setup_bottom_controls(self):
        """Setup bottom controls (log area and action buttons) / 设置底部控件（日志区域和操作按钮）"""

        # Log area / 日志区域
        log_frame = ttk.LabelFrame(self.root, text="Log / 日志", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, wrap=tk.WORD, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # Clear log button / 清除日志按钮
        ttk.Button(log_frame, text="Clear Log / 清除日志", command=self.clear_log).pack(anchor=tk.E, pady=5)

        # Bottom button frame / 底部按钮框架
        bottom_frame = ttk.Frame(self.root)
        bottom_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        ttk.Button(bottom_frame, text="Open Output Folder / 打开输出目录", command=self.open_output_folder).pack(side=tk.LEFT, padx=5)

        # Status bar / 状态栏
        self.status_var = tk.StringVar(value="Ready / 就绪")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)

    def browse_directory(self, var):
        """Browse for directory / 浏览选择目录"""
        directory = filedialog.askdirectory(initialdir=var.get())
        if directory:
            var.set(directory)

    def load_urls_from_file(self):
        """Load URLs from a file / 从文件加载 URL"""
        filepath = filedialog.askopenfilename(
            title="Select URL file / 选择 URL 文件",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filepath:
            try:
                urls = read_urls_from_file(filepath)
                self.url_text.delete(1.0, tk.END)
                self.url_text.insert(tk.END, "\n".join(urls))
                self.url_file_label.config(text=f"Loaded {len(urls)} URLs / 已加载 {len(urls)} 个链接")
            except Exception as e:
                messagebox.showerror("Error / 错误", f"Failed to load file / 加载文件失败:\n{e}")

    def clear_log(self):
        """Clear the log area / 清除日志区域"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)

    def open_output_folder(self):
        """Open the output folder in file explorer / 在文件管理器中打开输出目录"""
        current_tab = self.notebook.index(self.notebook.select())

        if current_tab == 0:  # Video tab
            output_dir = self.video_output_var.get()
        else:  # Bookmark tab
            output_dir = self.bookmark_output_var.get()

        if not output_dir:
            output_dir = self.default_output_dir

        # Create directory if it doesn't exist / 如果目录不存在则创建
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        # Open in file explorer / 在文件管理器中打开
        if sys.platform == 'win32':
            os.startfile(output_dir)
        elif sys.platform == 'darwin':
            os.system(f'open "{output_dir}"')
        else:
            os.system(f'xdg-open "{output_dir}"')

    def log(self, message):
        """Add message to log queue / 添加消息到日志队列"""
        self.log_queue.put(message)

    def update_log_display(self):
        """Update log display from queue / 从队列更新日志显示"""
        try:
            while True:
                message = self.log_queue.get_nowait()
                self.log_text.config(state=tk.NORMAL)
                self.log_text.insert(tk.END, message)
                self.log_text.see(tk.END)
                self.log_text.config(state=tk.DISABLED)
        except queue.Empty:
            pass

        # Schedule next update / 安排下一次更新
        self.root.after(100, self.update_log_display)

    def set_downloading_state(self, is_downloading):
        """Update UI state based on download status / 根据下载状态更新 UI"""
        self.is_downloading = is_downloading

        # Update video tab buttons / 更新视频标签页按钮
        if is_downloading:
            self.video_start_btn.config(state=tk.DISABLED)
            self.video_stop_btn.config(state=tk.NORMAL)
        else:
            self.video_start_btn.config(state=tk.NORMAL)
            self.video_stop_btn.config(state=tk.DISABLED)

        # Update bookmark tab buttons / 更新书签标签页按钮
        if is_downloading:
            self.bookmark_start_btn.config(state=tk.DISABLED)
            self.bookmark_stop_btn.config(state=tk.NORMAL)
        else:
            self.bookmark_start_btn.config(state=tk.NORMAL)
            self.bookmark_stop_btn.config(state=tk.DISABLED)

    def stop_download(self):
        """Stop the current download / 停止当前下载"""
        if self.download_thread and self.download_thread.is_alive():
            self.log("\nStopping download... / 正在停止下载...\n")
            # Note: This is a soft stop. The thread will finish its current task.
            # 注意：这是软停止。线程会完成当前任务后停止。
            self.is_downloading = False
            self.set_downloading_state(False)
            self.status_var.set("Stopped / 已停止")

    def start_video_download(self):
        """Start video download / 开始视频下载"""
        # Get URLs / 获取 URL
        url_text = self.url_text.get(1.0, tk.END).strip()
        urls = [line.strip() for line in url_text.split('\n') if line.strip()]

        if not urls:
            messagebox.showwarning("Warning / 警告", "Please enter at least one URL / 请输入至少一个链接")
            return

        # Validate settings / 验证设置
        try:
            delay = float(self.video_delay_var.get())
        except ValueError:
            messagebox.showwarning("Warning / 警告", "Invalid delay value / 无效的延迟值")
            return

        output_dir = self.video_output_var.get()
        if not output_dir:
            output_dir = self.default_output_dir

        # Update UI / 更新界面
        self.set_downloading_state(True)
        self.status_var.set("Downloading... / 下载中...")

        # Redirect stdout / 重定向标准输出
        self.original_stdout = sys.stdout
        sys.stdout = TextRedirector(self.log_text, self.log_queue)

        # Start download thread / 启动下载线程
        def download_thread():
            try:
                downloader = TwitterVideoDownloader(
                    output_dir=output_dir,
                    delay=delay
                )
                downloader.download_from_urls(urls)
            except Exception as e:
                self.log(f"\nError / 错误: {e}\n")
            finally:
                sys.stdout = self.original_stdout
                self.root.after(0, lambda: self.set_downloading_state(False))
                self.root.after(0, lambda: self.status_var.set("Ready / 就绪"))

        self.download_thread = threading.Thread(target=download_thread, daemon=True)
        self.download_thread.start()

    def start_bookmark_download(self):
        """Start bookmark download / 开始书签下载"""

        # Validate settings / 验证设置
        output_dir = self.bookmark_output_var.get()
        if not output_dir:
            output_dir = self.default_output_dir

        try:
            max_tweets = int(self.max_tweets_var.get()) if self.max_tweets_var.get() else 999999
        except ValueError:
            messagebox.showwarning("Warning / 警告", "Invalid max tweets value / 无效的最大推文数值")
            return

        try:
            max_scrolls = int(self.max_scrolls_var.get()) if self.max_scrolls_var.get() else 999999
        except ValueError:
            messagebox.showwarning("Warning / 警告", "Invalid max scrolls value / 无效的最大滚动次数值")
            return

        try:
            max_size = float(self.max_size_var.get())
        except ValueError:
            messagebox.showwarning("Warning / 警告", "Invalid max size value / 无效的最大视频大小值")
            return

        browser_type = self.browser_var.get()
        headless = self.headless_var.get()

        # Update UI / 更新界面
        self.set_downloading_state(True)
        self.status_var.set("Downloading from bookmarks... / 从书签下载中...")

        # Redirect stdout / 重定向标准输出
        self.original_stdout = sys.stdout
        sys.stdout = TextRedirector(self.log_text, self.log_queue)

        # Start download thread / 启动下载线程
        def download_thread():
            try:
                # Create new event loop for this thread / 为此线程创建新的事件循环
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                downloader = TwitterBookmarkDownloader(
                    output_dir=output_dir,
                    headless=headless,
                    max_size_mb=max_size,
                    browser_type=browser_type
                )

                loop.run_until_complete(downloader.run(
                    max_tweets=max_tweets,
                    max_scrolls=max_scrolls
                ))
            except Exception as e:
                self.log(f"\nError / 错误: {e}\n")
            finally:
                if 'loop' in locals():
                    loop.close()
                sys.stdout = self.original_stdout
                self.root.after(0, lambda: self.set_downloading_state(False))
                self.root.after(0, lambda: self.status_var.set("Ready / 就绪"))

        self.download_thread = threading.Thread(target=download_thread, daemon=True)
        self.download_thread.start()


def main():
    """Main entry point / 主入口"""
    root = tk.Tk()

    # Set icon if available / 如果可用则设置图标
    try:
        root.iconbitmap(default='')
    except:
        pass

    # Apply a theme if available / 如果可用则应用主题
    try:
        style = ttk.Style()
        available_themes = style.theme_names()
        if 'clam' in available_themes:
            style.theme_use('clam')
        elif 'vista' in available_themes:
            style.theme_use('vista')
    except:
        pass

    app = TwitterDownloaderGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
