#!/usr/bin/env python3
"""
Twitter/X Video Downloader GUI
A cute, warm beige-themed interface with scroll support
"""

import os
import sys
import threading
import asyncio
import queue
from pathlib import Path
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
    EN = {
        "title": "Twitter Video Downloader",
        "ready": "✨ Ready",
        "downloading": "⏳ Downloading...",
        "stopped": "⏹ Stopped",
        "tab_video": "📹 Video URL",
        "tab_bookmark": "🔖 Bookmarks",
        "tweet_urls": "Tweet URLs",
        "url_placeholder": "✏️ Paste tweet URLs here, one per line...\n\nExample:\nhttps://x.com/user/status/123456789\nhttps://x.com/user/status/987654321",
        "load_file": "📁 Load from file",
        "loaded_urls": "✅ Loaded {} URLs",
        "settings": "⚙️ Settings",
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
        "ready": "✨ 就绪",
        "downloading": "⏳ 下载中...",
        "stopped": "⏹ 已停止",
        "tab_video": "📹 视频链接",
        "tab_bookmark": "🔖 书签下载",
        "tweet_urls": "推文链接",
        "url_placeholder": "✏️ 在此粘贴推文链接，每行一个...\n\n示例:\nhttps://x.com/user/status/123456789\nhttps://x.com/user/status/987654321",
        "load_file": "📁 从文件加载",
        "loaded_urls": "✅ 已加载 {} 个链接",
        "settings": "⚙️ 设置",
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
    """Warm beige color scheme - cute and cozy"""
    BG_MAIN = "#FFF8E7"
    BG_CARD = "#FFFEF5"
    BG_INPUT = "#FFFDF0"
    BG_TAB = "#F5EBD8"
    BG_TAB_ACTIVE = "#FF9A8B"
    PRIMARY = "#FF7B7B"
    PRIMARY_HOVER = "#FF6B6B"
    SECONDARY = "#FFB347"
    SUCCESS = "#7BC47F"
    WARNING = "#FFD93D"
    ERROR = "#FF6B8A"
    INFO = "#74B9FF"
    PURPLE = "#B19CD9"
    TEXT_PRIMARY = "#5D4E37"
    TEXT_SECONDARY = "#8B7355"
    TEXT_LIGHT = "#A89078"
    TEXT_WHITE = "#FFFFFF"
    BORDER = "#E8DCC8"


class TextRedirector:
    """Redirect stdout to tkinter text widget"""
    def __init__(self, queue_obj):
        self.queue = queue_obj

    def write(self, string):
        self.queue.put(string)

    def flush(self):
        pass


class TabButton(tk.Canvas):
    """Custom tab button with cute styling"""
    def __init__(self, parent, text, command, **kwargs):
        super().__init__(parent, width=160, height=40, highlightthickness=0, **kwargs)

        self.text = text
        self.command = command
        self.is_active = False
        self.parent_bg = kwargs.get('bg', Colors.BG_MAIN)

        self.configure(bg=self.parent_bg)
        self._draw()

        self.bind("<Button-1>", self._on_click)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _draw(self, hover=False):
        self.delete("all")

        if self.is_active:
            bg_color = Colors.BG_TAB_ACTIVE
            text_color = Colors.TEXT_WHITE
            font_size = 12
        elif hover:
            bg_color = Colors.SECONDARY
            text_color = Colors.TEXT_WHITE
            font_size = 11
        else:
            bg_color = Colors.BG_TAB
            text_color = Colors.TEXT_PRIMARY
            font_size = 11

        # Draw rounded rectangle
        self._draw_rounded_rect(5, 5, 155, 35, 12, bg_color)

        # Draw text
        self.create_text(80, 20, text=self.text, font=("Segoe UI", font_size, "bold"),
                        fill=text_color)

    def _draw_rounded_rect(self, x1, y1, x2, y2, radius, color):
        """Draw a rounded rectangle"""
        self.create_arc(x1, y1, x1 + radius*2, y1 + radius*2, start=90, extent=90,
                       fill=color, outline=color)
        self.create_arc(x2 - radius*2, y1, x2, y1 + radius*2, start=0, extent=90,
                       fill=color, outline=color)
        self.create_arc(x1, y2 - radius*2, x1 + radius*2, y2, start=180, extent=90,
                       fill=color, outline=color)
        self.create_arc(x2 - radius*2, y2 - radius*2, x2, y2, start=270, extent=90,
                       fill=color, outline=color)

        self.create_rectangle(x1 + radius, y1, x2 - radius, y2, fill=color, outline=color)
        self.create_rectangle(x1, y1 + radius, x2, y2 - radius, fill=color, outline=color)

    def set_active(self, active):
        self.is_active = active
        self._draw()

    def _on_click(self, event):
        if self.command:
            self.command()

    def _on_enter(self, event):
        if not self.is_active:
            self._draw(hover=True)

    def _on_leave(self, event):
        self._draw()


class TwitterDownloaderGUI:
    """Main GUI Application with cute beige theme and scroll support"""

    def __init__(self, root):
        self.root = root
        self.root.title("Twitter Video Downloader")
        self.root.geometry("720x750")
        self.root.minsize(500, 500)  # Allow smaller minimum size
        self.root.configure(bg=Colors.BG_MAIN)

        # Language setting
        self.lang = "en"
        self.current_tab = "video"

        # Center window
        self._center_window()

        # State
        self.log_queue = queue.Queue()
        self.is_downloading = False
        self.download_thread = None
        self.default_output_dir = str(Path.cwd() / "twitter_videos")
        self.original_stdout = sys.stdout

        # Setup
        self._setup_ui()
        self._update_log_display()

    def _center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        w, h = 720, 750
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    def _t(self, key):
        """Get translated string"""
        lang_dict = Language.ZH if self.lang == "zh" else Language.EN
        return lang_dict.get(key, key)

    def _toggle_language(self):
        """Toggle between English and Chinese"""
        self.lang = "zh" if self.lang == "en" else "en"
        self.lang_btn.config(text=self._t("lang_switch"))
        self._refresh_ui()

    def _switch_tab(self, tab_name):
        """Switch between tabs"""
        self.current_tab = tab_name

        if tab_name == "video":
            self.video_tab_btn.set_active(True)
            self.bookmark_tab_btn.set_active(False)
            self.video_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
            self.bookmark_frame.pack_forget()
        else:
            self.video_tab_btn.set_active(False)
            self.bookmark_tab_btn.set_active(True)
            self.video_frame.pack_forget()
            self.bookmark_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        # Update scroll region
        self.root.after(100, self._update_scroll_region)

    def _update_scroll_region(self):
        """Update the scroll region to fit content"""
        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        """Handle canvas resize"""
        self.canvas.itemconfig(self.scroll_frame_id, width=event.width)

    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _refresh_ui(self):
        """Refresh UI with current language"""
        self.root.title(self._t("title"))
        self.title_label.config(text="🐦 " + self._t("title"))
        self.status_var.set(self._t("ready"))

        # Update tab buttons
        self.video_tab_btn.text = self._t("tab_video")
        self.video_tab_btn._draw()
        self.bookmark_tab_btn.text = self._t("tab_bookmark")
        self.bookmark_tab_btn._draw()

        # Update video tab
        self.url_label.config(text=self._t("tweet_urls"))
        self.load_file_btn.config(text=self._t("load_file"))
        self.settings_label1.config(text=self._t("settings"))
        self.save_to_label1.config(text=self._t("save_to"))
        self.delay_label.config(text=self._t("delay"))
        self.video_start_btn.config(text=self._t("start"))
        self.video_stop_btn.config(text=self._t("stop"))

        # Update bookmark tab
        self.info_label.config(text=self._t("how_to_use"))
        for i, key in enumerate(["step1", "step2", "step3", "step4"]):
            self.step_labels[i].config(text=self._t(key))
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
        current_text = self.url_text.get("1.0", tk.END).strip()
        if current_text.startswith("✏️") or current_text.startswith("在此"):
            self.url_text.delete("1.0", tk.END)
            self.url_text.insert(tk.END, self._t("url_placeholder"))

    def _setup_ui(self):
        """Setup the main user interface with scroll support"""
        # Main container with canvas for scrolling
        self.main_frame = tk.Frame(self.root, bg=Colors.BG_MAIN)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Create canvas and scrollbar
        self.canvas = tk.Canvas(self.main_frame, bg=Colors.BG_MAIN, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.main_frame, orient="vertical", command=self.canvas.yview)

        # Scrollable frame
        self.scrollable_frame = tk.Frame(self.canvas, bg=Colors.BG_MAIN)

        self.scroll_frame_id = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        # Configure canvas
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Pack scrollbar and canvas
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Bind events
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.scrollable_frame.bind("<Configure>", lambda e: self._update_scroll_region())

        # Mouse wheel scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # Content container with padding
        content_frame = tk.Frame(self.scrollable_frame, bg=Colors.BG_MAIN)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Header
        self._create_header(content_frame)

        # Tab buttons
        self._create_tab_buttons(content_frame)

        # Content frames (will be shown/hidden based on tab selection)
        self.content_area = tk.Frame(content_frame, bg=Colors.BG_MAIN)
        self.content_area.pack(fill=tk.BOTH, expand=True)

        self._create_video_tab()
        self._create_bookmark_tab()

        # Show video tab by default
        self.video_frame.pack(in_=self.content_area, fill=tk.BOTH, expand=True, pady=(10, 0))

        # Log area (always visible at bottom)
        self._create_log_area(content_frame)

        # Footer
        self._create_footer(content_frame)

    def _create_header(self, parent):
        """Create header section"""
        header = tk.Frame(parent, bg=Colors.BG_MAIN)
        header.pack(fill=tk.X)

        title_frame = tk.Frame(header, bg=Colors.BG_MAIN)
        title_frame.pack(fill=tk.X)

        # Cute title with emoji
        self.title_label = tk.Label(
            title_frame,
            text="🐦 " + self._t("title"),
            font=("Segoe UI", 20, "bold"),
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
            fg=Colors.TEXT_WHITE,
            activebackground=Colors.SECONDARY,
            activeforeground=Colors.TEXT_WHITE,
            relief=tk.FLAT,
            padx=18,
            pady=6,
            cursor="hand2",
            command=self._toggle_language
        )
        self.lang_btn.pack(side=tk.RIGHT)

        # Status
        self.status_var = tk.StringVar(value=self._t("ready"))
        self.status_label = tk.Label(
            header,
            textvariable=self.status_var,
            font=("Segoe UI", 11),
            bg=Colors.BG_MAIN,
            fg=Colors.TEXT_SECONDARY
        )
        self.status_label.pack(anchor=tk.W, pady=(8, 0))

    def _create_tab_buttons(self, parent):
        """Create custom tab buttons"""
        tab_frame = tk.Frame(parent, bg=Colors.BG_MAIN)
        tab_frame.pack(fill=tk.X, pady=(15, 0))

        self.video_tab_btn = TabButton(
            tab_frame,
            text=self._t("tab_video"),
            command=lambda: self._switch_tab("video"),
            bg=Colors.BG_MAIN
        )
        self.video_tab_btn.pack(side=tk.LEFT, padx=(0, 10))
        self.video_tab_btn.set_active(True)

        self.bookmark_tab_btn = TabButton(
            tab_frame,
            text=self._t("tab_bookmark"),
            command=lambda: self._switch_tab("bookmark"),
            bg=Colors.BG_MAIN
        )
        self.bookmark_tab_btn.pack(side=tk.LEFT)

    def _create_video_tab(self):
        """Create video download tab"""
        self.video_frame = tk.Frame(bg=Colors.BG_CARD)

        # URL Input Section
        url_frame = tk.LabelFrame(self.video_frame, text="", bg=Colors.BG_CARD,
                                  font=("Segoe UI", 11, "bold"), fg=Colors.PRIMARY)
        url_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10), padx=5)

        self.url_label = tk.Label(url_frame, text=self._t("tweet_urls"),
                                  font=("Segoe UI", 11, "bold"),
                                  bg=Colors.BG_CARD, fg=Colors.PRIMARY)
        self.url_label.pack(anchor=tk.W, padx=10, pady=(5, 0))

        self.url_text = scrolledtext.ScrolledText(
            url_frame,
            height=4,
            wrap=tk.WORD,
            font=("Segoe UI", 10),
            bg=Colors.BG_INPUT,
            fg=Colors.TEXT_PRIMARY,
            insertbackground=Colors.TEXT_PRIMARY,
            selectbackground=Colors.SECONDARY,
            relief=tk.FLAT,
            borderwidth=0,
            padx=12,
            pady=10
        )
        self.url_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.url_text.insert(tk.END, self._t("url_placeholder"))
        self.url_text.configure(foreground=Colors.TEXT_LIGHT)
        self.url_text.bind("<FocusIn>", self._on_url_focus_in)
        self.url_text.bind("<FocusOut>", self._on_url_focus_out)

        file_frame = tk.Frame(url_frame, bg=Colors.BG_CARD)
        file_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        self.load_file_btn = tk.Button(
            file_frame, text=self._t("load_file"),
            font=("Segoe UI", 9),
            bg=Colors.SECONDARY,
            fg=Colors.TEXT_WHITE,
            activebackground=Colors.PRIMARY,
            activeforeground=Colors.TEXT_WHITE,
            relief=tk.FLAT, padx=12, pady=6, cursor="hand2",
            command=self.load_urls_from_file
        )
        self.load_file_btn.pack(side=tk.LEFT)

        self.url_file_label = tk.Label(file_frame, text="", font=("Segoe UI", 9),
                                       bg=Colors.BG_CARD, fg=Colors.SUCCESS)
        self.url_file_label.pack(side=tk.LEFT, padx=10)

        # Settings Section
        settings_frame = tk.LabelFrame(self.video_frame, text="", bg=Colors.BG_CARD,
                                       font=("Segoe UI", 11, "bold"), fg=Colors.PRIMARY)
        settings_frame.pack(fill=tk.X, pady=(0, 10), padx=5)

        self.settings_label1 = tk.Label(settings_frame, text=self._t("settings"),
                                        font=("Segoe UI", 11, "bold"),
                                        bg=Colors.BG_CARD, fg=Colors.PRIMARY)
        self.settings_label1.pack(anchor=tk.W, padx=10, pady=(5, 0))

        dir_row = tk.Frame(settings_frame, bg=Colors.BG_CARD)
        dir_row.pack(fill=tk.X, padx=10, pady=8)

        self.save_to_label1 = tk.Label(dir_row, text=self._t("save_to"),
                                       font=("Segoe UI", 10),
                                       bg=Colors.BG_CARD, fg=Colors.TEXT_PRIMARY)
        self.save_to_label1.pack(side=tk.LEFT)
        self.video_output_var = tk.StringVar(value=self.default_output_dir)
        entry = tk.Entry(dir_row, textvariable=self.video_output_var, width=30,
                        font=("Segoe UI", 10), bg=Colors.BG_INPUT, fg=Colors.TEXT_PRIMARY,
                        insertbackground=Colors.TEXT_PRIMARY, relief=tk.FLAT)
        entry.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        browse_btn = tk.Button(
            dir_row, text="Browse",
            font=("Segoe UI", 9),
            bg=Colors.BG_TAB,
            fg=Colors.TEXT_PRIMARY,
            activebackground=Colors.SECONDARY,
            activeforeground=Colors.TEXT_WHITE,
            relief=tk.FLAT, padx=10, pady=5, cursor="hand2",
            command=lambda: self._browse_directory(self.video_output_var)
        )
        browse_btn.pack(side=tk.LEFT)

        delay_row = tk.Frame(settings_frame, bg=Colors.BG_CARD)
        delay_row.pack(fill=tk.X, padx=10, pady=(0, 8))

        self.delay_label = tk.Label(delay_row, text=self._t("delay"),
                                    font=("Segoe UI", 10),
                                    bg=Colors.BG_CARD, fg=Colors.TEXT_PRIMARY)
        self.delay_label.pack(side=tk.LEFT)
        self.video_delay_var = tk.StringVar(value="0.5")
        tk.Entry(delay_row, textvariable=self.video_delay_var, width=8,
                font=("Segoe UI", 10), bg=Colors.BG_INPUT, fg=Colors.TEXT_PRIMARY,
                insertbackground=Colors.TEXT_PRIMARY, relief=tk.FLAT).pack(side=tk.LEFT, padx=10)

        # Action buttons
        btn_frame = tk.Frame(self.video_frame, bg=Colors.BG_CARD)
        btn_frame.pack(fill=tk.X, padx=5, pady=(0, 10))

        self.video_start_btn = tk.Button(
            btn_frame, text=self._t("start"),
            font=("Segoe UI", 12, "bold"),
            bg=Colors.PRIMARY,
            fg=Colors.TEXT_WHITE,
            activebackground=Colors.SECONDARY,
            activeforeground=Colors.TEXT_WHITE,
            relief=tk.FLAT,
            padx=30,
            pady=12,
            cursor="hand2",
            command=self.start_video_download
        )
        self.video_start_btn.pack(side=tk.LEFT, padx=(10, 10))

        self.video_stop_btn = tk.Button(
            btn_frame, text=self._t("stop"),
            font=("Segoe UI", 10),
            bg=Colors.ERROR,
            fg=Colors.TEXT_WHITE,
            activebackground=Colors.WARNING,
            activeforeground=Colors.TEXT_PRIMARY,
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
        self.bookmark_frame = tk.Frame(bg=Colors.BG_CARD)

        # Info Section
        info_frame = tk.LabelFrame(self.bookmark_frame, text="", bg=Colors.BG_CARD,
                                   font=("Segoe UI", 11, "bold"), fg=Colors.PRIMARY)
        info_frame.pack(fill=tk.X, pady=(0, 10), padx=5)

        self.info_label = tk.Label(info_frame, text=self._t("how_to_use"),
                                   font=("Segoe UI", 11, "bold"),
                                   bg=Colors.BG_CARD, fg=Colors.PRIMARY)
        self.info_label.pack(anchor=tk.W, padx=10, pady=(5, 0))

        info_container = tk.Frame(info_frame, bg=Colors.BG_CARD)
        info_container.pack(fill=tk.X, padx=10, pady=10)

        self.step_labels = []
        for key in ["step1", "step2", "step3", "step4"]:
            label = tk.Label(
                info_container, text=self._t(key),
                font=("Segoe UI", 10),
                bg=Colors.BG_CARD, fg=Colors.TEXT_SECONDARY,
                anchor=tk.W, justify=tk.LEFT
            )
            label.pack(anchor=tk.W, pady=2)
            self.step_labels.append(label)

        # Settings Section
        settings_frame = tk.LabelFrame(self.bookmark_frame, text="", bg=Colors.BG_CARD,
                                       font=("Segoe UI", 11, "bold"), fg=Colors.PRIMARY)
        settings_frame.pack(fill=tk.X, pady=(0, 10), padx=5)

        self.settings_label2 = tk.Label(settings_frame, text=self._t("settings"),
                                        font=("Segoe UI", 11, "bold"),
                                        bg=Colors.BG_CARD, fg=Colors.PRIMARY)
        self.settings_label2.pack(anchor=tk.W, padx=10, pady=(5, 0))

        dir_row = tk.Frame(settings_frame, bg=Colors.BG_CARD)
        dir_row.pack(fill=tk.X, padx=10, pady=8)

        self.save_to_label2 = tk.Label(dir_row, text=self._t("save_to"),
                                       font=("Segoe UI", 10),
                                       bg=Colors.BG_CARD, fg=Colors.TEXT_PRIMARY)
        self.save_to_label2.pack(side=tk.LEFT)
        self.bookmark_output_var = tk.StringVar(value=self.default_output_dir)
        tk.Entry(dir_row, textvariable=self.bookmark_output_var, width=30,
                font=("Segoe UI", 10), bg=Colors.BG_INPUT, fg=Colors.TEXT_PRIMARY,
                insertbackground=Colors.TEXT_PRIMARY, relief=tk.FLAT).pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        browse_btn = tk.Button(
            dir_row, text="Browse",
            font=("Segoe UI", 9),
            bg=Colors.BG_TAB,
            fg=Colors.TEXT_PRIMARY,
            activebackground=Colors.SECONDARY,
            activeforeground=Colors.TEXT_WHITE,
            relief=tk.FLAT, padx=10, pady=5, cursor="hand2",
            command=lambda: self._browse_directory(self.bookmark_output_var)
        )
        browse_btn.pack(side=tk.LEFT)

        browser_row = tk.Frame(settings_frame, bg=Colors.BG_CARD)
        browser_row.pack(fill=tk.X, padx=10, pady=5)

        self.browser_label = tk.Label(browser_row, text=self._t("browser"),
                                      font=("Segoe UI", 10),
                                      bg=Colors.BG_CARD, fg=Colors.TEXT_PRIMARY)
        self.browser_label.pack(side=tk.LEFT)
        self.browser_var = tk.StringVar(value="auto")
        self.auto_radio = tk.Radiobutton(browser_row, text=self._t("auto"),
                                         variable=self.browser_var, value="auto",
                                         bg=Colors.BG_CARD, fg=Colors.TEXT_PRIMARY,
                                         selectcolor=Colors.BG_INPUT,
                                         activebackground=Colors.BG_CARD,
                                         font=("Segoe UI", 10))
        self.auto_radio.pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(browser_row, text="Chrome", variable=self.browser_var, value="chrome",
                       bg=Colors.BG_CARD, fg=Colors.TEXT_PRIMARY,
                       selectcolor=Colors.BG_INPUT, activebackground=Colors.BG_CARD,
                       font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(browser_row, text="Edge", variable=self.browser_var, value="edge",
                       bg=Colors.BG_CARD, fg=Colors.TEXT_PRIMARY,
                       selectcolor=Colors.BG_INPUT, activebackground=Colors.BG_CARD,
                       font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=5)

        limits_row1 = tk.Frame(settings_frame, bg=Colors.BG_CARD)
        limits_row1.pack(fill=tk.X, padx=10, pady=5)

        self.max_tweets_label = tk.Label(limits_row1, text=self._t("max_tweets"),
                                         font=("Segoe UI", 10),
                                         bg=Colors.BG_CARD, fg=Colors.TEXT_PRIMARY)
        self.max_tweets_label.pack(side=tk.LEFT)
        self.max_tweets_var = tk.StringVar(value="")
        tk.Entry(limits_row1, textvariable=self.max_tweets_var, width=6,
                font=("Segoe UI", 10), bg=Colors.BG_INPUT, fg=Colors.TEXT_PRIMARY,
                insertbackground=Colors.TEXT_PRIMARY, relief=tk.FLAT).pack(side=tk.LEFT, padx=(5, 15))

        self.max_scrolls_label = tk.Label(limits_row1, text=self._t("max_scrolls"),
                                          font=("Segoe UI", 10),
                                          bg=Colors.BG_CARD, fg=Colors.TEXT_PRIMARY)
        self.max_scrolls_label.pack(side=tk.LEFT)
        self.max_scrolls_var = tk.StringVar(value="")
        tk.Entry(limits_row1, textvariable=self.max_scrolls_var, width=6,
                font=("Segoe UI", 10), bg=Colors.BG_INPUT, fg=Colors.TEXT_PRIMARY,
                insertbackground=Colors.TEXT_PRIMARY, relief=tk.FLAT).pack(side=tk.LEFT, padx=5)

        limits_row2 = tk.Frame(settings_frame, bg=Colors.BG_CARD)
        limits_row2.pack(fill=tk.X, padx=10, pady=5)

        self.max_size_label = tk.Label(limits_row2, text=self._t("max_size"),
                                       font=("Segoe UI", 10),
                                       bg=Colors.BG_CARD, fg=Colors.TEXT_PRIMARY)
        self.max_size_label.pack(side=tk.LEFT)
        self.max_size_var = tk.StringVar(value="1500")
        tk.Entry(limits_row2, textvariable=self.max_size_var, width=6,
                font=("Segoe UI", 10), bg=Colors.BG_INPUT, fg=Colors.TEXT_PRIMARY,
                insertbackground=Colors.TEXT_PRIMARY, relief=tk.FLAT).pack(side=tk.LEFT, padx=(5, 15))

        self.headless_var = tk.BooleanVar(value=False)
        self.headless_check = tk.Checkbutton(limits_row2, text=self._t("hide_browser"),
                                             variable=self.headless_var,
                                             bg=Colors.BG_CARD, fg=Colors.TEXT_PRIMARY,
                                             selectcolor=Colors.BG_INPUT,
                                             activebackground=Colors.BG_CARD,
                                             font=("Segoe UI", 10))
        self.headless_check.pack(side=tk.LEFT)

        # Action buttons
        btn_frame = tk.Frame(self.bookmark_frame, bg=Colors.BG_CARD)
        btn_frame.pack(fill=tk.X, padx=5, pady=(0, 10))

        self.bookmark_start_btn = tk.Button(
            btn_frame, text=self._t("start"),
            font=("Segoe UI", 12, "bold"),
            bg=Colors.SUCCESS,
            fg=Colors.TEXT_WHITE,
            activebackground=Colors.SECONDARY,
            activeforeground=Colors.TEXT_WHITE,
            relief=tk.FLAT,
            padx=30,
            pady=12,
            cursor="hand2",
            command=self.start_bookmark_download
        )
        self.bookmark_start_btn.pack(side=tk.LEFT, padx=(10, 10))

        self.bookmark_stop_btn = tk.Button(
            btn_frame, text=self._t("stop"),
            font=("Segoe UI", 10),
            bg=Colors.ERROR,
            fg=Colors.TEXT_WHITE,
            activebackground=Colors.WARNING,
            activeforeground=Colors.TEXT_PRIMARY,
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor="hand2",
            command=self.stop_download,
            state=tk.DISABLED
        )
        self.bookmark_stop_btn.pack(side=tk.LEFT)

    def _create_log_area(self, parent):
        """Create log output area"""
        log_frame = tk.LabelFrame(parent, text="", bg=Colors.BG_CARD,
                                  font=("Segoe UI", 11, "bold"), fg=Colors.PRIMARY)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(15, 0))

        self.log_label = tk.Label(log_frame, text=self._t("log"),
                                  font=("Segoe UI", 11, "bold"),
                                  bg=Colors.BG_CARD, fg=Colors.PRIMARY)
        self.log_label.pack(anchor=tk.W, padx=10, pady=(5, 0))

        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=10,
            wrap=tk.WORD,
            font=("Consolas", 10),
            bg=Colors.BG_INPUT,
            fg=Colors.TEXT_PRIMARY,
            insertbackground=Colors.TEXT_PRIMARY,
            selectbackground=Colors.SECONDARY,
            relief=tk.FLAT,
            borderwidth=0,
            padx=12,
            pady=10,
            state=tk.DISABLED
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Configure text tags for colored output
        self.log_text.tag_config("success", foreground=Colors.SUCCESS)
        self.log_text.tag_config("error", foreground=Colors.ERROR)
        self.log_text.tag_config("warning", foreground=Colors.WARNING)
        self.log_text.tag_config("info", foreground=Colors.INFO)
        self.log_text.tag_config("progress", foreground=Colors.PRIMARY)
        self.log_text.tag_config("highlight", foreground=Colors.PURPLE)

    def _create_footer(self, parent):
        """Create footer with action buttons"""
        footer = tk.Frame(parent, bg=Colors.BG_MAIN)
        footer.pack(fill=tk.X, pady=(12, 0))

        self.open_folder_btn = tk.Button(
            footer, text=self._t("open_folder"),
            font=("Segoe UI", 9),
            bg=Colors.BG_TAB,
            fg=Colors.TEXT_PRIMARY,
            activebackground=Colors.SECONDARY,
            activeforeground=Colors.TEXT_WHITE,
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
            bg=Colors.BG_TAB,
            fg=Colors.TEXT_PRIMARY,
            activebackground=Colors.SECONDARY,
            activeforeground=Colors.TEXT_WHITE,
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
        if text.startswith("✏️") or text.startswith("在此"):
            self.url_text.delete("1.0", tk.END)
            self.url_text.configure(foreground=Colors.TEXT_PRIMARY)

    def _on_url_focus_out(self, event):
        """Handle URL text area focus out"""
        if not self.url_text.get("1.0", tk.END).strip():
            self.url_text.insert(tk.END, self._t("url_placeholder"))
            self.url_text.configure(foreground=Colors.TEXT_LIGHT)

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
        output_dir = self.video_output_var.get() if self.current_tab == "video" else self.bookmark_output_var.get()

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
        if "success" in text_lower or "✓" in text or "saved" in text_lower or "完成" in text:
            return "success"
        elif "error" in text_lower or "✗" in text or "failed" in text_lower or "错误" in text:
            return "error"
        elif "warning" in text_lower or "skipped" in text_lower or "跳过" in text:
            return "warning"
        elif "progress" in text_lower or "%" in text or "进度" in text:
            return "progress"
        elif "starting" in text_lower or "downloading" in text_lower or "processing" in text_lower or "开始" in text or "下载" in text:
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
            self.video_start_btn.config(state=tk.DISABLED, bg=Colors.TEXT_LIGHT)
            self.video_stop_btn.config(state=tk.NORMAL)
            self.bookmark_start_btn.config(state=tk.DISABLED, bg=Colors.TEXT_LIGHT)
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

        if url_text.startswith("✏️") or url_text.startswith("在此"):
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

    app = TwitterDownloaderGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
