"""
YouTube Downloader - Main Entry Point

A modern YouTube video downloader with a clean GUI interface.
"""

from ui.main_window import MainWindow


def main():
    """Main entry point for the application."""
    app = MainWindow()
    app.run()


if __name__ == "__main__":
    main()
