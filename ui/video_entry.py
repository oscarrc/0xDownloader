"""
Video entry component for the YouTube Downloader application.
"""

import threading
import tkinter as tk
import customtkinter as ctk
from customtkinter import CTkImage
from PIL import Image
import requests
from io import BytesIO

from core.video_info import (
    fetch_video_info, 
    extract_resolution_options, 
    extract_audio_language_options,
    extract_subtitle_options,
    extract_format_options
)
from core.downloader import download_video
from core.utils import sanitize_filename
from core.localization import localization
from config import THUMBNAIL_HEIGHT, THUMBNAIL_WIDTH


class VideoEntry:
    """Represents a single video entry in the download queue."""
    
    def __init__(self, parent_frame, url, output_dir, download_queue, main_window=None):
        self.parent_frame = parent_frame
        self.url = url
        self.output_dir = output_dir
        self.download_queue = download_queue
        self.main_window = main_window
        
        # Create the main frame
        self.frame = ctk.CTkFrame(parent_frame, corner_radius=8, fg_color="#2a2a2a")
        self.frame.pack(fill="x", pady=5, padx=5)
        
        # Create UI components
        self._create_thumbnail()
        self._create_content_area()
        self._create_progress_area()
        
        # Initialize entry data
        self.entry_data = {
            "url": url,
            "frame": self.frame,
            "thumb_label": self.thumb_label,
            "title_label": self.title_label,
            "progress": self.progress,
            "progress_label": self.progress_label,
            "status_label": self.status_label,
            "download_btn": None,
            "res_var": None,
            "format_var": None,
            "audio_var": None,
            "subs_var": None
        }
        
        # Add to download queue
        self.download_queue.append(self.entry_data)
        
        # Start loading video info
        self._load_video_info()
    
    def _create_thumbnail(self):
        """Create the thumbnail display area."""
        self.thumb_label = ctk.CTkLabel(
            self.frame, 
            text=localization.get("video.loading_image", "Loading image..."), 
            width=THUMBNAIL_WIDTH, 
            height=THUMBNAIL_HEIGHT, 
            fg_color="#1f1f1f"
        )
        self.thumb_label.pack(side="left", padx=5, pady=5)
    
    def _create_content_area(self):
        """Create the main content area."""
        self.content_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        self.content_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        # Title label
        self.title_label = ctk.CTkLabel(self.content_frame, text=localization.get("video.loading", "Loading..."))
        self.title_label.pack(anchor="w", pady=2)
    
    def _create_progress_area(self):
        """Create the progress tracking area."""
        # Status and progress bar layout
        self.status_progress_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.status_progress_frame.pack(fill="x", pady=2)

        # Top row: Status and progress percentage
        self.top_row = ctk.CTkFrame(self.status_progress_frame, fg_color="transparent")
        self.top_row.pack(fill="x", pady=(0,2))

        # Left side: Status
        self.status_label = ctk.CTkLabel(self.top_row, text=localization.get("video.waiting", "Waiting"), width=20, anchor="w")
        self.status_label.pack(side="left")

        # Right side: Progress percentage
        self.progress_label = ctk.CTkLabel(self.top_row, text="0%", width=10, anchor="e")
        self.progress_label.pack(side="right")

        # Bottom row: Progress bar (full width)
        self.progress = ctk.CTkProgressBar(self.status_progress_frame)
        self.progress.set(0)
        self.progress.pack(fill="x", expand=True, pady=(0, 10))  # Add padding below progress bar

        # Set initial indeterminate state while loading
        self.progress.configure(mode="indeterminate")
        self.progress.start()
    
    def _load_video_info(self):
        """Load video information in a separate thread."""
        def task():
            try:
                info = fetch_video_info(self.url)
                formats = info.get("formats", [])
                
                # Extract options
                resolution_options = extract_resolution_options(formats)
                format_options = extract_format_options(formats)
                audio_options = extract_audio_language_options(formats, info)
                subs_options = extract_subtitle_options(info)
                
                # Load thumbnail
                self._load_thumbnail(info)
                
                # Update UI
                self._update_ui(info, resolution_options, format_options, audio_options, subs_options)
                
            except Exception as e:
                self._handle_error(str(e))
        
        threading.Thread(target=task, daemon=True).start()
    
    def _load_thumbnail(self, info):
        """Load and display the video thumbnail."""
        try:
            resp = requests.get(info.get("thumbnail", ""), timeout=5)
            img_data = resp.content
            img = Image.open(BytesIO(img_data)).resize((THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT))
            ctk_img = CTkImage(light_image=img, dark_image=img, size=(THUMBNAIL_WIDTH, THUMBNAIL_HEIGHT))
            
            def update_thumb():
                self.thumb_label.configure(image=ctk_img, text="")
                self.thumb_label.image = ctk_img
            
            # Schedule UI update on main thread
            self.frame.after(0, update_thumb)
        except:
            pass  # Thumbnail loading is optional
    
    def _update_ui(self, info, resolution_options, format_options, audio_options, subs_options):
        """Update the UI with video information and options."""
        def update():
            # Update title
            self.title_label.configure(text=info.get("title", localization.get("video.error_loading", "Error loading metadata")))
            
            # Stop indeterminate progress and set to normal mode
            self.progress.stop()
            self.progress.configure(mode="determinate")
            self.progress.set(0)
            self.progress_label.configure(text="0%")
            self.status_label.configure(text=localization.get("video.ready", "Ready"))
            
            # Create variables
            self.entry_data["res_var"] = tk.StringVar(value=resolution_options[0])
            self.entry_data["format_var"] = tk.StringVar(value=format_options[0])
            self.entry_data["audio_var"] = tk.StringVar(value=audio_options[0])
            self.entry_data["subs_var"] = tk.StringVar(value=subs_options[0])
            
            # Create selectors and buttons
            self._create_controls(resolution_options, format_options, audio_options, subs_options)
        
        # Schedule UI update on main thread
        self.frame.after(0, update)
    
    def _create_controls(self, resolution_options, format_options, audio_options, subs_options):
        """Create the control selectors and buttons."""
        option_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        option_frame.pack(fill="x", pady=2)
        
        # Selectors
        ctk.CTkOptionMenu(option_frame, values=resolution_options, variable=self.entry_data["res_var"], width=120).pack(side="left", padx=2)
        ctk.CTkOptionMenu(option_frame, values=format_options, variable=self.entry_data["format_var"], width=100).pack(side="left", padx=2)
        ctk.CTkOptionMenu(option_frame, values=audio_options, variable=self.entry_data["audio_var"], width=120).pack(side="left", padx=2)
        ctk.CTkOptionMenu(option_frame, values=subs_options, variable=self.entry_data["subs_var"], width=120).pack(side="left", padx=2)
        
        # Buttons
        self.entry_data["download_btn"] = ctk.CTkButton(
            option_frame, 
            text=f"⬇ {localization.get('video.download', 'Download')}",
            command=self._start_download,
            state="disabled"
        )
        self.entry_data["download_btn"].pack(side="left", padx=2)
        
        ctk.CTkButton(option_frame, text=f"🗑 {localization.get('video.remove', 'Remove')}", command=self._remove_entry).pack(side="left", padx=2)
        
        # Enable the download button after UI is ready
        self.entry_data["download_btn"].configure(state="normal")
    
    def _start_download(self):
        """Start the download process."""
        def download_task():
            try:
                download_video(
                    self.entry_data,
                    self.output_dir,
                    progress_callback=self._update_progress,
                    status_callback=self._update_status,
                    completion_callback=self._download_complete
                )
            except Exception as e:
                self._handle_download_error(str(e))
        
        # Disable download button
        self.entry_data["download_btn"].configure(state="disabled")
        downloading_text = f"⏳ {localization.get('video.downloading', 'Downloading...')}"
        self._update_status(downloading_text)
        self._update_progress(0, downloading_text)
        
        # Start download in separate thread
        threading.Thread(target=download_task, daemon=True).start()
    
    def _update_progress(self, percent, status_text):
        """Update progress bar and status."""
        def update():
            self.progress.set(percent/100)
            self.progress_label.configure(text=f"{percent}%")
            self.status_label.configure(text=status_text)
        
        self.frame.after(0, update)
    
    def _update_status(self, status_text):
        """Update status text."""
        def update():
            self.status_label.configure(text=status_text)
        
        self.frame.after(0, update)
    
    def _download_complete(self):
        """Handle download completion."""
        def update():
            self.entry_data["download_btn"].configure(state="normal")
        
        self.frame.after(0, update)
    
    def _handle_error(self, error_message):
        """Handle video info loading error."""
        def update():
            # Map error types to localized messages
            if error_message == "video_not_found":
                error_text = localization.get("video.video_not_found", "Video not found or unavailable")
            elif error_message == "access_denied":
                error_text = localization.get("video.access_denied", "Access denied - video may be private or restricted")
            elif error_message == "network_error":
                error_text = localization.get("video.network_error", "Network error - check your connection")
            else:
                error_text = localization.get("video.error_loading", "Error loading metadata")
            
            # Show error message in main window
            if self.main_window:
                self.main_window._show_error_message(error_text)
            
            # Remove this entry from the download queue
            if self.entry_data in self.download_queue:
                self.download_queue.remove(self.entry_data)
            
            # Destroy the frame
            try:
                self.frame.destroy()
            except Exception:
                pass
        
        self.frame.after(0, update)
    
    def _handle_download_error(self, error_message):
        """Handle download error."""
        def update():
            error_text = f"❌ {localization.get('video.error', 'Error')}"
            self.status_label.configure(text=error_text)
            self.entry_data["download_btn"].configure(state="normal")
        
        self.frame.after(0, update)
    
    def _remove_entry(self):
        """Remove this entry from the download queue."""
        try:
            self.frame.destroy()
        except Exception:
            pass
        
        if self.entry_data in self.download_queue:
            self.download_queue.remove(self.entry_data)
