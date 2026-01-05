"""
Dialog windows for ComfyUI Manager
"""

import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
from pathlib import Path
import json

class AboutDialog:
    """About dialog window."""
    
    def __init__(self, parent):
        self.parent = parent
        self.top = tk.Toplevel(parent)
        self.top.title("About ComfyUI Manager")
        self.top.geometry("400x300")
        self.top.resizable(False, False)
        
        # Make dialog modal
        self.top.transient(parent)
        self.top.grab_set()
        
        self.setup_ui()
        self.center_window()
    
    def setup_ui(self):
        """Setup UI elements."""
        # Main frame
        main_frame = ttk.Frame(self.top, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="ComfyUI Manager",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(0, 10))
        
        # Version
        version_label = ttk.Label(
            main_frame,
            text="Version 1.0.0",
            font=("Arial", 10)
        )
        version_label.pack(pady=(0, 20))
        
        # Description
        description = """
A graphical user interface for managing ComfyUI
with system monitoring and optimizations.

Features:
• One-click ComfyUI control
• System resource monitoring
• Performance optimizations
• Easy configuration management
• Real-time log viewer
"""
        desc_label = ttk.Label(
            main_frame,
            text=description,
            justify=tk.LEFT
        )
        desc_label.pack(pady=(0, 20))
        
        # Links frame
        links_frame = ttk.Frame(main_frame)
        links_frame.pack(fill=tk.X, pady=(0, 10))
        
        # GitHub link
        github_btn = ttk.Button(
            links_frame,
            text="GitHub",
            command=self.open_github,
            width=10
        )
        github_btn.pack(side=tk.LEFT, padx=5)
        
        # Documentation link
        docs_btn = ttk.Button(
            links_frame,
            text="Documentation",
            command=self.open_docs,
            width=10
        )
        docs_btn.pack(side=tk.LEFT, padx=5)
        
        # Close button
        close_btn = ttk.Button(
            main_frame,
            text="Close",
            command=self.top.destroy,
            width=10
        )
        close_btn.pack()
    
    def open_github(self):
        """Open GitHub repository."""
        webbrowser.open("https://github.com/2a6o1/5060Comfy")
    
    def open_docs(self):
        """Open documentation."""
        webbrowser.open("https://github.com/2a6o1/5060Comfy")
    
    def center_window(self):
        """Center the dialog window."""
        self.top.update_idletasks()
        width = self.top.winfo_width()
        height = self.top.winfo_height()
        x = (self.top.winfo_screenwidth() // 2) - (width // 2)
        y = (self.top.winfo_screenheight() // 2) - (height // 2)
        self.top.geometry(f'{width}x{height}+{x}+{y}')

class SettingsDialog:
    """Settings dialog window."""
    
    def __init__(self, parent, config):
        self.parent = parent
        self.config = config
        self.top = tk.Toplevel(parent)
        self.top.title("Settings")
        self.top.geometry("600x500")
        
        # Make dialog modal
        self.top.transient(parent)
        self.top.grab_set()
        
        self.setup_ui()
        self.center_window()
    
    def setup_ui(self):
        """Setup UI elements."""
        # Create notebook for tabs
        notebook = ttk.Notebook(self.top)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Paths tab
        paths_frame = ttk.Frame(notebook, padding=10)
        notebook.add(paths_frame, text="Paths")
        self.create_paths_tab(paths_frame)
        
        # Network tab
        network_frame = ttk.Frame(notebook, padding=10)
        notebook.add(network_frame, text="Network")
        self.create_network_tab(network_frame)
        
        # GPU tab
        gpu_frame = ttk.Frame(notebook, padding=10)
        notebook.add(gpu_frame, text="GPU")
        self.create_gpu_tab(gpu_frame)
        
        # UI tab
        ui_frame = ttk.Frame(notebook, padding=10)
        notebook.add(ui_frame, text="UI")
        self.create_ui_tab(ui_frame)
        
        # Buttons frame
        buttons_frame = ttk.Frame(self.top)
        buttons_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Save button
        save_btn = ttk.Button(
            buttons_frame,
            text="Save",
            command=self.save_settings,
            width=10
        )
        save_btn.pack(side=tk.RIGHT, padx=5)
        
        # Cancel button
        cancel_btn = ttk.Button(
            buttons_frame,
            text="Cancel",
            command=self.top.destroy,
            width=10
        )
        cancel_btn.pack(side=tk.RIGHT, padx=5)
    
    def create_paths_tab(self, parent):
        """Create paths configuration tab."""
        # ComfyUI Path
        ttk.Label(parent, text="ComfyUI Path:").grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        self.comfyui_path_var = tk.StringVar(
            value=self.config.get("comfyui_path", "")
        )
        comfyui_entry = ttk.Entry(
            parent,
            textvariable=self.comfyui_path_var,
            width=50
        )
        comfyui_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        
        browse_comfyui_btn = ttk.Button(
            parent,
            text="Browse",
            command=lambda: self.browse_directory(self.comfyui_path_var),
            width=10
        )
        browse_comfyui_btn.grid(row=0, column=2, padx=(5, 0))
        
        # Output Directory
        ttk.Label(parent, text="Output Directory:").grid(
            row=1, column=0, sticky=tk.W, pady=5
        )
        self.output_dir_var = tk.StringVar(
            value=self.config.get("output_dir", "")
        )
        output_entry = ttk.Entry(
            parent,
            textvariable=self.output_dir_var,
            width=50
        )
        output_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        
        browse_output_btn = ttk.Button(
            parent,
            text="Browse",
            command=lambda: self.browse_directory(self.output_dir_var),
            width=10
        )
        browse_output_btn.grid(row=1, column=2, padx=(5, 0))
        
        # Temp Directory
        ttk.Label(parent, text="Temp Directory:").grid(
            row=2, column=0, sticky=tk.W, pady=5
        )
        self.temp_dir_var = tk.StringVar(
            value=self.config.get("temp_dir", "")
        )
        temp_entry = ttk.Entry(
            parent,
            textvariable=self.temp_dir_var,
            width=50
        )
        temp_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        
        browse_temp_btn = ttk.Button(
            parent,
            text="Browse",
            command=lambda: self.browse_directory(self.temp_dir_var),
            width=10
        )
        browse_temp_btn.grid(row=2, column=2, padx=(5, 0))
        
        # Auto-detect button
        auto_detect_btn = ttk.Button(
            parent,
            text="Auto-detect ComfyUI",
            command=self.auto_detect_comfyui,
            width=15
        )
        auto_detect_btn.grid(row=3, column=0, columnspan=3, pady=20)
        
        # Configure grid weights
        parent.columnconfigure(1, weight=1)
    
    def create_network_tab(self, parent):
        """Create network configuration tab."""
        # Host
        ttk.Label(parent, text="Host:").grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        self.host_var = tk.StringVar(
            value=self.config.get("host", "0.0.0.0")
        )
        host_entry = ttk.Entry(parent, textvariable=self.host_var, width=20)
        host_entry.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(5, 0))
        
        # Port
        ttk.Label(parent, text="Port:").grid(
            row=1, column=0, sticky=tk.W, pady=5
        )
        self.port_var = tk.IntVar(value=self.config.get("port", 8188))
        port_spinbox = ttk.Spinbox(
            parent,
            from_=1,
            to=65535,
            textvariable=self.port_var,
            width=10
        )
        port_spinbox.grid(row=1, column=1, sticky=tk.W, pady=5, padx=(5, 0))
        
        parent.columnconfigure(1, weight=1)
    
    def create_gpu_tab(self, parent):
        """Create GPU configuration tab."""
        # Device
        ttk.Label(parent, text="CUDA Device:").grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        self.cuda_device_var = tk.IntVar(
            value=self.config.get("cuda_device", 0)
        )
        device_spinbox = ttk.Spinbox(
            parent,
            from_=0,
            to=7,
            textvariable=self.cuda_device_var,
            width=5
        )
        device_spinbox.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(5, 0))
        
        # Optimizations
        self.enable_tf32_var = tk.BooleanVar(
            value=self.config.get("enable_tf32", True)
        )
        tf32_cb = ttk.Checkbutton(
            parent,
            text="Enable TF32 Precision",
            variable=self.enable_tf32_var
        )
        tf32_cb.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        self.enable_cudnn_bench_var = tk.BooleanVar(
            value=self.config.get("enable_cudnn_benchmark", True)
        )
        cudnn_cb = ttk.Checkbutton(
            parent,
            text="Enable cudNN Benchmark",
            variable=self.enable_cudnn_bench_var
        )
        cudnn_cb.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        self.enable_cuda_malloc_var = tk.BooleanVar(
            value=self.config.get("enable_cuda_malloc_async", True)
        )
        cuda_malloc_cb = ttk.Checkbutton(
            parent,
            text="Enable cudaMallocAsync",
            variable=self.enable_cuda_malloc_var
        )
        cuda_malloc_cb.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        parent.columnconfigure(1, weight=1)
    
    def create_ui_tab(self, parent):
        """Create UI configuration tab."""
        # Theme
        ttk.Label(parent, text="Theme:").grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        self.theme_var = tk.StringVar(
            value=self.config.get("theme", "dark")
        )
        theme_combo = ttk.Combobox(
            parent,
            textvariable=self.theme_var,
            values=["light", "dark", "system"],
            state="readonly",
            width=15
        )
        theme_combo.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(5, 0))
        
        # Language
        ttk.Label(parent, text="Language:").grid(
            row=1, column=0, sticky=tk.W, pady=5
        )
        self.language_var = tk.StringVar(
            value=self.config.get("language", "en")
        )
        lang_combo = ttk.Combobox(
            parent,
            textvariable=self.language_var,
            values=["en", "es"],  # Add more as needed
            state="readonly",
            width=15
        )
        lang_combo.grid(row=1, column=1, sticky=tk.W, pady=5, padx=(5, 0))
        
        # Auto-update
        self.auto_update_var = tk.BooleanVar(
            value=self.config.get("auto_update_check", True)
        )
        auto_update_cb = ttk.Checkbutton(
            parent,
            text="Check for updates automatically",
            variable=self.auto_update_var
        )
        auto_update_cb.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        parent.columnconfigure(1, weight=1)
    
    def browse_directory(self, path_var):
        """Browse for directory and update path variable."""
        from tkinter import filedialog
        directory = filedialog.askdirectory(
            title="Select Directory",
            initialdir=Path.home()
        )
        if directory:
            path_var.set(directory)
    
    def auto_detect_comfyui(self):
        """Try to auto-detect ComfyUI installation."""
        import os
        from pathlib import Path
        
        possible_paths = [
            Path.home() / "ComfyUI",
            Path.home() / "comfyui",
            Path.home() / "stable-diffusion" / "ComfyUI",
            Path("/opt/ComfyUI"),
            Path("/myfiles/ssd/stuff/projects/ComfyUI"),  # Tu ruta específica
        ]
        
        for path in possible_paths:
            if path.exists() and (path / "main.py").exists():
                self.comfyui_path_var.set(str(path))
                return
        
        # Show message if not found
        messagebox.showinfo(
            "Auto-detect",
            "Could not auto-detect ComfyUI installation.\nPlease set the path manually."
        )
    
    def save_settings(self):
        """Save settings to configuration."""
        # Update config
        self.config.set("comfyui_path", self.comfyui_path_var.get())
        self.config.set("output_dir", self.output_dir_var.get())
        self.config.set("temp_dir", self.temp_dir_var.get())
        self.config.set("host", self.host_var.get())
        self.config.set("port", self.port_var.get())
        self.config.set("cuda_device", self.cuda_device_var.get())
        self.config.set("enable_tf32", self.enable_tf32_var.get())
        self.config.set("enable_cudnn_benchmark", self.enable_cudnn_bench_var.get())
        self.config.set("enable_cuda_malloc_async", self.enable_cuda_malloc_var.get())
        self.config.set("theme", self.theme_var.get())
        self.config.set("language", self.language_var.get())
        self.config.set("auto_update_check", self.auto_update_var.get())
        
        # Save config
        if self.config.save():
            messagebox.showinfo("Success", "Settings saved successfully")
            self.top.destroy()
        else:
            messagebox.showerror("Error", "Failed to save settings")
    
    def center_window(self):
        """Center the dialog window."""
        self.top.update_idletasks()
        width = self.top.winfo_width()
        height = self.top.winfo_height()
        x = (self.top.winfo_screenwidth() // 2) - (width // 2)
        y = (self.top.winfo_screenheight() // 2) - (height // 2)
        self.top.geometry(f'{width}x{height}+{x}+{y}')

def confirmation_dialog(parent, title, message):
    """Show confirmation dialog."""
    return messagebox.askyesno(title, message)

def info_dialog(parent, title, message):
    """Show information dialog."""
    messagebox.showinfo(title, message)