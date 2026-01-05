#!/usr/bin/env python3
"""
ComfyUI Manager - Main Entry Point
A GUI application to manage ComfyUI with system monitoring and optimizations.
"""

import sys
import os
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from comfyui_manager.gui import ComfyUIManager
from comfyui_manager.config_manager import ConfigManager
from comfyui_manager.utils import setup_logging, check_dependencies, check_tkinter

def check_system_requirements():
    """Check if system meets requirements."""
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    
    # Check tkinter
    tk_available, tk_version = check_tkinter()
    if not tk_available:
        print("❌ Error: tkinter is not available")
        print("   On Ubuntu/Debian: sudo apt-get install python3-tk")
        print("   On Fedora: sudo dnf install python3-tkinter")
        print("   On Arch: sudo pacman -S tk")
        return False
    
    return True

def main():
    """Main entry point for the application."""
    
    # Check system requirements first
    if not check_system_requirements():
        sys.exit(1)
    
    # Setup logging
    log_file = setup_logging()
    logging.info("Starting ComfyUI Manager")
    
    # Load configuration
    config = ConfigManager()
    
    # Create and run application
    try:
        app = ComfyUIManager(config)
        app.run()
    except Exception as e:
        logging.error(f"Application error: {e}", exc_info=True)
        print(f"❌ Error: {e}")
        sys.exit(1)
    
    logging.info("Application closed")

if __name__ == "__main__":
    main()