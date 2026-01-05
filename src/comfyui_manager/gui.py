"""
Main GUI Window for ComfyUI Manager
"""

import tkinter as tk
from tkinter import ttk, font
import logging
from pathlib import Path
import webbrowser
import sys

from .widgets.dialogs import AboutDialog, SettingsDialog
from .widgets.widgets import StatusBar, SystemMonitor
from .process_manager import ProcessManager
from .system_monitor import SystemMonitorThread

class ComfyUIManager:
    """Main application window."""
    
    def __init__(self, config):
        self.config = config
        self.process_manager = ProcessManager(config)
        self.system_monitor = SystemMonitorThread(config)
        
        self.root = None
        self.notebook = None
        self.status_bar = None
        
        self.setup_gui()
        self.create_menu_bar()
        self.setup_bindings()
    
    def setup_gui(self):
        """Initialize the main window."""
        self.root = tk.Tk()
        self.root.title("ComfyUI Manager")
        self.root.geometry("1000x700")
        
        # Set icon if available
        icon_path = Path(__file__).parent / "assets" / "icons" / "app_icon.png"
        if icon_path.exists():
            try:
                from PIL import Image, ImageTk
                img = Image.open(icon_path)
                photo = ImageTk.PhotoImage(img)
                self.root.iconphoto(False, photo)
                # Keep reference to prevent garbage collection
                self.icon_photo = photo
            except ImportError:
                pass
            except Exception as e:
                logging.warning(f"Could not load icon: {e}")
        
        # Apply theme
        self.apply_theme()
        
        # Create menu
        self.create_menu_bar()
        
        # Create main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Create notebook for tabs
        self.create_notebook(main_frame)
        
        # Create status bar
        self.status_bar = StatusBar(main_frame)
        self.status_bar.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Start system monitor
        self.system_monitor.start()
        self.root.after(1000, self.update_monitor)
    
    def create_notebook(self, parent):
        """Create tabbed interface."""
        self.notebook = ttk.Notebook(parent)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        
        # Create tabs
        self.create_dashboard_tab()
        self.create_control_tab()
        self.create_monitor_tab()
        self.create_config_tab()
        self.create_logs_tab()
    
    def create_dashboard_tab(self):
        """Create dashboard tab."""
        from .widgets.widgets import DashboardTab
        dashboard = DashboardTab(self.notebook, self.config, self.process_manager)
        self.notebook.add(dashboard, text="📊 Dashboard")
    
    def create_control_tab(self):
        """Create control tab."""
        from .widgets.widgets import ControlTab
        control = ControlTab(self.notebook, self.config, self.process_manager)
        self.notebook.add(control, text="🎮 Control")
    
    def create_monitor_tab(self):
        """Create system monitor tab."""
        from .widgets.widgets import MonitorTab
        monitor = MonitorTab(self.notebook, self.config, self.system_monitor)
        self.notebook.add(monitor, text="📈 Monitor")
    
    def create_config_tab(self):
        """Create configuration tab."""
        from .widgets.widgets import ConfigTab
        config_tab = ConfigTab(self.notebook, self.config)
        self.notebook.add(config_tab, text="⚙️ Config")
    
    def create_logs_tab(self):
        """Create logs tab."""
        from .widgets.widgets import LogsTab
        logs = LogsTab(self.notebook, self.config)
        self.notebook.add(logs, text="📝 Logs")
    
    def create_menu_bar(self):
        """Create menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Web UI", command=self.open_webui)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Clear Cache", command=self.clear_cache)
        tools_menu.add_command(label="Backup Workflows", command=self.backup_workflows)
        tools_menu.add_command(label="Open Outputs", command=self.open_outputs)
        
        # Settings menu
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="Preferences", command=self.open_settings)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Documentation", command=self.open_docs)
        help_menu.add_command(label="Check for Updates", command=self.check_updates)
        help_menu.add_separator()
        help_menu.add_command(label="About", command=self.open_about)
    

    def apply_theme(self):
        """Apply theme to the application."""
        # Create style object
        style = ttk.Style()
        
        # List available themes
        available_themes = style.theme_names()
        print(f"Available themes: {available_themes}")
        
        # Try to use a nice theme
        preferred_themes = ['clam', 'alt', 'default', 'classic']
        
        for theme in preferred_themes:
            if theme in available_themes:
                try:
                    style.theme_use(theme)
                    print(f"Using theme: {theme}")
                    break
                except:
                    continue
        
        # Configure some basic styles
        try:
            # Configure button colors
            style.configure('TButton', 
                        padding=6, 
                        relief="flat",
                        background="#4CAF50")
            
            style.map('TButton',
                    background=[('active', '#45a049')])
            
            # Configure label frame
            style.configure('TLabelframe', 
                        background='#f0f0f0',
                        borderwidth=2,
                        relief="groove")
            
            style.configure('TLabelframe.Label',
                        background='#f0f0f0',
                        font=('Arial', 10, 'bold'))
            
            # Configure notebook
            style.configure('TNotebook',
                        background='#f0f0f0',
                        borderwidth=0)
            
            style.configure('TNotebook.Tab',
                        padding=[10, 5],
                        font=('Arial', 10))
            
        except Exception as e:
            print(f"Could not configure styles: {e}")

    def setup_bindings(self):
        """Set up keyboard bindings."""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.bind("<Control-q>", lambda e: self.on_closing())
        self.root.bind("<F5>", lambda e: self.refresh_all())
    
    def update_monitor(self):
        """Update system monitor displays."""
        if self.system_monitor.running:
            # Update status bar
            cpu = self.system_monitor.cpu_percent
            mem = self.system_monitor.memory_percent
            gpu = self.system_monitor.gpu_percent
            
            status_text = f"CPU: {cpu:.1f}% | Memory: {mem:.1f}% | GPU: {gpu:.1f}%"
            self.status_bar.set_text(status_text)
            
            # Schedule next update
            self.root.after(1000, self.update_monitor)
    
    def open_webui(self):
        """Open ComfyUI web interface."""
        port = self.config.get("port", 8188)
        webbrowser.open(f"http://localhost:{port}")
    
    def clear_cache(self):
        """Clear system cache."""
        from .widgets.dialogs import confirmation_dialog
        if confirmation_dialog(self.root, "Clear Cache", "Clear all cache files?"):
            success = self.process_manager.clear_cache()
            if success:
                logging.info("Cache cleared successfully")
            else:
                logging.error("Failed to clear cache")
    
    def backup_workflows(self):
        """Backup workflows."""
        success = self.process_manager.backup_workflows()
        if success:
            logging.info("Workflows backed up successfully")
        else:
            logging.error("Failed to backup workflows")
    
    def open_outputs(self):
        """Open outputs directory."""
        import subprocess
        output_dir = self.config.get("output_dir")
        if output_dir and Path(output_dir).exists():
            try:
                if sys.platform == "win32":
                    os.startfile(output_dir)
                elif sys.platform == "darwin":
                    subprocess.run(["open", output_dir])
                else:
                    subprocess.run(["xdg-open", output_dir])
            except Exception as e:
                logging.error(f"Failed to open outputs directory: {e}")
    
    def open_settings(self):
        """Open settings dialog."""
        dialog = SettingsDialog(self.root, self.config)
        self.root.wait_window(dialog.top)
    
    def open_docs(self):
        """Open documentation."""
        webbrowser.open("https://github.com/tuusuario/comfyui-manager/docs")
    
    def check_updates(self):
        """Check for updates."""
        from .widgets.dialogs import info_dialog
        info_dialog(self.root, "Updates", "Update check functionality coming soon!")
    
    def open_about(self):
        """Open about dialog."""
        dialog = AboutDialog(self.root)
        self.root.wait_window(dialog.top)
    
    def refresh_all(self):
        """Refresh all tabs."""
        # Refresh each tab
        for tab in self.notebook.tabs():
            widget = self.notebook.nametowidget(tab)
            if hasattr(widget, 'refresh'):
                widget.refresh()
    
    def on_closing(self):
        """Handle window closing."""
        from .widgets.dialogs import confirmation_dialog
        
        if self.process_manager.is_running():
            if not confirmation_dialog(
                self.root, 
                "ComfyUI Running", 
                "ComfyUI is currently running. Stop it and exit?"
            ):
                return
        
        # Stop system monitor
        self.system_monitor.stop()
        
        # Stop ComfyUI if running
        if self.process_manager.is_running():
            self.process_manager.stop()
        
        # Save configuration
        self.config.save()
        
        # Close window
        self.root.quit()
        self.root.destroy()
    
    def run(self):
        """Run the application."""
        # Center window
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
        # Start main loop
        self.root.mainloop()