"""
Utility functions for ComfyUI Manager
"""

import sys
import subprocess
import platform
from pathlib import Path
import logging

def check_tkinter():
    """Check if tkinter is available."""
    try:
        import tkinter
        return True, f"tkinter {tkinter.TkVersion}"
    except ImportError:
        return False, "tkinter not found"

def check_python_version():
    """Check Python version."""
    version = sys.version_info
    return version.major >= 3 and version.minor >= 8, f"{version.major}.{version.minor}.{version.micro}"

def install_system_dependencies():
    """Install system-level dependencies."""
    system = platform.system()
    
    install_commands = {
        "Linux": {
            "Debian/Ubuntu": "sudo apt-get install python3-tk",
            "Fedora": "sudo dnf install python3-tkinter",
            "Arch": "sudo pacman -S tk",
        },
        "Darwin": "brew install python-tk",
        "Windows": "Tkinter comes with Python on Windows",
    }
    
    if system == "Linux":
        # Try to detect distribution
        try:
            with open("/etc/os-release", "r") as f:
                content = f.read().lower()
                if "ubuntu" in content or "debian" in content:
                    return install_commands["Linux"]["Debian/Ubuntu"]
                elif "fedora" in content:
                    return install_commands["Linux"]["Fedora"]
                elif "arch" in content:
                    return install_commands["Linux"]["Arch"]
        except:
            pass
    
    return install_commands.get(system, "")

def check_dependencies():
    """Check all dependencies and return status."""
    dependencies = []
    
    # Check Python version
    py_ok, py_version = check_python_version()
    dependencies.append(("Python >=3.8", py_ok, py_version))
    
    # Check tkinter
    tk_ok, tk_version = check_tkinter()
    dependencies.append(("tkinter", tk_ok, tk_version))
    
    # Check other packages
    packages = ["PIL", "psutil", "python_dotenv"]
    for pkg in packages:
        try:
            __import__(pkg.replace("-", "_"))
            dependencies.append((pkg, True, "Installed"))
        except ImportError:
            dependencies.append((pkg, False, "Not installed"))
    
    return dependencies

def setup_logging():
    """Setup logging configuration."""
    log_dir = Path.home() / ".comfyui-manager" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / "comfyui_manager.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    return str(log_file)

def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = Path(__file__).parent.parent.parent
    
    return str(Path(base_path) / relative_path)