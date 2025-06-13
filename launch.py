#!/usr/bin/env python3
"""
Launcher script for Minecraft Skin Animation Slicer
This script handles dependency checking and provides helpful error messages.
"""

import sys
import os

def check_dependencies():
    """Check if all required dependencies are installed"""
    missing_deps = []
    
    try:
        import PIL
    except ImportError:
        missing_deps.append("Pillow")
    
    try:
        import customtkinter
    except ImportError:
        missing_deps.append("customtkinter")
    
    return missing_deps

def main():
    """Launch the Minecraft Skin Animation Slicer"""
    print("🎮 Minecraft Skin Animation Slicer")
    print("=" * 40)
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Error: Python 3.7 or newer is required!")
        print(f"   Current version: {sys.version}")
        input("Press Enter to exit...")
        return
    
    # Check dependencies
    print("🔍 Checking dependencies...")
    missing_deps = check_dependencies()
    
    if missing_deps:
        print(f"❌ Missing dependencies: {', '.join(missing_deps)}")
        print("\n📦 To install missing dependencies, run:")
        print("   pip install -r requirements.txt")
        input("Press Enter to exit...")
        return
    
    print("✅ All dependencies found!")
    
    # Try to launch the application
    try:
        print("🚀 Starting application...")
        from animation_slicer import main as app_main
        app_main()
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        print("\n🛠️  Troubleshooting tips:")
        print("   1. Make sure all files are in the same directory")
        print("   2. Try running: python animation_slicer.py")
        print("   3. Check that your display supports GUI applications")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main() 