"""
Download logic and progress tracking for the YouTube Downloader application.
"""

import os
import yt_dlp
from core.utils import find_language_code_by_name
from core.localization import localization


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
    Download a video with the specified options.
    
    Args:
        entry: Video entry dictionary with user selections
        output_dir: Output directory for the download
        progress_callback: Function to call with progress updates (percent, status)
        status_callback: Function to call with status updates
        completion_callback: Function to call when download completes
    """
    def progress_hook(d):
        """Progress hook for yt-dlp"""
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
    
    # Prepare yt-dlp options
    ydl_opts = {
        "format": ydl_format,
        "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),
        "progress_hooks": [progress_hook],
    }
    
    # Add subtitle options if selected
    no_subtitles_text = localization.get("formats.no_subtitles", "No subtitles")
    if subtitle_lang != no_subtitles_text:
        subtitle_code = find_language_code_by_name(subtitle_lang)
        ydl_opts.update({
            "writesubtitles": True,
            "subtitleslangs": [subtitle_code],
            "subtitlesformat": "best"
        })
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([entry["url"]])
    except Exception as e:
        if status_callback:
            error_text = f"❌ {localization.get('video.error', 'Error')}"
            status_callback(error_text)
        raise e
