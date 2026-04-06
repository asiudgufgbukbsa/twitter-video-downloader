#!/usr/bin/env python3
"""
Twitter/X Video Downloader GUI
A modern, clean graphical user interface
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


class ModernStyle:
    """Modern color scheme and fonts"""
    # Colors
    BG_PRIMARY = "#ffffff"
    BG_SECONDARY = "#f8f9fa"
    BG_TERTIARY = "#e9ecef"
    ACCENT = "#1da1f2"  # Twitter blue
    ACCENT_HOVER = "#1a91da"
    TEXT_PRIMARY = "#14171a"
    TEXT_SECONDARY = "#657786"
    SUCCESS = "#17bf63"
    ERROR = "#e0245e"
    WARNING = "#ffad1f"
    BORDER = "#e1e8ed"

    # Fonts
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
    """Main GUI Application with modern design"""

    def __init__(self, root):
        self.root = root
        self.root.title("Twitter Video Downloader")
        self.root.geometry("650x700")
        self.root.minsize(550, 550)
        self.root.configure(bg=ModernStyle.BG_PRIMARY)

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
        w, h = 650, 700
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    def _setup_styles(self):
        """Configure ttk styles"""
        style = ttk.Style()

        # Frame styles
        style.configure("Card.TFrame", background=ModernStyle.BG_PRIMARY)
        style.configure("Secondary.TFrame", background=ModernStyle.BG_SECONDARY)

        # Label styles
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

        # Button styles
        style.configure("Accent.TButton",
                       font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_NORMAL, "bold"),
                       padding=(20, 10))

        style.configure("Small.TButton",
                       font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SMALL),
                       padding=(10, 5))

        # Notebook styles
        style.configure("TNotebook", background=ModernStyle.BG_PRIMARY)
        style.configure("TNotebook.Tab",
                       font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_NORMAL),
                       padding=(20, 10))

        # Entry styles
        style.configure("TEntry",
                       fieldbackground=ModernStyle.BG_SECONDARY,
                       bordercolor=ModernStyle.BORDER)

        # Radiobutton styles
        style.configure("TRadiobutton",
                       font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_NORMAL),
                       background=ModernStyle.BG_PRIMARY)

        # Checkbutton styles
        style.configure("TCheckbutton",
                       font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_SMALL),
                       background=ModernStyle.BG_PRIMARY)

        # LabelFrame styles
        style.configure("Card.TLabelframe",
                       background=ModernStyle.BG_PRIMARY)
        style.configure("Card.TLabelframe.Label",
                       font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_NORMAL, "bold"),
                       background=ModernStyle.BG_PRIMARY,
                       foreground=ModernStyle.TEXT_PRIMARY)

    def _setup_ui(self):
        """Setup the main user interface"""
        # Main container
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

        # Title with icon
        title_frame = ttk.Frame(header, style="Card.TFrame")
        title_frame.pack(fill=tk.X)

        ttk.Label(title_frame, text="🐦", font=("Segoe UI Emoji", 24)).pack(side=tk.LEFT)
        ttk.Label(title_frame, text="  Twitter Video Downloader", style="Title.TLabel").pack(side=tk.LEFT)

        # Status
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(header, textvariable=self.status_var, style="Subtitle.TLabel").pack(anchor=tk.W, pady=(5, 0))

    def _create_video_tab(self):
        """Create video download tab"""
        frame = ttk.Frame(self.notebook, style="Card.TFrame", padding=15)
        self.notebook.add(frame, text="  📹 Video URL  ")

        # URL Input Section
        url_section = ttk.LabelFrame(frame, text="Tweet URLs", style="Card.TLabelframe", padding=10)
        url_section.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # URL text area with placeholder
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
        self.url_text.insert(tk.END, "Paste tweet URLs here, one per line...\n在此粘贴推文链接，每行一个...")
        self.url_text.configure(foreground=ModernStyle.TEXT_SECONDARY)
        self.url_text.bind("<FocusIn>", self._on_url_focus_in)
        self.url_text.bind("<FocusOut>", self._on_url_focus_out)

        # File load button
        file_frame = ttk.Frame(url_section, style="Card.TFrame")
        file_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(file_frame, text="📁 Load from file", style="Small.TButton",
                  command=self.load_urls_from_file).pack(side=tk.LEFT)
        self.url_file_label = ttk.Label(file_frame, text="", style="Info.TLabel")
        self.url_file_label.pack(side=tk.LEFT, padx=10)

        # Settings Section
        settings_section = ttk.LabelFrame(frame, text="Settings", style="Card.TLabelframe", padding=10)
        settings_section.pack(fill=tk.X, pady=(0, 15))

        # Output directory
        dir_row = ttk.Frame(settings_section, style="Card.TFrame")
        dir_row.pack(fill=tk.X, pady=5)

        ttk.Label(dir_row, text="📁 Save to:", style="Setting.TLabel").pack(side=tk.LEFT)
        self.video_output_var = tk.StringVar(value=self.default_output_dir)
        ttk.Entry(dir_row, textvariable=self.video_output_var, width=40).pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        ttk.Button(dir_row, text="Browse", style="Small.TButton",
                  command=lambda: self._browse_directory(self.video_output_var)).pack(side=tk.LEFT)

        # Delay
        delay_row = ttk.Frame(settings_section, style="Card.TFrame")
        delay_row.pack(fill=tk.X, pady=5)

        ttk.Label(delay_row, text="⏱ Delay (sec):", style="Setting.TLabel").pack(side=tk.LEFT)
        self.video_delay_var = tk.StringVar(value="0.5")
        ttk.Entry(delay_row, textvariable=self.video_delay_var, width=8).pack(side=tk.LEFT, padx=10)

        # Action buttons
        btn_frame = ttk.Frame(frame, style="Card.TFrame")
        btn_frame.pack(fill=tk.X)

        self.video_start_btn = ttk.Button(btn_frame, text="▶ Start Download",
                                          style="Accent.TButton", command=self.start_video_download)
        self.video_start_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.video_stop_btn = ttk.Button(btn_frame, text="⏹ Stop",
                                         style="Small.TButton", command=self.stop_download, state=tk.DISABLED)
        self.video_stop_btn.pack(side=tk.LEFT)

    def _create_bookmark_tab(self):
        """Create bookmark download tab"""
        frame = ttk.Frame(self.notebook, style="Card.TFrame", padding=15)
        self.notebook.add(frame, text="  🔖 Bookmarks  ")

        # Info Section
        info_section = ttk.LabelFrame(frame, text="How to use", style="Card.TLabelframe", padding=10)
        info_section.pack(fill=tk.X, pady=(0, 10))

        info_text = (
            "1️⃣  Login to Twitter/X in Chrome or Edge\n"
            "2️⃣  Close all browser windows before starting\n"
            "3️⃣  Click Start and wait for browser to open\n"
            "4️⃣  Login if needed, then press Enter in terminal"
        )
        ttk.Label(info_section, text=info_text, style="Info.TLabel", justify=tk.LEFT).pack(anchor=tk.W)

        # Settings Section
        settings_section = ttk.LabelFrame(frame, text="Settings", style="Card.TLabelframe", padding=10)
        settings_section.pack(fill=tk.X, pady=(0, 15))

        # Output directory
        dir_row = ttk.Frame(settings_section, style="Card.TFrame")
        dir_row.pack(fill=tk.X, pady=5)

        ttk.Label(dir_row, text="📁 Save to:", style="Setting.TLabel").pack(side=tk.LEFT)
        self.bookmark_output_var = tk.StringVar(value=self.default_output_dir)
        ttk.Entry(dir_row, textvariable=self.bookmark_output_var, width=40).pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        ttk.Button(dir_row, text="Browse", style="Small.TButton",
                  command=lambda: self._browse_directory(self.bookmark_output_var)).pack(side=tk.LEFT)

        # Browser selection
        browser_row = ttk.Frame(settings_section, style="Card.TFrame")
        browser_row.pack(fill=tk.X, pady=5)

        ttk.Label(browser_row, text="🌐 Browser:", style="Setting.TLabel").pack(side=tk.LEFT)
        self.browser_var = tk.StringVar(value="auto")
        ttk.Radiobutton(browser_row, text="Auto", variable=self.browser_var, value="auto").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(browser_row, text="Chrome", variable=self.browser_var, value="chrome").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(browser_row, text="Edge", variable=self.browser_var, value="edge").pack(side=tk.LEFT, padx=5)

        # Limits row 1
        limits_row1 = ttk.Frame(settings_section, style="Card.TFrame")
        limits_row1.pack(fill=tk.X, pady=5)

        ttk.Label(limits_row1, text="📊 Max tweets:", style="Setting.TLabel").pack(side=tk.LEFT)
        self.max_tweets_var = tk.StringVar(value="")
        ttk.Entry(limits_row1, textvariable=self.max_tweets_var, width=8).pack(side=tk.LEFT, padx=(5, 20))

        ttk.Label(limits_row1, text="🔄 Max scrolls:", style="Setting.TLabel").pack(side=tk.LEFT)
        self.max_scrolls_var = tk.StringVar(value="")
        ttk.Entry(limits_row1, textvariable=self.max_scrolls_var, width=8).pack(side=tk.LEFT, padx=5)

        # Limits row 2
        limits_row2 = ttk.Frame(settings_section, style="Card.TFrame")
        limits_row2.pack(fill=tk.X, pady=5)

        ttk.Label(limits_row2, text="💾 Max size (MB):", style="Setting.TLabel").pack(side=tk.LEFT)
        self.max_size_var = tk.StringVar(value="1500")
        ttk.Entry(limits_row2, textvariable=self.max_size_var, width=8).pack(side=tk.LEFT, padx=(5, 20))

        self.headless_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(limits_row2, text="Hide browser window", variable=self.headless_var).pack(side=tk.LEFT)

        # Action buttons
        btn_frame = ttk.Frame(frame, style="Card.TFrame")
        btn_frame.pack(fill=tk.X)

        self.bookmark_start_btn = ttk.Button(btn_frame, text="▶ Start Download",
                                             style="Accent.TButton", command=self.start_bookmark_download)
        self.bookmark_start_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.bookmark_stop_btn = ttk.Button(btn_frame, text="⏹ Stop",
                                            style="Small.TButton", command=self.stop_download, state=tk.DISABLED)
        self.bookmark_stop_btn.pack(side=tk.LEFT)

    def _create_log_area(self, parent):
        """Create log output area"""
        log_section = ttk.LabelFrame(parent, text="📝 Log", style="Card.TLabelframe", padding=10)
        log_section.pack(fill=tk.BOTH, expand=True, pady=(15, 0))

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

        ttk.Button(footer, text="📂 Open Output Folder", style="Small.TButton",
                  command=self.open_output_folder).pack(side=tk.LEFT)
        ttk.Button(footer, text="🗑 Clear Log", style="Small.TButton",
                  command=self.clear_log).pack(side=tk.RIGHT)

    def _on_url_focus_in(self, event):
        """Handle URL text area focus in"""
        if self.url_text.get("1.0", tk.END).strip().startswith("Paste tweet"):
            self.url_text.delete("1.0", tk.END)
            self.url_text.configure(foreground=ModernStyle.TEXT_PRIMARY)

    def _on_url_focus_out(self, event):
        """Handle URL text area focus out"""
        if not self.url_text.get("1.0", tk.END).strip():
            self.url_text.insert(tk.END, "Paste tweet URLs here, one per line...\n在此粘贴推文链接，每行一个...")
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
                self.url_file_label.config(text=f"Loaded {len(urls)} URLs")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file:\n{e}")

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
            self.status_var.set("Downloading...")
        else:
            self.video_start_btn.config(state=tk.NORMAL)
            self.video_stop_btn.config(state=tk.DISABLED)
            self.bookmark_start_btn.config(state=tk.NORMAL)
            self.bookmark_stop_btn.config(state=tk.DISABLED)
            self.status_var.set("Ready")

    def stop_download(self):
        """Stop the current download"""
        if self.download_thread and self.download_thread.is_alive():
            self.log_queue.put("\n⏹ Stopping download...\n")
            self.is_downloading = False
            self._set_downloading_state(False)
            self.status_var.set("Stopped")

    def start_video_download(self):
        """Start video download"""
        url_text = self.url_text.get("1.0", tk.END).strip()

        # Check for placeholder text
        if url_text.startswith("Paste tweet"):
            url_text = ""

        urls = [line.strip() for line in url_text.split('\n') if line.strip()]

        if not urls:
            messagebox.showwarning("Warning", "Please enter at least one URL")
            return

        try:
            delay = float(self.video_delay_var.get())
        except ValueError:
            messagebox.showwarning("Warning", "Invalid delay value")
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
            messagebox.showwarning("Warning", "Invalid max tweets value")
            return

        try:
            max_scrolls = int(self.max_scrolls_var.get()) if self.max_scrolls_var.get() else 999999
        except ValueError:
            messagebox.showwarning("Warning", "Invalid max scrolls value")
            return

        try:
            max_size = float(self.max_size_var.get())
        except ValueError:
            messagebox.showwarning("Warning", "Invalid max size value")
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

    # Try to set window icon
    try:
        root.iconbitmap(default='')
    except:
        pass

    # Apply theme
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
