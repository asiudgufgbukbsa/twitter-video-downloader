#!/usr/bin/env python3
"""
Twitter/X Video Downloader GUI
A modern, clean graphical user interface with language support
"""

import os
import sys
import threading
import asyncio
import queue
from pathlib import Path
from typing import Optional
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

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
    # English
    EN = {
        # Header
        "title": "Twitter Video Downloader",
        "ready": "Ready",
        "downloading": "Downloading...",
        "stopped": "Stopped",

        # Tabs
        "tab_video": "  📹 Video URL  ",
        "tab_bookmark": "  🔖 Bookmarks  ",

        # Video tab
        "tweet_urls": "Tweet URLs",
        "url_placeholder": "Paste tweet URLs here, one per line...",
        "load_file": "📁 Load from file",
        "loaded_urls": "Loaded {} URLs",
        "settings": "Settings",
        "save_to": "📁 Save to:",
        "delay": "⏱ Delay (sec):",
        "start": "▶ Start Download",
        "stop": "⏹ Stop",

        # Bookmark tab
        "how_to_use": "How to use",
        "step1": "1️⃣  Login to Twitter/X in Chrome or Edge",
        "step2": "2️⃣  Close all browser windows before starting",
        "step3": "3️⃣  Click Start and wait for browser to open",
        "step4": "4️⃣  Login if needed, then press Enter in terminal",
        "browser": "🌐 Browser:",
        "auto": "Auto",
        "max_tweets": "📊 Max tweets:",
        "max_scrolls": "🔄 Max scrolls:",
        "max_size": "💾 Max size (MB):",
        "hide_browser": "Hide browser window",

        # Log
        "log": "📝 Log",
        "clear_log": "🗑 Clear Log",
        "open_folder": "📂 Open Output Folder",

        # Warnings
        "warn_no_url": "Please enter at least one URL",
        "warn_delay": "Invalid delay value",
        "warn_max_tweets": "Invalid max tweets value",
        "warn_max_scrolls": "Invalid max scrolls value",
        "warn_max_size": "Invalid max size value",
        "warn_load_file": "Failed to load file:\n{}",

        # Language toggle
        "lang_en": "EN",
        "lang_zh": "中文",
    }

    # Chinese
    ZH = {
        # Header
        "title": "Twitter 视频下载器",
        "ready": "就绪",
        "downloading": "下载中...",
        "stopped": "已停止",

        # Tabs
        "tab_video": "  📹 视频链接  ",
        "tab_bookmark": "  🔖 书签下载  ",

        # Video tab
        "tweet_urls": "推文链接",
        "url_placeholder": "在此粘贴推文链接，每行一个...",
        "load_file": "📁 从文件加载",
        "loaded_urls": "已加载 {} 个链接",
        "settings": "设置",
        "save_to": "📁 保存到:",
        "delay": "⏱ 间隔(秒):",
        "start": "▶ 开始下载",
        "stop": "⏹ 停止",

        # Bookmark tab
        "how_to_use": "使用说明",
        "step1": "1️⃣  在 Chrome 或 Edge 中登录 Twitter/X",
        "step2": "2️⃣  开始前关闭所有浏览器窗口",
        "step3": "3️⃣  点击开始，等待浏览器打开",
        "step4": "4️⃣  如需登录，在浏览器中登录后按回车",
        "browser": "🌐 浏览器:",
        "auto": "自动",
        "max_tweets": "📊 最大推文数:",
        "max_scrolls": "🔄 最大滚动次数:",
        "max_size": "💾 最大文件大小(MB):",
        "hide_browser": "隐藏浏览器窗口",

        # Log
        "log": "📝 日志",
        "clear_log": "🗑 清除日志",
        "open_folder": "📂 打开输出目录",

        # Warnings
        "warn_no_url": "请输入至少一个链接",
        "warn_delay": "无效的延迟值",
        "warn_max_tweets": "无效的最大推文数值",
        "warn_max_scrolls": "无效的最大滚动次数值",
        "warn_max_size": "无效的最大文件大小值",
        "warn_load_file": "加载文件失败:\n{}",

        # Language toggle
        "lang_en": "EN",
        "lang_zh": "中文",
    }


class ModernStyle:
    """Modern color scheme and fonts"""
    BG_PRIMARY = "#ffffff"
    BG_SECONDARY = "#f8f9fa"
    BG_TERTIARY = "#e9ecef"
    ACCENT = "#1da1f2"
    ACCENT_HOVER = "#1a91da"
    TEXT_PRIMARY = "#14171a"
    TEXT_SECONDARY = "#657786"
    SUCCESS = "#17bf63"
    ERROR = "#e0245e"
    WARNING = "#ffad1f"
    BORDER = "#e1e8ed"

    FONT_FAMILY = "Segoe UI"
    FONT_SIZE_TITLE = 16
    FONT_SIZE_NORMAL = 10
    FONT_SIZE_SMALL = 9


class TextRedirector:
    """Redirect stdout to tkinter text widget"""
    def __init__(self, queue_obj):
        self.queue = queue_obj

    def write(self, string):
        self.queue.put(string)

    def flush(self):
        pass


class TwitterDownloaderGUI:
    """Main GUI Application with modern design and language support"""

    def __init__(self, root):
        self.root = root
        self.root.title("Twitter Video Downloader")
        self.root.geometry("650x720")
        self.root.minsize(550, 550)
        self.root.configure(bg=ModernStyle.BG_PRIMARY)

        # Language setting (default to system language)
        self.lang = "en"
        self.lang_btn_text = "中文"

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
        w, h = 650, 720
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    def _setup_styles(self):
        """Configure ttk styles"""
        style = ttk.Style()

        style.configure("Card.TFrame", background=ModernStyle.BG_PRIMARY)
        style.configure("Secondary.TFrame", background=ModernStyle.BG_SECONDARY)

        style.configure("Title.TLabel",
                       font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_TITLE, "bold"),
                       background=ModernStyle.BG_PRIMARY,
                       foreground=ModernStyle.TEXT_PRIMARY)

        style.configure("Subtitle.TLabel",
                       font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_NORMAL),
                       background=ModernStyle.BG_PRIMARY,
                       foreground=ModernStyle.TEXT_SECONDARY)

        style.configure("Setting.TLabel",
                       font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_NORMAL),
                       background=ModernStyle.BG_PRIMARY,
                       foreground=ModernStyle.TEXT_PRIMARY)

        style.configure("Info.TLabel",
                       font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SMALL),
                       background=ModernStyle.BG_SECONDARY,
                       foreground=ModernStyle.TEXT_SECONDARY)

        style.configure("Accent.TButton",
                       font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_NORMAL, "bold"),
                       padding=(20, 10))

        style.configure("Small.TButton",
                       font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SMALL),
                       padding=(10, 5))

        style.configure("Lang.TButton",
                       font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SMALL, "bold"),
                       padding=(8, 4))

        style.configure("TNotebook", background=ModernStyle.BG_PRIMARY)
        style.configure("TNotebook.Tab",
                       font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_NORMAL),
                       padding=(20, 10))

        style.configure("TRadiobutton",
                       font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_NORMAL),
                       background=ModernStyle.BG_PRIMARY)

        style.configure("TCheckbutton",
                       font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SMALL),
                       background=ModernStyle.BG_PRIMARY)

        style.configure("Card.TLabelframe",
                       background=ModernStyle.BG_PRIMARY)
        style.configure("Card.TLabelframe.Label",
                       font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_NORMAL, "bold"),
                       background=ModernStyle.BG_PRIMARY,
                       foreground=ModernStyle.TEXT_PRIMARY)

    def _t(self, key):
        """Get translated string"""
        lang_dict = Language.ZH if self.lang == "zh" else Language.EN
        return lang_dict.get(key, key)

    def _toggle_language(self):
        """Toggle between English and Chinese"""
        if self.lang == "en":
            self.lang = "zh"
            self.lang_btn_text = "EN"
        else:
            self.lang = "en"
            self.lang_btn_text = "中文"

        self.lang_btn.config(text=self.lang_btn_text)
        self._refresh_ui()

    def _refresh_ui(self):
        """Refresh UI with current language"""
        # Update title
        self.root.title(self._t("title"))
        self.title_label.config(text="🐦  " + self._t("title"))
        self.status_var.set(self._t("ready"))

        # Update tabs
        self.notebook.tab(self.video_frame, text=self._t("tab_video"))
        self.notebook.tab(self.bookmark_frame, text=self._t("tab_bookmark"))

        # Update video tab
        self.url_label.config(text=self._t("tweet_urls"))
        self.load_file_btn.config(text=self._t("load_file"))
        self.settings_label1.config(text=self._t("settings"))
        self.save_to_label1.config(text=self._t("save_to"))
        self.delay_label.config(text=self._t("delay"))
        self.video_start_btn.config(text=self._t("start"))
        self.video_stop_btn.config(text=self._t("stop"))

        # Update bookmark tab
        self.how_to_use_label.config(text=self._t("how_to_use"))
        self.step_labels[0].config(text=self._t("step1"))
        self.step_labels[1].config(text=self._t("step2"))
        self.step_labels[2].config(text=self._t("step3"))
        self.step_labels[3].config(text=self._t("step4"))
        self.settings_label2.config(text=self._t("settings"))
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
        self.log_label.config(text=self._t("log"))
        self.open_folder_btn.config(text=self._t("open_folder"))
        self.clear_log_btn.config(text=self._t("clear_log"))

        # Update placeholder
        if self.url_text.get("1.0", tk.END).strip().startswith("Paste") or \
           self.url_text.get("1.0", tk.END).strip().startswith("在此"):
            self.url_text.delete("1.0", tk.END)
            self.url_text.insert(tk.END, self._t("url_placeholder"))
            self.url_text.configure(foreground=ModernStyle.TEXT_SECONDARY)

    def _setup_ui(self):
        """Setup the main user interface"""
        main_container = ttk.Frame(self.root, style="Card.TFrame")
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Header
        self._create_header(main_container)

        # Notebook (tabs)
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=(15, 0))

        # Create tabs
        self._create_video_tab()
        self._create_bookmark_tab()

        # Log area
        self._create_log_area(main_container)

        # Footer
        self._create_footer(main_container)

    def _create_header(self, parent):
        """Create header section"""
        header = ttk.Frame(parent, style="Card.TFrame")
        header.pack(fill=tk.X)

        title_frame = ttk.Frame(header, style="Card.TFrame")
        title_frame.pack(fill=tk.X)

        self.title_label = ttk.Label(title_frame, text="🐦  " + self._t("title"), style="Title.TLabel")
        self.title_label.pack(side=tk.LEFT)

        # Language toggle button
        self.lang_btn = ttk.Button(title_frame, text="中文", style="Lang.TButton",
                                   command=self._toggle_language, width=6)
        self.lang_btn.pack(side=tk.RIGHT)

        self.status_var = tk.StringVar(value=self._t("ready"))
        ttk.Label(header, textvariable=self.status_var, style="Subtitle.TLabel").pack(anchor=tk.W, pady=(5, 0))

    def _create_video_tab(self):
        """Create video download tab"""
        self.video_frame = ttk.Frame(self.notebook, style="Card.TFrame", padding=15)
        self.notebook.add(self.video_frame, text=self._t("tab_video"))

        # URL Input Section
        url_section = ttk.LabelFrame(self.video_frame, text=self._t("tweet_urls"),
                                     style="Card.TLabelframe", padding=10)
        url_section.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.url_label = ttk.Label(url_section, text=self._t("tweet_urls"), style="Setting.TLabel")
        self.url_label.pack_forget()  # We use LabelFrame title instead

        self.url_text = scrolledtext.ScrolledText(
            url_section,
            height=6,
            wrap=tk.WORD,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_NORMAL),
            bg=ModernStyle.BG_SECONDARY,
            relief=tk.FLAT,
            borderwidth=0
        )
        self.url_text.pack(fill=tk.BOTH, expand=True)
        self.url_text.insert(tk.END, self._t("url_placeholder"))
        self.url_text.configure(foreground=ModernStyle.TEXT_SECONDARY)
        self.url_text.bind("<FocusIn>", self._on_url_focus_in)
        self.url_text.bind("<FocusOut>", self._on_url_focus_out)

        file_frame = ttk.Frame(url_section, style="Card.TFrame")
        file_frame.pack(fill=tk.X, pady=(10, 0))

        self.load_file_btn = ttk.Button(file_frame, text=self._t("load_file"),
                                        style="Small.TButton", command=self.load_urls_from_file)
        self.load_file_btn.pack(side=tk.LEFT)
        self.url_file_label = ttk.Label(file_frame, text="", style="Info.TLabel")
        self.url_file_label.pack(side=tk.LEFT, padx=10)

        # Settings Section
        settings_section = ttk.LabelFrame(self.video_frame, text=self._t("settings"),
                                          style="Card.TLabelframe", padding=10)
        settings_section.pack(fill=tk.X, pady=(0, 15))
        self.settings_label1 = ttk.Label(settings_section, text=self._t("settings"), style="Setting.TLabel")
        self.settings_label1.pack_forget()  # We use LabelFrame title instead

        dir_row = ttk.Frame(settings_section, style="Card.TFrame")
        dir_row.pack(fill=tk.X, pady=5)

        self.save_to_label1 = ttk.Label(dir_row, text=self._t("save_to"), style="Setting.TLabel")
        self.save_to_label1.pack(side=tk.LEFT)
        self.video_output_var = tk.StringVar(value=self.default_output_dir)
        ttk.Entry(dir_row, textvariable=self.video_output_var, width=40).pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        ttk.Button(dir_row, text="Browse", style="Small.TButton",
                  command=lambda: self._browse_directory(self.video_output_var)).pack(side=tk.LEFT)

        delay_row = ttk.Frame(settings_section, style="Card.TFrame")
        delay_row.pack(fill=tk.X, pady=5)

        self.delay_label = ttk.Label(delay_row, text=self._t("delay"), style="Setting.TLabel")
        self.delay_label.pack(side=tk.LEFT)
        self.video_delay_var = tk.StringVar(value="0.5")
        ttk.Entry(delay_row, textvariable=self.video_delay_var, width=8).pack(side=tk.LEFT, padx=10)

        btn_frame = ttk.Frame(self.video_frame, style="Card.TFrame")
        btn_frame.pack(fill=tk.X)

        self.video_start_btn = ttk.Button(btn_frame, text=self._t("start"),
                                          style="Accent.TButton", command=self.start_video_download)
        self.video_start_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.video_stop_btn = ttk.Button(btn_frame, text=self._t("stop"),
                                         style="Small.TButton", command=self.stop_download, state=tk.DISABLED)
        self.video_stop_btn.pack(side=tk.LEFT)

    def _create_bookmark_tab(self):
        """Create bookmark download tab"""
        self.bookmark_frame = ttk.Frame(self.notebook, style="Card.TFrame", padding=15)
        self.notebook.add(self.bookmark_frame, text=self._t("tab_bookmark"))

        # Info Section
        info_section = ttk.LabelFrame(self.bookmark_frame, text=self._t("how_to_use"),
                                      style="Card.TLabelframe", padding=10)
        info_section.pack(fill=tk.X, pady=(0, 10))

        self.how_to_use_label = ttk.Label(info_section, text=self._t("how_to_use"), style="Setting.TLabel")
        self.how_to_use_label.pack_forget()

        info_container = ttk.Frame(info_section, style="Card.TFrame")
        info_container.pack(fill=tk.X)

        self.step_labels = []
        for step_key in ["step1", "step2", "step3", "step4"]:
            label = ttk.Label(info_container, text=self._t(step_key), style="Info.TLabel", justify=tk.LEFT)
            label.pack(anchor=tk.W)
            self.step_labels.append(label)

        # Settings Section
        settings_section = ttk.LabelFrame(self.bookmark_frame, text=self._t("settings"),
                                          style="Card.TLabelframe", padding=10)
        settings_section.pack(fill=tk.X, pady=(0, 15))
        self.settings_label2 = ttk.Label(settings_section, text=self._t("settings"), style="Setting.TLabel")
        self.settings_label2.pack_forget()

        dir_row = ttk.Frame(settings_section, style="Card.TFrame")
        dir_row.pack(fill=tk.X, pady=5)

        self.save_to_label2 = ttk.Label(dir_row, text=self._t("save_to"), style="Setting.TLabel")
        self.save_to_label2.pack(side=tk.LEFT)
        self.bookmark_output_var = tk.StringVar(value=self.default_output_dir)
        ttk.Entry(dir_row, textvariable=self.bookmark_output_var, width=40).pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        ttk.Button(dir_row, text="Browse", style="Small.TButton",
                  command=lambda: self._browse_directory(self.bookmark_output_var)).pack(side=tk.LEFT)

        browser_row = ttk.Frame(settings_section, style="Card.TFrame")
        browser_row.pack(fill=tk.X, pady=5)

        self.browser_label = ttk.Label(browser_row, text=self._t("browser"), style="Setting.TLabel")
        self.browser_label.pack(side=tk.LEFT)
        self.browser_var = tk.StringVar(value="auto")
        self.auto_radio = ttk.Radiobutton(browser_row, text=self._t("auto"),
                                          variable=self.browser_var, value="auto")
        self.auto_radio.pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(browser_row, text="Chrome", variable=self.browser_var, value="chrome").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(browser_row, text="Edge", variable=self.browser_var, value="edge").pack(side=tk.LEFT, padx=5)

        limits_row1 = ttk.Frame(settings_section, style="Card.TFrame")
        limits_row1.pack(fill=tk.X, pady=5)

        self.max_tweets_label = ttk.Label(limits_row1, text=self._t("max_tweets"), style="Setting.TLabel")
        self.max_tweets_label.pack(side=tk.LEFT)
        self.max_tweets_var = tk.StringVar(value="")
        ttk.Entry(limits_row1, textvariable=self.max_tweets_var, width=8).pack(side=tk.LEFT, padx=(5, 20))

        self.max_scrolls_label = ttk.Label(limits_row1, text=self._t("max_scrolls"), style="Setting.TLabel")
        self.max_scrolls_label.pack(side=tk.LEFT)
        self.max_scrolls_var = tk.StringVar(value="")
        ttk.Entry(limits_row1, textvariable=self.max_scrolls_var, width=8).pack(side=tk.LEFT, padx=5)

        limits_row2 = ttk.Frame(settings_section, style="Card.TFrame")
        limits_row2.pack(fill=tk.X, pady=5)

        self.max_size_label = ttk.Label(limits_row2, text=self._t("max_size"), style="Setting.TLabel")
        self.max_size_label.pack(side=tk.LEFT)
        self.max_size_var = tk.StringVar(value="1500")
        ttk.Entry(limits_row2, textvariable=self.max_size_var, width=8).pack(side=tk.LEFT, padx=(5, 20))

        self.headless_var = tk.BooleanVar(value=False)
        self.headless_check = ttk.Checkbutton(limits_row2, text=self._t("hide_browser"),
                                              variable=self.headless_var)
        self.headless_check.pack(side=tk.LEFT)

        btn_frame = ttk.Frame(self.bookmark_frame, style="Card.TFrame")
        btn_frame.pack(fill=tk.X)

        self.bookmark_start_btn = ttk.Button(btn_frame, text=self._t("start"),
                                             style="Accent.TButton", command=self.start_bookmark_download)
        self.bookmark_start_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.bookmark_stop_btn = ttk.Button(btn_frame, text=self._t("stop"),
                                            style="Small.TButton", command=self.stop_download, state=tk.DISABLED)
        self.bookmark_stop_btn.pack(side=tk.LEFT)

    def _create_log_area(self, parent):
        """Create log output area"""
        log_section = ttk.LabelFrame(parent, text=self._t("log"), style="Card.TLabelframe", padding=10)
        log_section.pack(fill=tk.BOTH, expand=True, pady=(15, 0))

        self.log_label = ttk.Label(log_section, text=self._t("log"), style="Setting.TLabel")
        self.log_label.pack_forget()

        self.log_text = scrolledtext.ScrolledText(
            log_section,
            height=8,
            wrap=tk.WORD,
            font=("Consolas", ModernStyle.FONT_SIZE_SMALL),
            bg=ModernStyle.BG_SECONDARY,
            fg=ModernStyle.TEXT_PRIMARY,
            relief=tk.FLAT,
            borderwidth=0,
            state=tk.DISABLED
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

    def _create_footer(self, parent):
        """Create footer with action buttons"""
        footer = ttk.Frame(parent, style="Card.TFrame")
        footer.pack(fill=tk.X, pady=(15, 0))

        self.open_folder_btn = ttk.Button(footer, text=self._t("open_folder"),
                                          style="Small.TButton", command=self.open_output_folder)
        self.open_folder_btn.pack(side=tk.LEFT)

        self.clear_log_btn = ttk.Button(footer, text=self._t("clear_log"),
                                        style="Small.TButton", command=self.clear_log)
        self.clear_log_btn.pack(side=tk.RIGHT)

    def _on_url_focus_in(self, event):
        """Handle URL text area focus in"""
        text = self.url_text.get("1.0", tk.END).strip()
        if text.startswith("Paste") or text.startswith("在此"):
            self.url_text.delete("1.0", tk.END)
            self.url_text.configure(foreground=ModernStyle.TEXT_PRIMARY)

    def _on_url_focus_out(self, event):
        """Handle URL text area focus out"""
        if not self.url_text.get("1.0", tk.END).strip():
            self.url_text.insert(tk.END, self._t("url_placeholder"))
            self.url_text.configure(foreground=ModernStyle.TEXT_SECONDARY)

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
                self.url_text.configure(foreground=ModernStyle.TEXT_PRIMARY)
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

    def _update_log_display(self):
        """Update log display from queue"""
        try:
            while True:
                message = self.log_queue.get_nowait()
                self.log_text.config(state=tk.NORMAL)
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
            self.video_start_btn.config(state=tk.DISABLED)
            self.video_stop_btn.config(state=tk.NORMAL)
            self.bookmark_start_btn.config(state=tk.DISABLED)
            self.bookmark_stop_btn.config(state=tk.NORMAL)
            self.status_var.set(self._t("downloading"))
        else:
            self.video_start_btn.config(state=tk.NORMAL)
            self.video_stop_btn.config(state=tk.DISABLED)
            self.bookmark_start_btn.config(state=tk.NORMAL)
            self.bookmark_stop_btn.config(state=tk.DISABLED)
            self.status_var.set(self._t("ready"))

    def stop_download(self):
        """Stop the current download"""
        if self.download_thread and self.download_thread.is_alive():
            self.log_queue.put("\n⏹ Stopping download...\n")
            self.is_downloading = False
            self._set_downloading_state(False)
            self.status_var.set(self._t("stopped"))

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
