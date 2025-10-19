# 0xDownloader

A modern, multilingual YouTube video downloader with a clean GUI interface built with Python and CustomTkinter.

## 🌟 Features

- **🎥 Video Downloading** - Download YouTube videos in various formats and qualities
- **🌍 Multilingual Support** - Available in English and Spanish with automatic language detection
- **📱 Modern UI** - Clean, dark-themed interface built with CustomTkinter
- **⚙️ Advanced Options** - Choose resolution, format, audio language, and subtitles
- **📊 Progress Tracking** - Real-time download progress with status updates
- **📁 Batch Downloads** - Download multiple videos from a queue
- **🖼️ Thumbnail Preview** - See video thumbnails while managing downloads

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone or download** this repository
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the application**:
   ```bash
   python main.py
   ```

### Building Executable

To create a standalone `.exe` file:

```bash
python build.py
```

The executable will be created in the `/dist` directory as `0xDownloader.exe`.

#### Adding a Custom Icon

To add a custom icon to your application:

1. **Create or obtain an icon file**:
   - Format: `.ico` file (Windows icon format)
   - Size: 256x256 pixels (or multiple sizes: 16x16, 32x32, 48x48, 64x64, 128x128, 256x256)
   - Name: `icon.ico`
   - Location: Place it in the `assets/` directory

2. **The build script will automatically detect and use the icon**:
   - If `assets/icon.ico` exists, it will be included in the executable
   - The icon will appear in the taskbar, window title bar, and file explorer
   - If no icon is found, the default Python icon will be used

3. **Icon sources**:
   - Create your own using tools like GIMP, Photoshop, or online icon generators
   - Use free icon resources like [Flaticon](https://www.flaticon.com/), [Icons8](https://icons8.com/), or [Feather Icons](https://feathericons.com/)
   - Convert existing images to `.ico` format using online converters

## 📖 Usage

1. **Add Videos**: Paste YouTube URLs in the input field and click "Add"
2. **Configure Options**: For each video, select:
   - **Resolution**: Choose video quality (best, 1080p, 720p, etc.)
   - **Format**: Select output format (mp4, webm, mkv, etc.)
   - **Audio**: Choose audio language
   - **Subtitles**: Select subtitle language or "No subtitles"
3. **Download**: Click the download button for individual videos or "Download List" for all
4. **Monitor Progress**: Watch real-time progress bars and status updates

## 🛠️ Technical Details

### Architecture

The application is built with a modular architecture:

```
ytdl/
├── main.py              # Entry point
├── config.py            # Configuration and constants
├── core/                # Business logic
│   ├── downloader.py    # Download functionality
│   ├── video_info.py    # Video metadata processing
│   ├── utils.py         # Helper functions
│   └── localization.py  # Multilingual support
├── ui/                  # User interface
│   ├── main_window.py   # Main window layout
│   └── video_entry.py   # Video entry components
└── locales/             # Translation files
    ├── en.json          # English translations
    └── es.json          # Spanish translations
```

### Dependencies

- **yt-dlp** - YouTube video downloading
- **customtkinter** - Modern GUI framework
- **Pillow** - Image processing for thumbnails
- **requests** - HTTP requests for thumbnails

## 🌍 Language Support

The application automatically detects your system language:

- **English** - Default language, always available
- **Spanish** - Full translation support
- **Other languages** - Falls back to English

### Adding New Languages

To add support for a new language:

1. Create a new JSON file in `/locales/` (e.g., `fr.json`)
2. Copy the structure from `en.json` and translate the values
3. Update the `LocalizationManager` to include the new language code

## 📁 File Structure

```
ytdl/
├── main.py                 # Application entry point
├── config.py              # Configuration settings
├── build.py               # Build script for executable
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── core/                 # Core business logic
│   ├── __init__.py
│   ├── downloader.py     # Download functionality
│   ├── video_info.py     # Video metadata handling
│   ├── utils.py          # Utility functions
│   └── localization.py   # Internationalization
├── ui/                   # User interface components
│   ├── __init__.py
│   ├── main_window.py    # Main application window
│   └── video_entry.py    # Individual video entries
├── locales/              # Translation files
│   ├── en.json          # English translations
│   ├── es.json          # Spanish translations
│   └── lang.json        # Language name mappings
└── dist/                 # Built executables (created by build script)
```

## 🔧 Configuration

### Customizing Settings

Edit `config.py` to modify:

- **App appearance** - Title, geometry, theme
- **Default paths** - Output directory, language files
- **UI dimensions** - Thumbnail sizes, window dimensions
- **Links** - Website and support links

### Language Files

Translation files are located in `/locales/`:

- **`en.json`** - English translations
- **`es.json`** - Spanish translations
- **`lang.json`** - Language name mappings for audio/subtitle languages

## 🚀 Building and Distribution

### Development Build

```bash
python main.py
```

### Production Build

```bash
python build.py
```

This creates a standalone executable in `/dist/` that includes:

- All Python dependencies
- Translation files
- Configuration files
- No Python installation required on target machine

### Build Requirements

- **PyInstaller** - For creating executables
- **All application dependencies** - Listed in `requirements.txt`

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch
3. **Make** your changes
4. **Test** thoroughly
5. **Submit** a pull request

### Development Setup

```bash
# Clone repository
git clone <repository-url>
cd ytdl

# Install dependencies
pip install -r requirements.txt

# Run in development mode
python main.py
```

## 📄 License

This project is open source. Feel free to use, modify, and distribute.

## 👨‍💻 Author

**Oscar R.C.**

- Website: [oscarrc.me](https://oscarrc.me)
- Support: [Buy me a coffee](https://ko-fi.com/oscarrc)

## 🆘 Support

If you encounter any issues:

1. Check the **Prerequisites** section
2. Ensure all **dependencies** are installed
3. Verify **Python version** (3.8+)
4. Check **file permissions** for output directory

For additional support, visit the project page or contact the author.

---

**Made with ❤️ by Oscar R.C.**
