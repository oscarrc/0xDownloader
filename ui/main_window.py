"""
Main window and layout for the YouTube Downloader application.
"""

import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog
import webbrowser

from config import (
    APP_GEOMETRY, APPEARANCE_MODE, COLOR_THEME,
    DEFAULT_OUTPUT_DIR, VIDEO_LIST_WIDTH, VIDEO_LIST_HEIGHT,
    OSCAR_WEBSITE, KO_FI_LINK
)
from core.localization import localization
from ui.video_entry import VideoEntry


class MainWindow:
    """Main application window."""
    
    def __init__(self):
        # Initialize CustomTkinter
        ctk.set_appearance_mode(APPEARANCE_MODE)
        ctk.set_default_color_theme(COLOR_THEME)
        
        # Create main window
        self.root = ctk.CTk()
        self.root.title(localization.get("app.title", "YouTube Downloader"))
        self.root.geometry(APP_GEOMETRY)
        
        # Initialize data
        self.output_dir = DEFAULT_OUTPUT_DIR
        self.download_queue = []
        
        # Create UI components
        self._create_top_frame()
        self._create_button_frame()
        self._create_video_list_frame()
        self._create_footer()
        
        # Set initial folder value
        self._update_folder_display()
    
    def _create_top_frame(self):
        """Create the top frame with URL input and add button."""
        self.top_frame = ctk.CTkFrame(self.root)
        self.top_frame.pack(fill="x", pady=(10, 20), padx=10)
        
        # URL input
        self.url_entry = ctk.CTkEntry(self.top_frame, placeholder_text=localization.get("app.url_placeholder", "YouTube Link"))
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        # Add button
        self.add_button = ctk.CTkButton(self.top_frame, text=localization.get("app.add_button", "Add"), command=self._add_video)
        self.add_button.pack(side="left")
    
    def _create_button_frame(self):
        """Create the button frame with download/clear buttons and folder selection."""
        self.btn_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.btn_frame.pack(fill="x", pady=5, padx=5)
        
        # Download and clear buttons
        self.download_all_button = ctk.CTkButton(
            self.btn_frame, 
            text=localization.get("app.download_list", "Download List"),
            command=self._download_all
        )
        self.download_all_button.pack(side="left", padx=5)
        
        self.clear_button = ctk.CTkButton(
            self.btn_frame, 
            text=localization.get("app.clear_list", "Clear List"), 
            command=self._clear_list
        )
        self.clear_button.pack(side="left", padx=5)
        
        # Folder selection
        self._create_folder_selection()
    
    def _create_folder_selection(self):
        """Create the folder selection controls."""
        self.folder_frame = ctk.CTkFrame(self.btn_frame, fg_color="transparent")
        self.folder_frame.pack(side="right", padx=5)
        
        # Folder input field
        self.folder_entry = ctk.CTkEntry(
            self.folder_frame, 
            placeholder_text=localization.get("app.folder_placeholder", "Destination Folder"), 
            width=300
        )
        self.folder_entry.pack(side="left", padx=(0, 5))
        
        # Folder selection button
        self.folder_button = ctk.CTkButton(
            self.folder_frame, 
            text="📁", 
            command=self._choose_folder, 
            width=30
        )
        self.folder_button.pack(side="left")
    
    def _create_video_list_frame(self):
        """Create the scrollable video list frame."""
        self.video_list_frame = ctk.CTkScrollableFrame(
            self.root, 
            width=VIDEO_LIST_WIDTH, 
            height=VIDEO_LIST_HEIGHT
        )
        self.video_list_frame.pack(padx=5, pady=5, fill="both", expand=True)
    
    def _create_footer(self):
        """Create the footer with attribution and coffee link."""
        self.footer_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.footer_frame.pack(fill="x", padx=10, pady=5)
        
        # Left side: Attribution
        attribution_text = f"{localization.get('app.made_with', 'Made with')} 🩷 {localization.get('app.by', 'by')} Oscar R.C."
        self.attribution_label = ctk.CTkLabel(
            self.footer_frame, 
            text=attribution_text, 
            text_color="white", 
            cursor="hand2"
        )
        self.attribution_label.pack(side="left")
        
        # Right side: Coffee link
        self.coffee_label = ctk.CTkLabel(
            self.footer_frame, 
            text=localization.get("app.buy_coffee", "Buy me a coffee"), 
            text_color="white", 
            cursor="hand2"
        )
        self.coffee_label.pack(side="right")
        
        # Bind click handlers
        self.attribution_label.bind("<Button-1>", self._open_oscar_site)
        self.coffee_label.bind("<Button-1>", self._open_ko_fi)
    
    def _add_video(self):
        """Add a video to the download queue."""
        url = self.url_entry.get().strip()
        if not url:
            return
        
        # Clear the URL entry
        self.url_entry.delete(0, tk.END)
        
        # Create new video entry
        VideoEntry(self.video_list_frame, url, self.output_dir, self.download_queue)
    
    def _download_all(self):
        """Download all videos in the queue."""
        for entry in self.download_queue:
            if entry["download_btn"] and entry["download_btn"].cget("state") == "normal":
                entry["download_btn"].invoke()
    
    def _clear_list(self):
        """Clear all videos from the download queue."""
        for entry in self.download_queue[:]:  # Copy list to avoid modification during iteration
            try:
                entry["frame"].destroy()
            except Exception:
                pass
        self.download_queue.clear()
    
    def _choose_folder(self):
        """Open folder selection dialog."""
        folder = filedialog.askdirectory()
        if folder:
            self.output_dir = folder
            self._update_folder_display()
    
    def _update_folder_display(self):
        """Update the folder display in the input field."""
        self.folder_entry.delete(0, tk.END)
        self.folder_entry.insert(0, self.output_dir)
    
    def _open_oscar_site(self, event):
        """Open Oscar's website."""
        webbrowser.open(OSCAR_WEBSITE)
    
    def _open_ko_fi(self, event):
        """Open Ko-fi page."""
        webbrowser.open(KO_FI_LINK)
    
    def run(self):
        """Start the application main loop."""
        self.root.mainloop()
