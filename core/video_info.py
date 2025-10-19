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
        info = ydl.extract_info(url, download=False)
    return info


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


def get_format_options():
    """Get available output format options."""
    return ["mp4", "webm", "mkv", "avi", "mov"]
