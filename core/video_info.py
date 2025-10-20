"""
Video information fetching and processing for the YouTube Downloader application.
"""

import yt_dlp
from core.utils import get_language_display_name
from core.localization import localization


def fetch_video_info(url):
    """Fetch video information from YouTube URL."""
    ydl_opts = {"quiet": True, "no_warnings": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            return info
        except yt_dlp.utils.DownloadError as e:
            error_msg = str(e).lower()
            if "video unavailable" in error_msg or "private video" in error_msg:
                raise Exception("video_not_found")
            elif "access denied" in error_msg or "sign in" in error_msg:
                raise Exception("access_denied")
            elif "network" in error_msg or "connection" in error_msg:
                raise Exception("network_error")
            else:
                raise Exception("video_not_found")
        except Exception as e:
            # Re-raise with a generic error message
            raise Exception("video_not_found")


def extract_resolution_options(formats):
    """Extract available resolution options from video formats."""
    resolution_options = []
    seen_heights = set()
    
    # Add "best" option first
    resolution_options.append(localization.get("formats.best", "best - Best quality"))
    
    # Add specific resolutions
    for f in formats:
        if f.get("vcodec") != "none" and f.get("height"):
            height = f.get("height")
            if height not in seen_heights:
                resolution_options.append(f"{height}p")
                seen_heights.add(height)
    
    # Sort resolutions (best first, then descending)
    def sort_key(option):
        if option.startswith("best"):
            return (0, 0)  # best comes first
        else:
            height = int(option.replace("p", ""))
            return (1, -height)  # higher resolutions first
    
    resolution_options.sort(key=sort_key)
    return resolution_options


def extract_audio_language_options(formats, info):
    """Extract available audio language options from video formats."""
    audio_languages = set()
    default_audio_lang = None
    
    # Get the default audio language from video info
    if "language" in info:
        default_audio_lang = info["language"]
    elif "automatic_captions" in info:
        # Try to get from automatic captions
        for lang in info["automatic_captions"]:
            if default_audio_lang is None:
                default_audio_lang = lang
                break
    
    # Collect all available audio languages
    for f in formats:
        if f.get("acodec") != "none":  # Has audio
            lang = f.get("language")
            if lang:
                audio_languages.add(lang)
    
    # If we couldn't find a default from video info, use the first audio language
    if default_audio_lang is None and audio_languages:
        default_audio_lang = list(audio_languages)[0]
    
    # Create audio language options with display names
    audio_options = []
    if audio_languages:
        # Sort languages and put default first
        sorted_langs = sorted(audio_languages)
        if default_audio_lang and default_audio_lang in sorted_langs:
            sorted_langs.remove(default_audio_lang)
            sorted_langs.insert(0, default_audio_lang)
        
        # Convert to display names
        audio_options = [get_language_display_name(lang) for lang in sorted_langs]
    else:
        audio_options = ["default"]
        default_audio_lang = "default"
    
    return audio_options


def extract_subtitle_options(info):
    """Extract available subtitle options from video info."""
    subs_options = [localization.get("formats.no_subtitles", "No subtitles")]
    if info.get("subtitles"):
        subtitle_langs = list(info.get("subtitles", {}).keys())
        subs_options.extend([get_language_display_name(lang) for lang in subtitle_langs])
    subs_options = subs_options or [localization.get("formats.no_subtitles", "No subtitles")]
    return subs_options


def extract_format_options(formats):
    """Extract available video container format options from video formats."""
    # Define valid video container formats
    valid_video_formats = {"mp4", "webm", "mkv", "avi", "mov", "flv", "3gp", "ogv"}
    
    format_options = set()
    
    # Extract unique video container formats from the video's available formats
    for f in formats:
        if f.get("ext") and f["ext"] in valid_video_formats:
            # Only include formats that have video (not audio-only)
            if f.get("vcodec") and f["vcodec"] != "none":
                format_options.add(f["ext"])
    
    # Convert to sorted list
    format_list = sorted(list(format_options))
    
    # If no formats found, provide common fallbacks
    if not format_list:
        format_list = ["mp4", "webm", "mkv"]
    
    return format_list
