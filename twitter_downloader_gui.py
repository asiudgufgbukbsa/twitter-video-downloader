#!/usr/bin/env python3
"""
Twitter/X Video Downloader GUI
A modern, colorful and user-friendly interface with language support
"""

import os
import sys
import threading
import asyncio
import queue
import re
from pathlib import Path
from typing import Optional
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext, font

# Import downloader classes
try:
    from twitter_video_downloader import TwitterVideoDownloader, read_urls_from_file
except ImportError:
    print("Error: Cannot import twitter_video_downloader.py")
    sys.exit(1)

try:
    from twitter_bookmark_downloader import TwitterBookmarkDownloader
except ImportError:
    print("Error: Cannot import twitter_bookmark_downloader.py")
    sys.exit(1)


class Language:
    """Language strings"""
    EN = {
        "title": "Twitter Video Downloader",
        "ready": "Ready",
        "downloading": "Downloading...",
        "stopped": "Stopped",
        "tab_video": "📹 Video URL",
        "tab_bookmark": "🔖 Bookmarks",
        "tweet_urls": "Tweet URLs",
        "url_placeholder": "Paste tweet URLs here, one per line...",
        "load_file": "📁 Load from file",
        "loaded_urls": "Loaded {} URLs",
        "settings": "Settings",
        "save_to": "📁 Save to:",
        "delay": "⏱ Delay (sec):",
        "start": "▶ Start Download",
        "stop": "⏹ Stop",
        "how_to_use": "💡 Tips",
        "step1": "① Make sure you're logged into Twitter/X in Chrome or Edge",
        "step2": "② Close ALL browser windows before starting",
        "step3": "③ Click Start - a browser window will open automatically",
        "step4": "④ If not logged in, log in the browser then come back here",
        "browser": "🌐 Browser:",
        "auto": "Auto",
        "max_tweets": "📊 Max tweets:",
        "max_scrolls": "🔄 Max scrolls:",
        "max_size": "💾 Max size (MB):",
        "hide_browser": "Hide browser window",
        "log": "📝 Log",
        "clear_log": "🗑 Clear",
        "open_folder": "📂 Open Folder",
        "warn_no_url": "Please enter at least one URL",
        "warn_delay": "Invalid delay value",
        "warn_max_tweets": "Invalid max tweets value",
        "warn_max_scrolls": "Invalid max scrolls value",
        "warn_max_size": "Invalid max size value",
        "warn_load_file": "Failed to load file:\n{}",
        "lang_switch": "中文",
    }

    ZH = {
        "title": "Twitter 视频下载器",
        "ready": "就绪",
        "downloading": "下载中...",
        "stopped": "已停止",
        "tab_video": "📹 视频链接",
        "tab_bookmark": "🔖 书签下载",
        "tweet_urls": "推文链接",
        "url_placeholder": "在此粘贴推文链接，每行一个...",
        "load_file": "📁 从文件加载",
        "loaded_urls": "已加载 {} 个链接",
        "settings": "设置",
        "save_to": "📁 保存到:",
        "delay": "⏱ 间隔(秒):",
        "start": "▶ 开始下载",
        "stop": "⏹ 停止",
        "how_to_use": "💡 使用提示",
        "step1": "① 确保你已在 Chrome 或 Edge 中登录 Twitter/X",
        "step2": "② 开始前关闭所有浏览器窗口",
        "step3": "③ 点击开始 - 会自动打开浏览器窗口",
        "step4": "④ 如未登录，在浏览器中登录后返回此窗口",
        "browser": "🌐 浏览器:",
        "auto": "自动",
        "max_tweets": "📊 最大推文数:",
        "max_scrolls": "🔄 最大滚动次数:",
        "max_size": "💾 最大文件大小(MB):",
        "hide_browser": "隐藏浏览器窗口",
        "log": "📝 日志",
        "clear_log": "🗑 清除",
        "open_folder": "📂 打开目录",
        "warn_no_url": "请输入至少一个链接",
        "warn_delay": "无效的延迟值",
        "warn_max_tweets": "无效的最大推文数值",
        "warn_max_scrolls": "无效的最大滚动次数值",
        "warn_max_size": "无效的最大文件大小值",
        "warn_load_file": "加载文件失败:\n{}",
        "lang_switch": "EN",
    }


class Colors:
    """Color scheme - Twitter inspired vibrant colors"""
    # Primary colors
    BG_MAIN = "#1a1a2e"           # Dark blue background
    BG_CARD = "#16213e"           # Card background
    BG_INPUT = "#0f3460"          # Input background
    BG_HOVER = "#1f4287"          # Hover state

    # Accent colors
    PRIMARY = "#1da1f2"           # Twitter blue
    PRIMARY_HOVER = "#1a91da"
    SECONDARY = "#0fbcf9"         # Cyan
    SUCCESS = "#26de81"           # Green
    WARNING = "#fed330"           # Yellow
    ERROR = "#fc5c65"             # Red
    PURPLE = "#a55eea"            # Purple

    # Text colors
    TEXT_PRIMARY = "#ffffff"       # White
    TEXT_SECONDARY = "#a0aec0"    # Gray
    TEXT_ACCENT = "#63b3ed"       # Light blue

    # Special
    GRADIENT_START = "#667eea"    # Purple-blue
    GRADIENT_END = "#764ba2"      # Purple


class TextRedirector:
    """Redirect stdout to tkinter text widget with formatting"""
    def __init__(self, queue_obj):
        self.queue = queue_obj

    def write(self, string):
        self.queue.put(string)

    def flush(self):
        pass


class ColoredScrolledText(scrolledtext.ScrolledText):
    """ScrolledText with colored output support"""
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)

        # Configure text tags for different message types
        self.tag_config("success", foreground=Colors.SUCCESS)
        self.tag_config("error", foreground=Colors.ERROR)
        self.tag_config("warning", foreground=Colors.WARNING)
        self.tag_config("info", foreground=Colors.SECONDARY)
        self.tag_config("progress", foreground=Colors.PRIMARY)
        self.tag_config("normal", foreground=Colors.TEXT_PRIMARY)

    def append(self, text, tag="normal"):
        """Append text with optional color tag"""
        self.config(state=tk.NORMAL)
        self.insert(tk.END, text, tag)
        self.see(tk.END)
        self.config(state=tk.DISABLED)


class TwitterDownloaderGUI:
    """Main GUI Application with modern colorful design"""

    def __init__(self, root):
        self.root = root
        self.root.title("Twitter Video Downloader")
        self.root.geometry("700x750")
        self.root.minsize(600, 600)
        self.root.configure(bg=Colors.BG_MAIN)

        # Language setting
        self.lang = "en"

        # Center window
        self._center_window()

        # State
        self.log_queue = queue.Queue()
        self.is_downloading = False
        self.download_thread = None
        self.default_output_dir = str(Path.cwd() / "twitter_videos")
        self.original_stdout = sys.stdout

        # Setup
        self._setup_styles()
        self._setup_ui()
        self._update_log_display()

    def _center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        w, h = 700, 750
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    def _setup_styles(self):
        """Configure ttk styles with colors"""
        style = ttk.Style()

        # Frame styles
        style.configure("Main.TFrame", background=Colors.BG_MAIN)
        style.configure("Card.TFrame", background=Colors.BG_CARD)

        # Label styles
        style.configure("Title.TLabel",
                       font=("Segoe UI", 18, "bold"),
                       background=Colors.BG_MAIN,
                       foreground=Colors.PRIMARY)

        style.configure("Subtitle.TLabel",
                       font=("Segoe UI", 10),
                       background=Colors.BG_MAIN,
                       foreground=Colors.TEXT_SECONDARY)

        style.configure("Setting.TLabel",
                       font=("Segoe UI", 10),
                       background=Colors.BG_CARD,
                       foreground=Colors.TEXT_PRIMARY)

        style.configure("Info.TLabel",
                       font=("Segoe UI", 10),
                       background=Colors.BG_CARD,
                       foreground=Colors.TEXT_SECONDARY)

        style.configure("Step.TLabel",
                       font=("Segoe UI", 10),
                       background=Colors.BG_CARD,
                       foreground=Colors.TEXT_ACCENT)

        # Button styles
        style.configure("Accent.TButton",
                       font=("Segoe UI", 11, "bold"),
                       padding=(25, 12),
                       background=Colors.PRIMARY,
                       foreground=Colors.TEXT_PRIMARY)

        style.map("Accent.TButton",
                 background=[("active", Colors.PRIMARY_HOVER), ("pressed", Colors.SECONDARY)])

        style.configure("Small.TButton",
                       font=("Segoe UI", 9),
                       padding=(12, 6),
                       background=Colors.BG_HOVER,
                       foreground=Colors.TEXT_PRIMARY)

        style.configure("Lang.TButton",
                       font=("Segoe UI", 10, "bold"),
                       padding=(10, 5),
                       background=Colors.PURPLE,
                       foreground=Colors.TEXT_PRIMARY)

        # Notebook styles - this is the key for tab styling
        style.configure("TNotebook", background=Colors.BG_MAIN, borderwidth=0)
        style.configure("TNotebook.Tab",
                       font=("Segoe UI", 11, "bold"),
                       padding=(25, 12),
                       background=Colors.BG_CARD,
                       foreground=Colors.TEXT_SECONDARY)

        style.map("TNotebook.Tab",
                 background=[("selected", Colors.PRIMARY)],
                 foreground=[("selected", Colors.TEXT_PRIMARY)],
                 expand=[("selected", (2, 2, 2, 2))])

        # Entry styles
        style.configure("TEntry",
                       fieldbackground=Colors.BG_INPUT,
                       foreground=Colors.TEXT_PRIMARY,
                       insertcolor=Colors.TEXT_PRIMARY)

        # Radiobutton styles
        style.configure("TRadiobutton",
                       font=("Segoe UI", 10),
                       background=Colors.BG_CARD,
                       foreground=Colors.TEXT_PRIMARY)

        style.map("TRadiobutton",
                 background=[("active", Colors.BG_CARD)])

        # Checkbutton styles
        style.configure("TCheckbutton",
                       font=("Segoe UI", 10),
                       background=Colors.BG_CARD,
                       foreground=Colors.TEXT_PRIMARY)

        style.map("TCheckbutton",
                 background=[("active", Colors.BG_CARD)])

        # LabelFrame styles
        style.configure("Card.TLabelframe",
                       background=Colors.BG_CARD,
                       bordercolor=Colors.PRIMARY,
                       relief=tk.FLAT)
        style.configure("Card.TLabelframe.Label",
                       font=("Segoe UI", 11, "bold"),
                       background=Colors.BG_CARD,
                       foreground=Colors.PRIMARY)

        # Scrollbar
        style.configure("TScrollbar",
                       background=Colors.BG_HOVER,
                       troughcolor=Colors.BG_CARD,
                       arrowcolor=Colors.TEXT_PRIMARY)

    def _t(self, key):
        """Get translated string"""
        lang_dict = Language.ZH if self.lang == "zh" else Language.EN
        return lang_dict.get(key, key)

    def _toggle_language(self):
        """Toggle between English and Chinese"""
        if self.lang == "en":
            self.lang = "zh"
        else:
            self.lang = "en"
        self.lang_btn.config(text=self._t("lang_switch"))
        self._refresh_ui()

    def _refresh_ui(self):
        """Refresh UI with current language"""
        self.root.title(self._t("title"))
        self.title_label.config(text="🐦 " + self._t("title"))
        self.status_var.set(self._t("ready"))

        # Update tabs
        self.notebook.tab(self.video_frame, text=self._t("tab_video"))
        self.notebook.tab(self.bookmark_frame, text=self._t("tab_bookmark"))

        # Update video tab
        self.url_section.config(text=self._t("tweet_urls"))
        self.load_file_btn.config(text=self._t("load_file"))
        self.settings_section1.config(text=self._t("settings"))
        self.save_to_label1.config(text=self._t("save_to"))
        self.delay_label.config(text=self._t("delay"))
        self.video_start_btn.config(text=self._t("start"))
        self.video_stop_btn.config(text=self._t("stop"))

        # Update bookmark tab
        self.info_section.config(text=self._t("how_to_use"))
        for i, step_key in enumerate(["step1", "step2", "step3", "step4"]):
            self.step_labels[i].config(text=self._t(step_key))
        self.settings_section2.config(text=self._t("settings"))
        self.save_to_label2.config(text=self._t("save_to"))
        self.browser_label.config(text=self._t("browser"))
        self.auto_radio.config(text=self._t("auto"))
        self.max_tweets_label.config(text=self._t("max_tweets"))
        self.max_scrolls_label.config(text=self._t("max_scrolls"))
        self.max_size_label.config(text=self._t("max_size"))
        self.headless_check.config(text=self._t("hide_browser"))
        self.bookmark_start_btn.config(text=self._t("start"))
        self.bookmark_stop_btn.config(text=self._t("stop"))

        # Update footer
        self.log_section.config(text=self._t("log"))
        self.open_folder_btn.config(text=self._t("open_folder"))
        self.clear_log_btn.config(text=self._t("clear_log"))

        # Update placeholder
        current_text = self.url_text.get("1.0", tk.END).strip()
        if current_text.startswith("Paste") or current_text.startswith("在此"):
            self.url_text.delete("1.0", tk.END)
            self.url_text.insert(tk.END, self._t("url_placeholder"))

    def _setup_ui(self):
        """Setup the main user interface"""
        main_container = ttk.Frame(self.root, style="Main.TFrame")
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Header
        self._create_header(main_container)

        # Notebook (tabs)
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(15, 0))

        # Create tabs
        self._create_video_tab()
        self._create_bookmark_tab()

        # Log area (resizable)
        self._create_log_area(main_container)

        # Footer
        self._create_footer(main_container)

    def _create_header(self, parent):
        """Create header section"""
        header = ttk.Frame(parent, style="Main.TFrame")
        header.pack(fill=tk.X)

        title_frame = ttk.Frame(header, style="Main.TFrame")
        title_frame.pack(fill=tk.X)

        # Colorful logo with emoji
        logo_frame = ttk.Frame(title_frame, style="Main.TFrame")
        logo_frame.pack(side=tk.LEFT)

        self.title_label = tk.Label(
            logo_frame,
            text="🐦 " + self._t("title"),
            font=("Segoe UI", 18, "bold"),
            bg=Colors.BG_MAIN,
            fg=Colors.PRIMARY
        )
        self.title_label.pack(side=tk.LEFT)

        # Language toggle button
        self.lang_btn = tk.Button(
            title_frame,
            text=self._t("lang_switch"),
            font=("Segoe UI", 10, "bold"),
            bg=Colors.PURPLE,
            fg=Colors.TEXT_PRIMARY,
            activebackground=Colors.SECONDARY,
            activeforeground=Colors.TEXT_PRIMARY,
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor="hand2",
            command=self._toggle_language
        )
        self.lang_btn.pack(side=tk.RIGHT)

        # Status
        self.status_var = tk.StringVar(value=self._t("ready"))
        self.status_label = tk.Label(
            header,
            textvariable=self.status_var,
            font=("Segoe UI", 10),
            bg=Colors.BG_MAIN,
            fg=Colors.TEXT_SECONDARY
        )
        self.status_label.pack(anchor=tk.W, pady=(8, 0))

    def _create_video_tab(self):
        """Create video download tab"""
        self.video_frame = ttk.Frame(self.notebook, style="Card.TFrame", padding=15)
        self.notebook.add(self.video_frame, text=self._t("tab_video"))

        # URL Input Section
        self.url_section = ttk.LabelFrame(self.video_frame, text=self._t("tweet_urls"),
                                          style="Card.TLabelframe", padding=10)
        self.url_section.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.url_text = scrolledtext.ScrolledText(
            self.url_section,
            height=5,
            wrap=tk.WORD,
            font=("Segoe UI", 10),
            bg=Colors.BG_INPUT,
            fg=Colors.TEXT_PRIMARY,
            insertbackground=Colors.TEXT_PRIMARY,
            selectbackground=Colors.PRIMARY,
            relief=tk.FLAT,
            borderwidth=0,
            padx=10,
            pady=10
        )
        self.url_text.pack(fill=tk.BOTH, expand=True)
        self.url_text.insert(tk.END, self._t("url_placeholder"))
        self.url_text.configure(foreground=Colors.TEXT_SECONDARY)
        self.url_text.bind("<FocusIn>", self._on_url_focus_in)
        self.url_text.bind("<FocusOut>", self._on_url_focus_out)

        file_frame = ttk.Frame(self.url_section, style="Card.TFrame")
        file_frame.pack(fill=tk.X, pady=(10, 0))

        self.load_file_btn = tk.Button(
            file_frame,
            text=self._t("load_file"),
            font=("Segoe UI", 9),
            bg=Colors.BG_HOVER,
            fg=Colors.TEXT_PRIMARY,
            activebackground=Colors.PRIMARY,
            activeforeground=Colors.TEXT_PRIMARY,
            relief=tk.FLAT,
            padx=12,
            pady=6,
            cursor="hand2",
            command=self.load_urls_from_file
        )
        self.load_file_btn.pack(side=tk.LEFT)

        self.url_file_label = ttk.Label(file_frame, text="", style="Info.TLabel")
        self.url_file_label.pack(side=tk.LEFT, padx=10)

        # Settings Section
        self.settings_section1 = ttk.LabelFrame(self.video_frame, text=self._t("settings"),
                                                style="Card.TLabelframe", padding=10)
        self.settings_section1.pack(fill=tk.X, pady=(0, 15))

        dir_row = ttk.Frame(self.settings_section1, style="Card.TFrame")
        dir_row.pack(fill=tk.X, pady=5)

        self.save_to_label1 = ttk.Label(dir_row, text=self._t("save_to"), style="Setting.TLabel")
        self.save_to_label1.pack(side=tk.LEFT)
        self.video_output_var = tk.StringVar(value=self.default_output_dir)
        entry = ttk.Entry(dir_row, textvariable=self.video_output_var, width=35)
        entry.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        browse_btn = tk.Button(
            dir_row, text="Browse",
            font=("Segoe UI", 9),
            bg=Colors.BG_HOVER,
            fg=Colors.TEXT_PRIMARY,
            activebackground=Colors.PRIMARY,
            activeforeground=Colors.TEXT_PRIMARY,
            relief=tk.FLAT, padx=10, pady=5, cursor="hand2",
            command=lambda: self._browse_directory(self.video_output_var)
        )
        browse_btn.pack(side=tk.LEFT)

        delay_row = ttk.Frame(self.settings_section1, style="Card.TFrame")
        delay_row.pack(fill=tk.X, pady=5)

        self.delay_label = ttk.Label(delay_row, text=self._t("delay"), style="Setting.TLabel")
        self.delay_label.pack(side=tk.LEFT)
        self.video_delay_var = tk.StringVar(value="0.5")
        ttk.Entry(delay_row, textvariable=self.video_delay_var, width=8).pack(side=tk.LEFT, padx=10)

        # Action buttons
        btn_frame = ttk.Frame(self.video_frame, style="Card.TFrame")
        btn_frame.pack(fill=tk.X)

        self.video_start_btn = tk.Button(
            btn_frame, text=self._t("start"),
            font=("Segoe UI", 12, "bold"),
            bg=Colors.PRIMARY,
            fg=Colors.TEXT_PRIMARY,
            activebackground=Colors.SECONDARY,
            activeforeground=Colors.TEXT_PRIMARY,
            relief=tk.FLAT,
            padx=30,
            pady=12,
            cursor="hand2",
            command=self.start_video_download
        )
        self.video_start_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.video_stop_btn = tk.Button(
            btn_frame, text=self._t("stop"),
            font=("Segoe UI", 10),
            bg=Colors.ERROR,
            fg=Colors.TEXT_PRIMARY,
            activebackground=Colors.WARNING,
            activeforeground=Colors.BG_MAIN,
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor="hand2",
            command=self.stop_download,
            state=tk.DISABLED
        )
        self.video_stop_btn.pack(side=tk.LEFT)

    def _create_bookmark_tab(self):
        """Create bookmark download tab"""
        self.bookmark_frame = ttk.Frame(self.notebook, style="Card.TFrame", padding=15)
        self.notebook.add(self.bookmark_frame, text=self._t("tab_bookmark"))

        # Info Section
        self.info_section = ttk.LabelFrame(self.bookmark_frame, text=self._t("how_to_use"),
                                           style="Card.TLabelframe", padding=15)
        self.info_section.pack(fill=tk.X, pady=(0, 10))

        info_container = ttk.Frame(self.info_section, style="Card.TFrame")
        info_container.pack(fill=tk.X)

        self.step_labels = []
        for i, step_key in enumerate(["step1", "step2", "step3", "step4"]):
            label = tk.Label(
                info_container,
                text=self._t(step_key),
                font=("Segoe UI", 10),
                bg=Colors.BG_CARD,
                fg=Colors.TEXT_ACCENT,
                anchor=tk.W
            )
            label.pack(anchor=tk.W, pady=3)
            self.step_labels.append(label)

        # Settings Section
        self.settings_section2 = ttk.LabelFrame(self.bookmark_frame, text=self._t("settings"),
                                                style="Card.TLabelframe", padding=10)
        self.settings_section2.pack(fill=tk.X, pady=(0, 15))

        dir_row = ttk.Frame(self.settings_section2, style="Card.TFrame")
        dir_row.pack(fill=tk.X, pady=5)

        self.save_to_label2 = ttk.Label(dir_row, text=self._t("save_to"), style="Setting.TLabel")
        self.save_to_label2.pack(side=tk.LEFT)
        self.bookmark_output_var = tk.StringVar(value=self.default_output_dir)
        ttk.Entry(dir_row, textvariable=self.bookmark_output_var, width=35).pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        browse_btn = tk.Button(
            dir_row, text="Browse",
            font=("Segoe UI", 9),
            bg=Colors.BG_HOVER,
            fg=Colors.TEXT_PRIMARY,
            activebackground=Colors.PRIMARY,
            activeforeground=Colors.TEXT_PRIMARY,
            relief=tk.FLAT, padx=10, pady=5, cursor="hand2",
            command=lambda: self._browse_directory(self.bookmark_output_var)
        )
        browse_btn.pack(side=tk.LEFT)

        browser_row = ttk.Frame(self.settings_section2, style="Card.TFrame")
        browser_row.pack(fill=tk.X, pady=5)

        self.browser_label = ttk.Label(browser_row, text=self._t("browser"), style="Setting.TLabel")
        self.browser_label.pack(side=tk.LEFT)
        self.browser_var = tk.StringVar(value="auto")
        self.auto_radio = ttk.Radiobutton(browser_row, text=self._t("auto"),
                                          variable=self.browser_var, value="auto")
        self.auto_radio.pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(browser_row, text="Chrome", variable=self.browser_var, value="chrome").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(browser_row, text="Edge", variable=self.browser_var, value="edge").pack(side=tk.LEFT, padx=5)

        limits_row1 = ttk.Frame(self.settings_section2, style="Card.TFrame")
        limits_row1.pack(fill=tk.X, pady=5)

        self.max_tweets_label = ttk.Label(limits_row1, text=self._t("max_tweets"), style="Setting.TLabel")
        self.max_tweets_label.pack(side=tk.LEFT)
        self.max_tweets_var = tk.StringVar(value="")
        ttk.Entry(limits_row1, textvariable=self.max_tweets_var, width=8).pack(side=tk.LEFT, padx=(5, 20))

        self.max_scrolls_label = ttk.Label(limits_row1, text=self._t("max_scrolls"), style="Setting.TLabel")
        self.max_scrolls_label.pack(side=tk.LEFT)
        self.max_scrolls_var = tk.StringVar(value="")
        ttk.Entry(limits_row1, textvariable=self.max_scrolls_var, width=8).pack(side=tk.LEFT, padx=5)

        limits_row2 = ttk.Frame(self.settings_section2, style="Card.TFrame")
        limits_row2.pack(fill=tk.X, pady=5)

        self.max_size_label = ttk.Label(limits_row2, text=self._t("max_size"), style="Setting.TLabel")
        self.max_size_label.pack(side=tk.LEFT)
        self.max_size_var = tk.StringVar(value="1500")
        ttk.Entry(limits_row2, textvariable=self.max_size_var, width=8).pack(side=tk.LEFT, padx=(5, 20))

        self.headless_var = tk.BooleanVar(value=False)
        self.headless_check = ttk.Checkbutton(limits_row2, text=self._t("hide_browser"),
                                              variable=self.headless_var)
        self.headless_check.pack(side=tk.LEFT)

        # Action buttons
        btn_frame = ttk.Frame(self.bookmark_frame, style="Card.TFrame")
        btn_frame.pack(fill=tk.X)

        self.bookmark_start_btn = tk.Button(
            btn_frame, text=self._t("start"),
            font=("Segoe UI", 12, "bold"),
            bg=Colors.SUCCESS,
            fg=Colors.TEXT_PRIMARY,
            activebackground=Colors.SECONDARY,
            activeforeground=Colors.TEXT_PRIMARY,
            relief=tk.FLAT,
            padx=30,
            pady=12,
            cursor="hand2",
            command=self.start_bookmark_download
        )
        self.bookmark_start_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.bookmark_stop_btn = tk.Button(
            btn_frame, text=self._t("stop"),
            font=("Segoe UI", 10),
            bg=Colors.ERROR,
            fg=Colors.TEXT_PRIMARY,
            activebackground=Colors.WARNING,
            activeforeground=Colors.BG_MAIN,
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor="hand2",
            command=self.stop_download,
            state=tk.DISABLED
        )
        self.bookmark_stop_btn.pack(side=tk.LEFT)

    def _create_log_area(self, parent):
        """Create resizable log output area"""
        # Create a paned window for resizing
        self.paned = tk.PanedWindow(parent, orient=tk.VERTICAL, bg=Colors.BG_MAIN, sashwidth=10)
        self.paned.pack(fill=tk.BOTH, expand=True, pady=(15, 0))

        # Top frame (for tabs - already created)
        # We need to restructure, but for simplicity, just add log below

        log_frame = ttk.Frame(parent, style="Main.TFrame")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(15, 0))

        self.log_section = ttk.LabelFrame(log_frame, text=self._t("log"),
                                          style="Card.TLabelframe", padding=10)
        self.log_section.pack(fill=tk.BOTH, expand=True)

        self.log_text = scrolledtext.ScrolledText(
            self.log_section,
            height=8,
            wrap=tk.WORD,
            font=("Consolas", 10),
            bg=Colors.BG_INPUT,
            fg=Colors.TEXT_PRIMARY,
            insertbackground=Colors.TEXT_PRIMARY,
            selectbackground=Colors.PRIMARY,
            relief=tk.FLAT,
            borderwidth=0,
            padx=10,
            pady=10,
            state=tk.DISABLED
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # Configure text tags for colored output
        self.log_text.tag_config("success", foreground=Colors.SUCCESS)
        self.log_text.tag_config("error", foreground=Colors.ERROR)
        self.log_text.tag_config("warning", foreground=Colors.WARNING)
        self.log_text.tag_config("info", foreground=Colors.SECONDARY)
        self.log_text.tag_config("progress", foreground=Colors.PRIMARY)
        self.log_text.tag_config("highlight", foreground=Colors.PURPLE)

    def _create_footer(self, parent):
        """Create footer with action buttons"""
        footer = ttk.Frame(parent, style="Main.TFrame")
        footer.pack(fill=tk.X, pady=(15, 0))

        self.open_folder_btn = tk.Button(
            footer, text=self._t("open_folder"),
            font=("Segoe UI", 9),
            bg=Colors.BG_HOVER,
            fg=Colors.TEXT_PRIMARY,
            activebackground=Colors.PRIMARY,
            activeforeground=Colors.TEXT_PRIMARY,
            relief=tk.FLAT,
            padx=15,
            pady=6,
            cursor="hand2",
            command=self.open_output_folder
        )
        self.open_folder_btn.pack(side=tk.LEFT)

        self.clear_log_btn = tk.Button(
            footer, text=self._t("clear_log"),
            font=("Segoe UI", 9),
            bg=Colors.BG_HOVER,
            fg=Colors.TEXT_PRIMARY,
            activebackground=Colors.PRIMARY,
            activeforeground=Colors.TEXT_PRIMARY,
            relief=tk.FLAT,
            padx=15,
            pady=6,
            cursor="hand2",
            command=self.clear_log
        )
        self.clear_log_btn.pack(side=tk.RIGHT)

    def _on_url_focus_in(self, event):
        """Handle URL text area focus in"""
        text = self.url_text.get("1.0", tk.END).strip()
        if text.startswith("Paste") or text.startswith("在此"):
            self.url_text.delete("1.0", tk.END)
            self.url_text.configure(foreground=Colors.TEXT_PRIMARY)

    def _on_url_focus_out(self, event):
        """Handle URL text area focus out"""
        if not self.url_text.get("1.0", tk.END).strip():
            self.url_text.insert(tk.END, self._t("url_placeholder"))
            self.url_text.configure(foreground=Colors.TEXT_SECONDARY)

    def _browse_directory(self, var):
        """Browse for directory"""
        directory = filedialog.askdirectory(initialdir=var.get())
        if directory:
            var.set(directory)

    def load_urls_from_file(self):
        """Load URLs from a file"""
        filepath = filedialog.askopenfilename(
            title="Select URL file",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filepath:
            try:
                urls = read_urls_from_file(filepath)
                self.url_text.configure(foreground=Colors.TEXT_PRIMARY)
                self.url_text.delete("1.0", tk.END)
                self.url_text.insert(tk.END, "\n".join(urls))
                self.url_file_label.config(text=self._t("loaded_urls").format(len(urls)))
            except Exception as e:
                messagebox.showerror("Error", self._t("warn_load_file").format(e))

    def clear_log(self):
        """Clear the log area"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.config(state=tk.DISABLED)

    def open_output_folder(self):
        """Open the output folder"""
        current_tab = self.notebook.index(self.notebook.select())
        output_dir = self.video_output_var.get() if current_tab == 0 else self.bookmark_output_var.get()

        if not output_dir:
            output_dir = self.default_output_dir

        Path(output_dir).mkdir(parents=True, exist_ok=True)

        if sys.platform == 'win32':
            os.startfile(output_dir)
        elif sys.platform == 'darwin':
            os.system(f'open "{output_dir}"')
        else:
            os.system(f'xdg-open "{output_dir}"')

    def _get_log_tag(self, text):
        """Determine the appropriate tag for log text"""
        text_lower = text.lower()
        if "success" in text_lower or "✓" in text or "saved" in text_lower:
            return "success"
        elif "error" in text_lower or "✗" in text or "failed" in text_lower:
            return "error"
        elif "warning" in text_lower or "skipped" in text_lower:
            return "warning"
        elif "progress" in text_lower or "%" in text:
            return "progress"
        elif "starting" in text_lower or "downloading" in text_lower or "processing" in text_lower:
            return "info"
        elif "=" in text and len(text.strip()) > 10:
            return "highlight"
        return None

    def _update_log_display(self):
        """Update log display from queue with formatting"""
        try:
            while True:
                message = self.log_queue.get_nowait()
                self.log_text.config(state=tk.NORMAL)

                # Determine tag for coloring
                tag = self._get_log_tag(message)

                if tag:
                    self.log_text.insert(tk.END, message, tag)
                else:
                    self.log_text.insert(tk.END, message)

                self.log_text.see(tk.END)
                self.log_text.config(state=tk.DISABLED)
        except queue.Empty:
            pass

        self.root.after(100, self._update_log_display)

    def _set_downloading_state(self, is_downloading):
        """Update UI state based on download status"""
        self.is_downloading = is_downloading

        if is_downloading:
            self.video_start_btn.config(state=tk.DISABLED, bg=Colors.TEXT_SECONDARY)
            self.video_stop_btn.config(state=tk.NORMAL)
            self.bookmark_start_btn.config(state=tk.DISABLED, bg=Colors.TEXT_SECONDARY)
            self.bookmark_stop_btn.config(state=tk.NORMAL)
            self.status_var.set(self._t("downloading"))
            self.status_label.config(fg=Colors.WARNING)
        else:
            self.video_start_btn.config(state=tk.NORMAL, bg=Colors.PRIMARY)
            self.video_stop_btn.config(state=tk.DISABLED)
            self.bookmark_start_btn.config(state=tk.NORMAL, bg=Colors.SUCCESS)
            self.bookmark_stop_btn.config(state=tk.DISABLED)
            self.status_var.set(self._t("ready"))
            self.status_label.config(fg=Colors.TEXT_SECONDARY)

    def stop_download(self):
        """Stop the current download"""
        if self.download_thread and self.download_thread.is_alive():
            self.log_queue.put("\n⏹ Stopping download...\n")
            self.is_downloading = False
            self._set_downloading_state(False)
            self.status_var.set(self._t("stopped"))
            self.status_label.config(fg=Colors.ERROR)

    def start_video_download(self):
        """Start video download"""
        url_text = self.url_text.get("1.0", tk.END).strip()

        if url_text.startswith("Paste") or url_text.startswith("在此"):
            url_text = ""

        urls = [line.strip() for line in url_text.split('\n') if line.strip()]

        if not urls:
            messagebox.showwarning("Warning", self._t("warn_no_url"))
            return

        try:
            delay = float(self.video_delay_var.get())
        except ValueError:
            messagebox.showwarning("Warning", self._t("warn_delay"))
            return

        output_dir = self.video_output_var.get() or self.default_output_dir

        self._set_downloading_state(True)
        sys.stdout = TextRedirector(self.log_queue)

        def download_thread():
            try:
                downloader = TwitterVideoDownloader(output_dir=output_dir, delay=delay)
                downloader.download_from_urls(urls)
            except Exception as e:
                self.log_queue.put(f"\n❌ Error: {e}\n")
            finally:
                sys.stdout = self.original_stdout
                self.root.after(0, lambda: self._set_downloading_state(False))

        self.download_thread = threading.Thread(target=download_thread, daemon=True)
        self.download_thread.start()

    def start_bookmark_download(self):
        """Start bookmark download"""
        output_dir = self.bookmark_output_var.get() or self.default_output_dir

        try:
            max_tweets = int(self.max_tweets_var.get()) if self.max_tweets_var.get() else 999999
        except ValueError:
            messagebox.showwarning("Warning", self._t("warn_max_tweets"))
            return

        try:
            max_scrolls = int(self.max_scrolls_var.get()) if self.max_scrolls_var.get() else 999999
        except ValueError:
            messagebox.showwarning("Warning", self._t("warn_max_scrolls"))
            return

        try:
            max_size = float(self.max_size_var.get())
        except ValueError:
            messagebox.showwarning("Warning", self._t("warn_max_size"))
            return

        browser_type = self.browser_var.get()
        headless = self.headless_var.get()

        self._set_downloading_state(True)
        sys.stdout = TextRedirector(self.log_queue)

        def download_thread():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                downloader = TwitterBookmarkDownloader(
                    output_dir=output_dir,
                    headless=headless,
                    max_size_mb=max_size,
                    browser_type=browser_type
                )

                loop.run_until_complete(downloader.run(max_tweets=max_tweets, max_scrolls=max_scrolls))
            except Exception as e:
                self.log_queue.put(f"\n❌ Error: {e}\n")
            finally:
                if 'loop' in locals():
                    loop.close()
                sys.stdout = self.original_stdout
                self.root.after(0, lambda: self._set_downloading_state(False))

        self.download_thread = threading.Thread(target=download_thread, daemon=True)
        self.download_thread.start()


def main():
    """Main entry point"""
    root = tk.Tk()

    try:
        root.iconbitmap(default='')
    except:
        pass

    try:
        style = ttk.Style()
        if 'clam' in style.theme_names():
            style.theme_use('clam')
    except:
        pass

    app = TwitterDownloaderGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
