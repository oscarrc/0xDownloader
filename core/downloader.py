"""
Download logic and progress tracking for the YouTube Downloader application.
"""

import os
import sys
import yt_dlp
from pathlib import Path
from core.utils import find_language_code_by_name
from core.localization import localization
from core.download_config import download_config


def get_ffmpeg_path():
    """Get the path to the local ffmpeg executable."""
    # Get the directory where the script is located
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        base_path = Path(sys._MEIPASS)
    else:
        # Running as script
        base_path = Path(__file__).parent.parent
    
    ffmpeg_path = base_path / "ffmpeg" / "ffmpeg.exe"
    ffprobe_path = base_path / "ffmpeg" / "ffprobe.exe"
    
    # Check if ffmpeg exists
    if ffmpeg_path.exists() and ffprobe_path.exists():
        return str(ffmpeg_path), str(ffprobe_path)
    else:
        # Fallback to system ffmpeg
        return "ffmpeg", "ffprobe"


def create_ydl_format_string(selected_resolution, selected_format, selected_audio):
    """Create yt-dlp format string based on user selections."""
    if selected_resolution.startswith("best"):
        # For "best" resolution, use format and audio-specific best
        if selected_audio == "default":
            ydl_format = f"best[ext={selected_format}]"
        else:
            ydl_format = f"best[ext={selected_format}][language={selected_audio}]/best[ext={selected_format}]"
    else:
        # For specific resolution, find the best format for that resolution with audio language
        height = selected_resolution.replace("p", "")
        if selected_audio == "default":
            ydl_format = f"best[height<={height}][ext={selected_format}]/best[height<={height}]/best[ext={selected_format}]/best"
        else:
            ydl_format = f"best[height<={height}][ext={selected_format}][language={selected_audio}]/best[height<={height}][ext={selected_format}]/best[height<={height}]/best[ext={selected_format}]/best"
    
    return ydl_format


def download_video(entry, output_dir, progress_callback=None, status_callback=None, completion_callback=None):
    """
    Download a video with the specified options using enhanced yt-dlp configuration.
    
    Args:
        entry: Video entry dictionary with user selections
        output_dir: Output directory for the download
        progress_callback: Function to call with progress updates (percent, status)
        status_callback: Function to call with status updates
        completion_callback: Function to call when download completes
    """
    def progress_hook(d):
        """Enhanced progress hook for yt-dlp with better status reporting."""
        if d['status'] == 'downloading':
            downloading_text = f"⏳ {localization.get('video.downloading', 'Downloading...')}"
            if 'total_bytes' in d and d['total_bytes']:
                percent = int(d['downloaded_bytes'] * 100 / d['total_bytes'])
                if progress_callback:
                    progress_callback(percent, downloading_text)
            elif 'total_bytes_estimate' in d and d['total_bytes_estimate']:
                percent = int(d['downloaded_bytes'] * 100 / d['total_bytes_estimate'])
                if progress_callback:
                    progress_callback(percent, downloading_text)
        elif d['status'] == 'finished':
            completed_text = f"✅ {localization.get('video.completed', 'Completed')}"
            if progress_callback:
                progress_callback(100, completed_text)
            if completion_callback:
                completion_callback()
        elif d['status'] == 'error':
            error_text = f"❌ {localization.get('video.error', 'Error')}: {d.get('error', 'Unknown error')}"
            if status_callback:
                status_callback(error_text)
    
    # Get the selected options
    selected_resolution = entry["res_var"].get()
    selected_format = entry["format_var"].get()
    selected_audio_display = entry["audio_var"].get()
    subtitle_lang = entry["subs_var"].get()
    
    # Extract audio locale/language code from display name using unified resolver
    if selected_audio_display == "default":
        selected_audio = "default"
    else:
        selected_audio = find_language_code_by_name(selected_audio_display)
    
    # Create yt-dlp format string
    ydl_format = create_ydl_format_string(selected_resolution, selected_format, selected_audio)
    
    # Get configuration
    config = download_config.get_config()
    ffmpeg_path, ffprobe_path = get_ffmpeg_path()
    
    # Enhanced yt-dlp options following best practices
    ydl_opts = {
        # Basic options
        "format": ydl_format,
        "outtmpl": os.path.join(output_dir, config["output_template"]),
        "progress_hooks": [progress_hook],
        
        # FFmpeg integration
        "ffmpeg_location": ffmpeg_path,
        
        # Network and performance options
        "socket_timeout": config["socket_timeout"],
        "retries": config["retries"],
        "fragment_retries": config["fragment_retries"],
        "retry_sleep_functions": {"http": lambda n: min(4 ** n, 60)},
        
        # Quality and format options
        "prefer_free_formats": config["prefer_free_formats"],
        "merge_output_format": selected_format if selected_format in ['mp4', 'mkv', 'webm'] else None,
        
        # Metadata and thumbnails
        "writethumbnail": config["embed_thumbnails"],
        "writeinfojson": config["write_info_json"],
        "writedescription": config["write_description"],
        "writeannotations": config["write_annotations"],
        
        # Audio/Video processing
        "postprocessors": config["postprocessors"].copy(),
        
        # Error handling
        "ignoreerrors": False,
        "no_warnings": False,
        "extract_flat": False,
        
        # User agent and headers for better compatibility
        "http_headers": {
            "User-Agent": config["user_agent"]
        },
        
        # Concurrent downloads (if supported by the site)
        "concurrent_fragment_downloads": config["concurrent_fragment_downloads"],
        
        # Age limit (optional, can be configured)
        "age_limit": None,
        
        # Playlist options (if URL is a playlist)
        "extract_flat": False,
        "playlist_items": None,
    }
    
    # Add subtitle options if selected
    no_subtitles_text = localization.get("formats.no_subtitles", "No subtitles")
    if subtitle_lang != no_subtitles_text:
        subtitle_code = find_language_code_by_name(subtitle_lang)
        ydl_opts.update({
            "writesubtitles": True,
            "subtitleslangs": [subtitle_code],
            "subtitlesformat": "best",
            "writeautomaticsub": config["write_automatic_sub"],
        })
        
        # Add subtitle post-processor
        ydl_opts["postprocessors"].append({
            'key': 'FFmpegSubtitlesConvertor',
            'format': config["subtitle_format"],
        })
    
    # Add post-processing for audio/video merging if needed
    if selected_format in ['mp4', 'mkv', 'webm']:
        ydl_opts["postprocessors"].append({
            'key': 'FFmpegVideoConvertor',
            'preferedformat': selected_format,
        })
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Add error handling for specific download errors
            try:
                ydl.download([entry["url"]])
            except yt_dlp.utils.DownloadError as e:
                error_msg = str(e).lower()
                if "sign in" in error_msg or "private" in error_msg:
                    raise Exception("access_denied")
                elif "unavailable" in error_msg or "not found" in error_msg:
                    raise Exception("video_not_found")
                elif "network" in error_msg or "connection" in error_msg:
                    raise Exception("network_error")
                else:
                    raise Exception("download_error")
    except Exception as e:
        if status_callback:
            error_text = f"❌ {localization.get('video.error', 'Error')}: {str(e)}"
            status_callback(error_text)
        raise e


def get_download_config():
    """Get download configuration with best practices."""
    ffmpeg_path, ffprobe_path = get_ffmpeg_path()
    
    return {
        "ffmpeg_path": ffmpeg_path,
        "ffprobe_path": ffprobe_path,
        "max_concurrent_downloads": 4,
        "retry_attempts": 3,
        "socket_timeout": 30,
        "fragment_retries": 3,
        "prefer_free_formats": True,
        "write_metadata": True,
        "embed_thumbnails": True,
        "convert_thumbnails": True,
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }


def validate_ffmpeg():
    """Validate that ffmpeg is working correctly."""
    ffmpeg_path, ffprobe_path = get_ffmpeg_path()
    
    try:
        import subprocess
        # Test ffmpeg
        result = subprocess.run([ffmpeg_path, "-version"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            return False, "FFmpeg test failed"
        
        # Test ffprobe
        result = subprocess.run([ffprobe_path, "-version"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            return False, "FFprobe test failed"
            
        return True, "FFmpeg and FFprobe are working correctly"
    except subprocess.TimeoutExpired:
        return False, "FFmpeg validation timed out"
    except FileNotFoundError:
        return False, "FFmpeg not found in system PATH"
    except Exception as e:
        return False, f"FFmpeg validation error: {str(e)}"


def get_supported_formats():
    """Get list of supported output formats."""
    return {
        "video": ["mp4", "webm", "mkv", "avi", "mov", "flv", "3gp", "ogv"],
        "audio": ["mp3", "aac", "m4a", "ogg", "wav", "flac"],
        "subtitle": ["srt", "vtt", "ass", "ssa"]
    }


def create_advanced_format_string(selected_resolution, selected_format, selected_audio, prefer_quality="best"):
    """Create advanced format string with quality preferences."""
    if selected_resolution.startswith("best"):
        if selected_audio == "default":
            return f"best[ext={selected_format}]/best"
        else:
            return f"best[ext={selected_format}][language={selected_audio}]/best[ext={selected_format}]/best"
    else:
        height = selected_resolution.replace("p", "")
        if selected_audio == "default":
            return f"best[height<={height}][ext={selected_format}]/best[height<={height}]/best[ext={selected_format}]/best"
        else:
            return f"best[height<={height}][ext={selected_format}][language={selected_audio}]/best[height<={height}][ext={selected_format}]/best[height<={height}]/best[ext={selected_format}]/best"
