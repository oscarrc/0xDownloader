"""
Download configuration and settings for the YouTube Downloader application.
"""

import os
from pathlib import Path


class DownloadConfig:
    """Configuration class for download settings."""
    
    def __init__(self):
        self.config = {
            # FFmpeg settings
            "ffmpeg_location": None,
            "ffprobe_location": None,
            
            # Network settings
            "socket_timeout": 30,
            "retries": 3,
            "fragment_retries": 3,
            "concurrent_fragment_downloads": 4,
            
            # Quality settings
            "prefer_free_formats": True,
            "write_metadata": True,
            "embed_thumbnails": True,
            "convert_thumbnails": True,
            
            # User agent
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            
            # Output settings
            "output_template": "%(title)s.%(ext)s",
            "write_info_json": False,
            "write_description": False,
            "write_annotations": False,
            
            # Subtitle settings
            "write_automatic_sub": True,
            "subtitle_format": "srt",
            
            # Post-processing
            "postprocessors": [
                {
                    'key': 'FFmpegThumbnailsConvertor',
                    'format': 'jpg',
                },
                {
                    'key': 'EmbedThumbnail',
                    'already_have_thumbnail': False,
                }
            ]
        }
    
    def get_config(self):
        """Get the current configuration."""
        return self.config.copy()
    
    def update_config(self, new_config):
        """Update configuration with new values."""
        self.config.update(new_config)
    
    def get_ffmpeg_paths(self):
        """Get FFmpeg and FFprobe paths."""
        from core.downloader import get_ffmpeg_path
        return get_ffmpeg_path()
    
    def validate_config(self):
        """Validate the current configuration."""
        errors = []
        
        # Check FFmpeg paths
        ffmpeg_path, ffprobe_path = self.get_ffmpeg_paths()
        if not os.path.exists(ffmpeg_path):
            errors.append(f"FFmpeg not found at: {ffmpeg_path}")
        if not os.path.exists(ffprobe_path):
            errors.append(f"FFprobe not found at: {ffprobe_path}")
        
        # Check numeric values
        if not isinstance(self.config["socket_timeout"], (int, float)) or self.config["socket_timeout"] <= 0:
            errors.append("socket_timeout must be a positive number")
        
        if not isinstance(self.config["retries"], int) or self.config["retries"] < 0:
            errors.append("retries must be a non-negative integer")
        
        if not isinstance(self.config["concurrent_fragment_downloads"], int) or self.config["concurrent_fragment_downloads"] <= 0:
            errors.append("concurrent_fragment_downloads must be a positive integer")
        
        return len(errors) == 0, errors


# Global configuration instance
download_config = DownloadConfig()
