"""
Build script for 0xDownloader application.

This script creates a standalone executable using PyInstaller.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from datetime import datetime


def check_dependencies():
    """Check if required dependencies are installed."""
    print("Checking dependencies...")
    
    try:
        import PyInstaller
        print("[OK] PyInstaller is installed")
    except ImportError:
        print("[ERROR] PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("[OK] PyInstaller installed successfully")
    
    # Check other dependencies
    required_packages = ["yt_dlp", "customtkinter", "PIL", "requests"]
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"[OK] {package} is available")
        except ImportError:
            missing_packages.append(package)
            print(f"[ERROR] {package} not found")
    
    if missing_packages:
        print(f"\nInstalling missing packages: {', '.join(missing_packages)}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("[OK] All dependencies installed")


def clean_build_directories():
    """Clean previous build artifacts."""
    print("\nCleaning previous build artifacts...")
    
    dirs_to_clean = ["build", "dist", "__pycache__"]
    files_to_clean = ["*.spec"]
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"[OK] Removed {dir_name}/")
    
    # Clean .spec files
    for spec_file in Path(".").glob("*.spec"):
        spec_file.unlink()
        print(f"[OK] Removed {spec_file}")


def create_build_spec():
    """Create PyInstaller spec file with proper configuration."""
    print("\nCreating build specification...")
    
    # Prepare data files
    datas = [
        ('locales', 'locales'),
        ('config.py', '.'),
    ]
    
    # Add icon if it exists
    icon_path = None
    icon_file = 'assets/icon.ico'  # Change this to your desired icon path
    
    if os.path.exists(icon_file):
        datas.append((icon_file, 'assets'))
        icon_path = icon_file
        print(f"[INFO] Icon file found: {icon_file}")
    else:
        print(f"[INFO] No icon file found ({icon_file})")
    
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Data files to include
datas = {datas}

# Hidden imports (modules that PyInstaller might miss)
hiddenimports = [
    'yt_dlp',
    'customtkinter',
    'PIL',
    'PIL.Image',
    'PIL.ImageTk',
    'requests',
    'json',
    'threading',
    'tkinter',
    'tkinter.filedialog',
    'tkinter.messagebox',
    'webbrowser',
    'locale',
    'os',
    'sys',
    'pathlib',
    'io',
    'subprocess',
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='0xDownloader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon={repr(icon_path)},  # Icon path
)
'''
    
    with open("oxDownloader.spec", "w", encoding="utf-8") as f:
        f.write(spec_content)
    
    print("[OK] Build specification created")


def build_executable():
    """Build the executable using PyInstaller."""
    print("\nBuilding executable...")
    
    try:
        # Run PyInstaller with the spec file
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "--noconfirm",
            "0xDownloader.spec"
        ]
        
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("[OK] Build completed successfully!")
            return True
        else:
            print("[ERROR] Build failed!")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
            
    except Exception as e:
        print(f"[ERROR] Build error: {e}")
        return False


def verify_build():
    """Verify that the build was successful."""
    print("\nVerifying build...")
    
    exe_path = Path("dist") / "0xDownloader.exe"
    
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"[OK] Executable created: {exe_path}")
        print(f"File size: {size_mb:.1f} MB")
        return True
    else:
        print("[ERROR] Executable not found!")
        return False


def create_distribution_info():
    """Create distribution information file."""
    print("\nCreating distribution info...")
    
    # Get current date in a cross-platform way
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    info_content = f"""0xDownloader - Distribution Package
Generated on: {current_date}

Contents:
- 0xDownloader.exe: Main application executable
- README.md: Documentation and usage instructions

System Requirements:
- Windows 7 or later
- No additional software installation required

Usage:
1. Double-click 0xDownloader.exe to run
2. Paste YouTube URLs and configure download options
3. Click download to start downloading videos

For support, visit: https://oscarrc.me
"""
    
    with open("dist/README.txt", "w", encoding="utf-8") as f:
        f.write(info_content)
    
    print("[OK] Distribution info created")


def main():
    """Main build process."""
    print("0xDownloader - Build Script")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("main.py"):
        print("[ERROR] main.py not found. Please run this script from the project root directory.")
        sys.exit(1)
    
    try:
        # Step 1: Check dependencies
        check_dependencies()
        
        # Step 2: Clean previous builds
        clean_build_directories()
        
        # Step 3: Create build specification
        create_build_spec()
        
        # Step 4: Build executable
        if not build_executable():
            print("[ERROR] Build failed. Check the error messages above.")
            sys.exit(1)
        
        # Step 5: Verify build
        if not verify_build():
            print("[ERROR] Build verification failed.")
            sys.exit(1)
        
        # Step 6: Create distribution info
        create_distribution_info()
        
        print("\n[SUCCESS] Build completed successfully!")
        print("Executable location: dist/0xDownloader.exe")
        print("Documentation: dist/README.txt")
        print("\nYou can now distribute the contents of the 'dist' folder.")
        
    except KeyboardInterrupt:
        print("\nBuild cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
