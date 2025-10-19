import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from customtkinter import CTkImage
import yt_dlp
from PIL import Image
import requests
from io import BytesIO
import json

# --- Configuración ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

output_dir = os.getcwd()
download_queue = []

# Load language names
def load_language_names():
    try:
        with open("lang.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

language_names = load_language_names()

def get_language_display_name(lang_code):
    """Get the display name for a language code"""
    if lang_code in language_names:
        return f"{language_names[lang_code]}"
    else:
        return lang_code

# --- Funciones helper ---
def choose_folder():
    global output_dir
    folder = filedialog.askdirectory()
    if folder:
        folder_entry.delete(0, tk.END)
        folder_entry.insert(0, folder)
        output_dir = folder

def fetch_video_info(url):
    ydl_opts = {"quiet": True, "no_warnings": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
    return info


def download_video(entry):
    def update_ui_progress(percent, status_text):
        """Helper function to update UI from main thread"""
        entry["progress"].set(percent/100)
        entry["progress_label"].configure(text=f"{percent}%")
        entry["status_label"].configure(text=status_text)
    
    def progress_hook(d):
        """Progress hook for yt-dlp"""
        if d['status'] == 'downloading':
            if 'total_bytes' in d and d['total_bytes']:
                percent = int(d['downloaded_bytes'] * 100 / d['total_bytes'])
                root.after(0, lambda p=percent: update_ui_progress(p, "⏳ Descargando..."))
            elif 'total_bytes_estimate' in d and d['total_bytes_estimate']:
                percent = int(d['downloaded_bytes'] * 100 / d['total_bytes_estimate'])
                root.after(0, lambda p=percent: update_ui_progress(p, "⏳ Descargando..."))
        elif d['status'] == 'finished':
            root.after(0, lambda: update_ui_progress(100, "✅ Completado"))
            root.after(0, lambda: entry["download_btn"].configure(state="normal"))
    
    entry["download_btn"].configure(state="disabled")
    entry["status_label"].configure(text="⏳ Descargando...")
    entry["progress"].set(0)
    entry["progress_label"].configure(text="0%")

    # Get the selected options
    selected_resolution = entry["res_var"].get()
    selected_format = entry["format_var"].get()
    selected_audio_display = entry["audio_var"].get()
    subtitle_lang = entry["subs_var"].get()
    
    # Extract language code from display name (e.g., "English" -> find "en")
    if selected_audio_display == "default":
        selected_audio = "default"
    else:
        # Find the language code that corresponds to this display name
        selected_audio = None
        for code, name in language_names.items():
            if name == selected_audio_display:
                selected_audio = code
                break
        if selected_audio is None:
            selected_audio = selected_audio_display  # fallback to original
    
    # Combine resolution, format, and audio language into yt-dlp format string
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

    ydl_opts = {
        "format": ydl_format,
        "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),
        "progress_hooks": [progress_hook],
    }
    
    if subtitle_lang != "Sin subtítulos":
        # Find the language code that corresponds to this display name
        subtitle_code = None
        for code, name in language_names.items():
            if name == subtitle_lang:
                subtitle_code = code
                break
        if subtitle_code is None:
            subtitle_code = subtitle_lang  # fallback to original
        
        ydl_opts.update({
            "writesubtitles": True,
            "subtitleslangs": [subtitle_code],
            "subtitlesformat": "best"
        })

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([entry["url"]])
    except Exception as e:
        root.after(0, lambda: entry["status_label"].configure(text="❌ Error"))
        root.after(0, lambda: entry["download_btn"].configure(state="normal"))
        root.after(0, lambda: messagebox.showerror("Error", str(e)))

def add_video():
    url = url_entry.get().strip()
    if not url:
        messagebox.showwarning("Aviso", "Introduce una URL válida")
        return
    url_entry.delete(0, tk.END)

    # Frame horizontal: thumbnail | contenido
    frame = ctk.CTkFrame(video_list_frame, corner_radius=8, fg_color="#2a2a2a")
    frame.pack(fill="x", pady=5, padx=5)

    # Calculate thumbnail size to match content height
    # Estimate: title (~20px) + progress area (~40px) + selectors (~30px) + padding (~20px) = ~110px
    thumb_height = 110
    thumb_width = int(thumb_height * 16 / 9)  # Maintain 16:9 aspect ratio
    thumb_label = ctk.CTkLabel(frame, text="Cargando imagen...", width=thumb_width, height=thumb_height, fg_color="#1f1f1f")
    thumb_label.pack(side="left", padx=5, pady=5)

    # Right content
    content_frame = ctk.CTkFrame(frame, fg_color="transparent")
    content_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

    title_lbl = ctk.CTkLabel(content_frame, text="Cargando...")
    title_lbl.pack(anchor="w", pady=2)

    # Status and progress bar layout
    status_progress_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
    status_progress_frame.pack(fill="x", pady=2)

    # Top row: Status and progress percentage
    top_row = ctk.CTkFrame(status_progress_frame, fg_color="transparent")
    top_row.pack(fill="x", pady=(0,2))

    # Left side: Status
    status_label = ctk.CTkLabel(top_row, text="Esperando", width=20, anchor="w")
    status_label.pack(side="left")

    # Right side: Progress percentage
    progress_label = ctk.CTkLabel(top_row, text="0%", width=10, anchor="e")
    progress_label.pack(side="right")

    # Bottom row: Progress bar (full width)
    progress = ctk.CTkProgressBar(status_progress_frame)
    progress.set(0)
    progress.pack(fill="x", expand=True, pady=(0, 10))  # Add padding below progress bar

    # Set initial indeterminate state while loading
    progress.configure(mode="indeterminate")
    progress.start()

    entry = {
        "url": url,
        "frame": frame,
        "thumb_label": thumb_label,
        "title_label": title_lbl,
        "progress": progress,
        "progress_label": progress_label,
        "status_label": status_label,
        "download_btn": None,
        "res_var": None,
        "format_var": None,
        "audio_var": None,
        "subs_var": None
    }
    download_queue.append(entry)

    def task():
        try:
            info = fetch_video_info(url)
            formats = info.get("formats", [])
            
            # Create resolution options
            resolution_options = []
            seen_heights = set()
            
            # Add "best" option first
            resolution_options.append("best - Mejor calidad")
            
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
            
            # Create format options
            format_options = ["mp4", "webm", "mkv", "avi", "mov"]
            
            # Extract audio languages from formats
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
            
            # Create subtitle options with display names
            subs_options = ["Sin subtítulos"]
            if info.get("subtitles"):
                subtitle_langs = list(info.get("subtitles", {}).keys())
                subs_options.extend([get_language_display_name(lang) for lang in subtitle_langs])
            subs_options = subs_options or ["Sin subtítulos"]

            # Descargar thumbnail
            try:
                resp = requests.get(info.get("thumbnail",""), timeout=5)
                img_data = resp.content
                img = Image.open(BytesIO(img_data)).resize((thumb_width, thumb_height))
                ctk_img = CTkImage(light_image=img, dark_image=img, size=(thumb_width, thumb_height))
                def update_thumb():
                    entry["thumb_label"].configure(image=ctk_img, text="")
                    entry["thumb_label"].image = ctk_img
                root.after(0, update_thumb)
            except:
                pass

            def update_ui():
                entry["title_label"].configure(text=info.get("title","Título no disponible"))
                
                # Stop indeterminate progress and set to normal mode
                entry["progress"].stop()
                entry["progress"].configure(mode="determinate")
                entry["progress"].set(0)
                entry["progress_label"].configure(text="0%")
                entry["status_label"].configure(text="Listo")
                
                # Variables TK
                entry["res_var"] = tk.StringVar(value=resolution_options[0])
                entry["format_var"] = tk.StringVar(value=format_options[0])
                entry["audio_var"] = tk.StringVar(value=audio_options[0])
                entry["subs_var"] = tk.StringVar(value=subs_options[0])
                
                # Selectores sin etiquetas
                option_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
                option_frame.pack(fill="x", pady=2)
                
                ctk.CTkOptionMenu(option_frame, values=resolution_options, variable=entry["res_var"], width=120).pack(side="left", padx=2)
                ctk.CTkOptionMenu(option_frame, values=format_options, variable=entry["format_var"], width=100).pack(side="left", padx=2)
                ctk.CTkOptionMenu(option_frame, values=audio_options, variable=entry["audio_var"], width=120).pack(side="left", padx=2)
                ctk.CTkOptionMenu(option_frame, values=subs_options, variable=entry["subs_var"], width=120).pack(side="left", padx=2)
                
                entry["download_btn"] = ctk.CTkButton(option_frame, text="⬇ Descargar",
                                                      command=lambda e=entry: threading.Thread(target=download_video,args=(e,),daemon=True).start(),
                                                      state="disabled")
                entry["download_btn"].pack(side="left", padx=2)
                ctk.CTkButton(option_frame, text="🗑 Quitar", command=lambda e=entry: remove_entry(e)).pack(side="left", padx=2)
                
                # Enable the download button after UI is ready
                entry["download_btn"].configure(state="normal")

            root.after(0, update_ui)
        except Exception as e:
            def fail_ui():
                entry["title_label"].configure(text="Error cargando metadata")
                entry["status_label"].configure(text="Error")
                entry["progress"].stop()
                entry["progress"].configure(mode="determinate")
                entry["progress"].set(0)
                entry["progress_label"].configure(text="0%")
            root.after(0, fail_ui)

    threading.Thread(target=task, daemon=True).start()

def remove_entry(entry):
    try:
        entry["frame"].destroy()
    except Exception:
        pass
    if entry in download_queue:
        download_queue.remove(entry)

def clear_list():
    global download_queue
    for entry in download_queue[:]:
        remove_entry(entry)
    download_queue = []

# --- GUI ---
root = ctk.CTk()
root.title("YouTube Downloader")
root.geometry("1000x700")

top_frame = ctk.CTkFrame(root)
top_frame.pack(fill="x", pady=(10, 20), padx=10)

url_entry = ctk.CTkEntry(top_frame, placeholder_text="Enlace de YouTube")
url_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
ctk.CTkButton(top_frame, text="Añadir", command=add_video).pack(side="left")

btn_frame = ctk.CTkFrame(root, fg_color="transparent")
btn_frame.pack(fill="x", pady=5, padx=5)
ctk.CTkButton(btn_frame, text="Descargar lista",
              command=lambda: [threading.Thread(target=download_video, args=(e,), daemon=True).start() for e in download_queue]).pack(side="left", padx=5)
ctk.CTkButton(btn_frame, text="Vaciar lista", command=clear_list).pack(side="left", padx=5)

# Folder selection with input field - positioned on the right
folder_frame = ctk.CTkFrame(btn_frame, fg_color="transparent")
folder_frame.pack(side="right", padx=5)

folder_entry = ctk.CTkEntry(folder_frame, placeholder_text=output_dir, width=300)
folder_entry.pack(side="left", padx=(0,5))

ctk.CTkButton(folder_frame, text="📁", command=choose_folder, width=30).pack(side="left")

video_list_frame = ctk.CTkScrollableFrame(root, width=980, height=550)
video_list_frame.pack(padx=5, pady=5, fill="both", expand=True)

# Footer
footer_frame = ctk.CTkFrame(root, fg_color="transparent")
footer_frame.pack(fill="x", padx=10, pady=5)

# Left side: Attribution
attribution_label = ctk.CTkLabel(footer_frame, text="Made with 🩷 by Oscar R.C.", text_color="white", cursor="hand2")
attribution_label.pack(side="left")

# Right side: Coffee link
coffee_label = ctk.CTkLabel(footer_frame, text="Buy me a coffee", text_color="white", cursor="hand2")
coffee_label.pack(side="right")

# Set the initial folder value after all widgets are created
folder_entry.delete(0, tk.END)
folder_entry.insert(0, output_dir)

# Add click handlers for links
def open_web(event):
    import webbrowser
    webbrowser.open("https://oscarrc.me")

def open_ko_fi(event):
    import webbrowser
    webbrowser.open("https://ko-fi.com/oscarrc")

attribution_label.bind("<Button-1>", open_web)
coffee_label.bind("<Button-1>", open_ko_fi)

root.mainloop()
