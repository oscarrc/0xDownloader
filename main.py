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

# --- Configuración ---
ctk.set_appearance_mode("dark")  # "light" o "dark"
ctk.set_default_color_theme("blue")

FFMPEG_PATH = os.path.join(os.getcwd(), "ffmpeg", "ffmpeg.exe")
output_dir = os.getcwd()
download_queue = []

# --- Funciones helper ---
def choose_folder():
    global output_dir
    folder = filedialog.askdirectory()
    if folder:
        output_dir_label.configure(text=f"📁 Carpeta destino: {folder}")
        output_dir = folder

def fetch_video_info(url):
    ydl_opts = {"quiet": True, "no_warnings": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
    return info

def download_video(entry):
    def progress_hook(d):
        if d.get("status") == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate")
            downloaded = d.get("downloaded_bytes")
            if total and downloaded is not None:
                percent = int(downloaded * 100 / total)
                entry["progress"].set(percent / 100)
                entry["progress_label"].configure(text=f"{percent}%")
            else:
                # Modo indeterminado
                entry["progress"].set(0.5)
                entry["progress_label"].configure(text="...%")
            entry["status_label"].configure(text="⏳ Descargando...")
        elif d.get("status") == "finished":
            entry["progress"].set(1.0)
            entry["progress_label"].configure(text="100%")
            entry["status_label"].configure(text="✅ Completado")
            entry["download_btn"].configure(state="normal")

    entry["download_btn"].configure(state="disabled")
    entry["status_label"].configure(text="⏳ Descargando...")

    fmt = entry["res_var"].get().split(" ")[0] if entry["res_var"].get() else "best"
    out_format = entry["out_var"].get()
    ydl_opts = {
        "format": fmt,
        "progress_hooks": [progress_hook],
        "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),
        "ffmpeg_location": os.path.dirname(FFMPEG_PATH),
        "merge_output_format": out_format,
        "postprocessors": [{
            "key": "FFmpegVideoConvertor",
            "preferedformat": out_format
        }]
    }
    if entry["subs_var"].get() != "Ninguno":
        ydl_opts.update({
            "writesubtitles": True,
            "subtitleslangs": [entry["subs_var"].get()],
            "subtitlesformat": "best"
        })

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([entry["url"]])
    except Exception as e:
        messagebox.showerror("Error", f"Error descargando: {e}")
        entry["download_btn"].configure(state="normal")
        entry["status_label"].configure(text="❌ Error")

def add_video():
    url = url_entry.get().strip()
    if not url:
        messagebox.showwarning("Aviso", "Introduce una URL válida")
        return
    url_entry.delete(0, tk.END)

    # Frame horizontal: thumbnail | contenido
    frame = ctk.CTkFrame(video_list_frame, corner_radius=8, fg_color="#2a2a2a")
    frame.pack(fill="x", pady=5, padx=5)

    # Thumbnail 16:9
    thumb_width = 160
    thumb_height = int(thumb_width * 9 / 16)
    thumb_label = ctk.CTkLabel(frame, text="Cargando imagen...", width=thumb_width, height=thumb_height, fg_color="#1f1f1f")
    thumb_label.pack(side="left", padx=5, pady=5)

    # Right content
    content_frame = ctk.CTkFrame(frame, fg_color="transparent")
    content_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

    title_lbl = ctk.CTkLabel(content_frame, text="Cargando...")
    title_lbl.pack(anchor="w", pady=2)

    # Frame horizontal para barra de progreso
    progress_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
    progress_frame.pack(fill="x", pady=2)

    status_label = ctk.CTkLabel(progress_frame, text="Esperando", width=15, anchor="w")
    status_label.pack(side="left", padx=(0,5))

    progress = ctk.CTkProgressBar(progress_frame)
    progress.set(0)
    progress.pack(side="left", fill="x", expand=True)

    progress_label = ctk.CTkLabel(progress_frame, text="0%", width=5, anchor="e")
    progress_label.pack(side="right", padx=(5,0))

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
        "out_var": None,
        "subs_var": None
    }
    download_queue.append(entry)

    def task():
        try:
            info = fetch_video_info(url)
            resolutions = [f"{f['format_id']} ({f.get('height','?')}p) - {f.get('ext')}" for f in info.get("formats", []) if f.get("vcodec") != "none"]
            resolutions = resolutions or ["best"]
            out_options = ["mp4","mkv","webm"]
            subs_options = ["Ninguno"] + list(info.get("subtitles", {}).keys())
            subs_options = subs_options or ["Ninguno"]

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
                # Variables TK
                entry["res_var"] = tk.StringVar(value=resolutions[0])
                entry["out_var"] = tk.StringVar(value=out_options[0])
                entry["subs_var"] = tk.StringVar(value=subs_options[0])
                # Selectores y botones
                option_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
                option_frame.pack(fill="x", pady=2)
                ctk.CTkOptionMenu(option_frame, values=resolutions, variable=entry["res_var"], width=150).pack(side="left", padx=2)
                ctk.CTkOptionMenu(option_frame, values=subs_options, variable=entry["subs_var"], width=120).pack(side="left", padx=2)
                ctk.CTkOptionMenu(option_frame, values=out_options, variable=entry["out_var"], width=100).pack(side="left", padx=2)
                entry["download_btn"] = ctk.CTkButton(option_frame, text="⬇ Descargar",
                                                      command=lambda e=entry: threading.Thread(target=download_video,args=(e,),daemon=True).start())
                entry["download_btn"].pack(side="left", padx=2)
                ctk.CTkButton(option_frame, text="🗑 Quitar", command=lambda e=entry: remove_entry(e)).pack(side="left", padx=2)

            root.after(0, update_ui)
        except Exception as e:
            def fail_ui():
                entry["title_label"].configure(text="Error cargando metadata")
                status_label.configure(text=str(e))
            root.after(0, fail_ui)

    threading.Thread(target=task, daemon=True).start()

def remove_entry(entry):
    try:
        entry["frame"].destroy()
    except Exception:
        pass
    if entry in download_queue:
        download_queue.remove(entry)

# --- GUI ---
root = ctk.CTk()
root.title("YouTube Downloader")
root.geometry("1000x700")

# Top controls
top_frame = ctk.CTkFrame(root)
top_frame.pack(fill="x", pady=5)

url_entry = ctk.CTkEntry(top_frame, placeholder_text="Enlace de YouTube", width=600)
url_entry.pack(side="left", padx=5)
ctk.CTkButton(top_frame, text="➕ Añadir", command=add_video).pack(side="left", padx=5)
ctk.CTkButton(top_frame, text="📁 Carpeta", command=choose_folder).pack(side="left", padx=5)

output_dir_label = ctk.CTkLabel(root, text=f"📁 Carpeta destino: {output_dir}")
output_dir_label.pack(anchor="w", padx=5, pady=2)

download_all_btn = ctk.CTkButton(root, text="⬇ Descargar todos",
                                  command=lambda: [threading.Thread(target=download_video,args=(e,),daemon=True).start() for e in download_queue])
download_all_btn.pack(padx=5, pady=5, anchor="w")

video_list_frame = ctk.CTkScrollableFrame(root, width=980, height=550)
video_list_frame.pack(padx=5, pady=5)

root.mainloop()
