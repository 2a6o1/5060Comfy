"""
Custom widgets for ComfyUI Manager
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
from datetime import datetime
from pathlib import Path

class StatusBar(ttk.Frame):
    """Status bar widget."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.text_var = tk.StringVar(value="Ready")
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI elements."""
        self.status_label = ttk.Label(
            self,
            textvariable=self.text_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
            padding=(5, 2)
        )
        self.status_label.pack(fill=tk.X)
    
    def set_text(self, text):
        """Set status text."""
        self.text_var.set(text)

class SystemMonitor:
    """System monitoring widget."""
    
    def __init__(self, parent, **kwargs):
        self.parent = parent
        self.frame = ttk.Frame(parent, **kwargs)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI elements."""
        # CPU
        cpu_frame = ttk.LabelFrame(self.frame, text="CPU", padding=10)
        cpu_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.cpu_label = ttk.Label(cpu_frame, text="0%", font=("Arial", 14))
        self.cpu_label.pack()
        self.cpu_bar = ttk.Progressbar(cpu_frame, length=150)
        self.cpu_bar.pack(pady=5)
        
        # Memory
        mem_frame = ttk.LabelFrame(self.frame, text="Memory", padding=10)
        mem_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.mem_label = ttk.Label(mem_frame, text="0%", font=("Arial", 14))
        self.mem_label.pack()
        self.mem_bar = ttk.Progressbar(mem_frame, length=150)
        self.mem_bar.pack(pady=5)
        
        # GPU
        gpu_frame = ttk.LabelFrame(self.frame, text="GPU", padding=10)
        gpu_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.gpu_label = ttk.Label(gpu_frame, text="0%", font=("Arial", 14))
        self.gpu_label.pack()
        self.gpu_bar = ttk.Progressbar(gpu_frame, length=150)
        self.gpu_bar.pack(pady=5)
    
    def update_cpu(self, percent):
        """Update CPU display."""
        self.cpu_label.config(text=f"{percent:.1f}%")
        self.cpu_bar['value'] = percent
    
    def update_memory(self, percent):
        """Update memory display."""
        self.mem_label.config(text=f"{percent:.1f}%")
        self.mem_bar['value'] = percent
    
    def update_gpu(self, percent):
        """Update GPU display."""
        self.gpu_label.config(text=f"{percent:.1f}%")
        self.gpu_bar['value'] = percent


class DashboardTab(ttk.Frame):
    """Dashboard tab."""
    
    def __init__(self, parent, config, process_manager):
        super().__init__(parent)
        self.config = config
        self.process_manager = process_manager
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI elements."""
        # Title
        title_label = ttk.Label(
            self,
            text="ComfyUI Dashboard",
            font=("Arial", 16, "bold")
        )
        title_label.pack(pady=(10, 20))
        
        # Quick stats frame
        stats_frame = ttk.LabelFrame(self, text="Quick Stats", padding=10)
        stats_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        # Stats grid
        self.status_value = ttk.Label(stats_frame, text="⏹️ Stopped", font=("Arial", 10, "bold"))
        self.mode_value = ttk.Label(stats_frame, text="Normal VRAM", font=("Arial", 10, "bold"))
        self.images_value = ttk.Label(stats_frame, text="0", font=("Arial", 10, "bold"))
        self.queue_value = ttk.Label(stats_frame, text="0", font=("Arial", 10, "bold"))
        
        stats = [
            ("Status:", self.status_value),
            ("Memory Mode:", self.mode_value),
            ("Images:", self.images_value),
            ("Queue:", self.queue_value),
        ]
        
        for i, (label, value_widget) in enumerate(stats):
            lbl = ttk.Label(stats_frame, text=label, font=("Arial", 10))
            lbl.grid(row=i//2, column=(i%2)*2, sticky=tk.W, padx=5, pady=2)
            value_widget.grid(row=i//2, column=(i%2)*2+1, sticky=tk.W, padx=5, pady=2)
        
        # Quick actions
        actions_frame = ttk.LabelFrame(self, text="Quick Actions", padding=10)
        actions_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        # Buttons
        self.start_btn = ttk.Button(
            actions_frame,
            text="🚀 Start ComfyUI",
            command=self.start_comfyui,
            width=15
        )
        self.start_btn.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W+tk.E)
        
        self.stop_btn = ttk.Button(
            actions_frame,
            text="🛑 Stop ComfyUI",
            command=self.stop_comfyui,
            width=15,
            state=tk.DISABLED
        )
        self.stop_btn.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        
        self.open_webui_btn = ttk.Button(
            actions_frame,
            text="🌐 Open WebUI",
            command=self.open_webui,
            width=15
        )
        self.open_webui_btn.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W+tk.E)
        
        self.clear_cache_btn = ttk.Button(
            actions_frame,
            text="🗑️ Clear Cache",
            command=self.clear_cache,
            width=15
        )
        self.clear_cache_btn.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        
        # Configure grid weights
        for i in range(2):
            actions_frame.columnconfigure(i, weight=1)
        
        # Memory mode quick selector
        mode_frame = ttk.LabelFrame(self, text="Quick Memory Mode", padding=10)
        mode_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        # Mode buttons
        mode_buttons_frame = ttk.Frame(mode_frame)
        mode_buttons_frame.pack(fill=tk.X)
        
        modes = [
            ("Low", "lowvram", "For GPUs with ≤ 4GB"),
            ("Normal", "normalvram", "Recommended for RTX 5060"),
            ("High", "highvram", "For GPUs with ≥ 12GB"),
        ]
        
        for text, mode, desc in modes:
            btn_frame = ttk.Frame(mode_buttons_frame)
            btn_frame.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
            
            btn = ttk.Button(
                btn_frame,
                text=text,
                command=lambda m=mode: self.set_memory_mode(m),
                width=8
            )
            btn.pack()
            
            desc_label = ttk.Label(btn_frame, text=desc, font=("Arial", 8))
            desc_label.pack()
        
        # System info
        info_frame = ttk.LabelFrame(self, text="System Information", padding=10)
        info_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        comfyui_path = self.config.get('comfyui_path', 'Not set')
        output_dir = self.config.get('output_dir', 'Not set')
        port = self.config.get('port', 8188)
        
        info_text = f"""ComfyUI Path: {comfyui_path}
Output Directory: {output_dir}
Port: {port}"""
        
        info_label = ttk.Label(info_frame, text=info_text, justify=tk.LEFT)
        info_label.pack(anchor=tk.W)
        
        # Start periodic updates
        self.after(1000, self.update_dashboard)
    
    def set_memory_mode(self, mode):
        """Set memory mode from dashboard."""
        mode_names = {
            "lowvram": "Low VRAM",
            "normalvram": "Normal VRAM",
            "highvram": "High VRAM",
        }
        
        from . import dialogs
        if dialogs.confirmation_dialog(
            self, 
            "Change Memory Mode",
            f"Change memory mode to {mode_names.get(mode, mode)}?\n"
            "This will take effect on next start."
        ):
            # In a real implementation, you would save this preference
            print(f"Memory mode set to: {mode}")
    
    def start_comfyui(self):
        """Start ComfyUI."""
        from . import dialogs
        if dialogs.confirmation_dialog(self, "Start ComfyUI", "Start ComfyUI now?"):
            # Use normalvram as default from dashboard
            success = self.process_manager.start("normalvram")
            
            if success:
                self.start_btn.config(state=tk.DISABLED)
                self.stop_btn.config(state=tk.NORMAL)
            else:
                dialogs.info_dialog(self, "Error", "Failed to start ComfyUI")
    
    def stop_comfyui(self):
        """Stop ComfyUI."""
        from . import dialogs
        if dialogs.confirmation_dialog(self, "Stop ComfyUI", "Stop ComfyUI now?"):
            success = self.process_manager.stop()
            
            if success:
                self.start_btn.config(state=tk.NORMAL)
                self.stop_btn.config(state=tk.DISABLED)
            else:
                dialogs.info_dialog(self, "Error", "Failed to stop ComfyUI")
    
    def open_webui(self):
        """Open WebUI."""
        import webbrowser
        port = self.config.get("port", 8188)
        webbrowser.open(f"http://localhost:{port}")
    
    def clear_cache(self):
        """Clear cache."""
        from . import dialogs
        if dialogs.confirmation_dialog(self, "Clear Cache", "Clear all cache files?"):
            print("Clearing cache...")
            # Implement cache clearing here
    
    def update_dashboard(self):
        """Update dashboard display."""
        # Update status
        is_running = self.process_manager.is_running()
        
        if is_running:
            self.status_value.config(text="🟢 Running", foreground="green")
            self.mode_value.config(text="Running", foreground="green")
        else:
            self.status_value.config(text="⏹️ Stopped", foreground="red")
            self.mode_value.config(text="Normal VRAM", foreground="black")
        
        # Update button states
        if is_running:
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
        else:
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
        
        # Schedule next update
        self.after(1000, self.update_dashboard)
    
    def refresh(self):
        """Refresh dashboard."""
        self.update_dashboard()
   


class ControlTab(ttk.Frame):
    """Control tab."""
    
    def __init__(self, parent, config, process_manager):
        super().__init__(parent)
        self.config = config
        self.process_manager = process_manager
        self.setup_ui()
        self.update_button_states()
    
    def setup_ui(self):
        """Setup UI elements."""
        # Memory mode selection
        mode_frame = ttk.LabelFrame(self, text="Memory Mode", padding=10)
        mode_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Description
        desc_label = ttk.Label(
            mode_frame,
            text="Select memory mode based on your GPU VRAM:",
            font=("Arial", 9)
        )
        desc_label.pack(anchor=tk.W, pady=(0, 10))
        
        self.mode_var = tk.StringVar(value="normalvram")
        
        modes = [
            ("lowvram", "Low VRAM (≤ 4GB) - Models loaded to GPU only when needed"),
            ("normalvram", "Normal VRAM (6-8GB) - Recommended for RTX 5060"),
            ("highvram", "High VRAM (≥ 12GB) - Keep all models in GPU memory"),
            ("cpu", "CPU Only - No GPU, very slow"),
        ]
        
        for value, text in modes:
            frame = ttk.Frame(mode_frame)
            frame.pack(fill=tk.X, pady=2)
            
            rb = ttk.Radiobutton(
                frame,
                text=text,
                value=value,
                variable=self.mode_var,
                command=self.on_mode_change,
                width=50
            )
            rb.pack(side=tk.LEFT, anchor=tk.W)
            
            # Add small indicator
            if value == "normalvram":
                indicator = ttk.Label(frame, text="✓ Recommended", foreground="green")
                indicator.pack(side=tk.RIGHT, padx=10)
        
        # Control buttons
        buttons_frame = ttk.Frame(self)
        buttons_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        self.start_btn = ttk.Button(
            buttons_frame,
            text="🚀 Start ComfyUI",
            command=self.start_comfyui,
            width=20
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(
            buttons_frame,
            text="🛑 Stop ComfyUI",
            command=self.stop_comfyui,
            width=20
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        self.restart_btn = ttk.Button(
            buttons_frame,
            text="↻ Restart",
            command=self.restart_comfyui,
            width=20
        )
        self.restart_btn.pack(side=tk.LEFT, padx=5)
        
        # Status indicator
        status_frame = ttk.LabelFrame(self, text="Status", padding=10)
        status_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        self.status_label = ttk.Label(
            status_frame,
            text="Status: Stopped",
            font=("Arial", 10, "bold")
        )
        self.status_label.pack(anchor=tk.W)
        
        self.pid_label = ttk.Label(
            status_frame,
            text="PID: N/A",
            font=("Arial", 10)
        )
        self.pid_label.pack(anchor=tk.W)
        
        self.mode_label = ttk.Label(
            status_frame,
            text="Mode: Not running",
            font=("Arial", 10)
        )
        self.mode_label.pack(anchor=tk.W)
        
        # Log output
        log_frame = ttk.LabelFrame(self, text="Output", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        self.log_text = tk.Text(log_frame, height=10)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(self.log_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.log_text.yview)
        
        # Start periodic status update
        self.after(1000, self.update_status)
    
    def on_mode_change(self):
        """Handle mode change."""
        mode = self.mode_var.get()
        mode_names = {
            "lowvram": "Low VRAM",
            "normalvram": "Normal VRAM",
            "highvram": "High VRAM",
            "cpu": "CPU Only"
        }
        self.log(f"Memory mode changed to: {mode_names.get(mode, mode)}")
    
    def start_comfyui(self):
        """Start ComfyUI by executing the bash script with memory mode."""
        mode = self.mode_var.get()
        mode_names = {
            "lowvram": "Low VRAM",
            "normalvram": "Normal VRAM",
            "highvram": "High VRAM",
            "cpu": "CPU Only"
        }
        mode_display = mode_names.get(mode, mode)
        
        self.log(f"Starting ComfyUI in {mode_display} mode...")
        
        # Ask for confirmation
        from .dialogs import confirmation_dialog
        if not confirmation_dialog(self, "Start ComfyUI", 
                                  f"Start ComfyUI in {mode_display} mode?"):
            return
        
        # Start ComfyUI using process manager
        success = self.process_manager.start(mode)
        
        if success:
            self.log(f"✓ ComfyUI started successfully in {mode_display} mode")
            self.update_button_states()
        else:
            self.log("✗ Failed to start ComfyUI")
    
    def stop_comfyui(self):
        """Stop ComfyUI."""
        self.log("Stopping ComfyUI...")
        
        # Ask for confirmation
        from .dialogs import confirmation_dialog
        if not confirmation_dialog(self, "Stop ComfyUI", "Stop ComfyUI now?"):
            return
        
        # Stop ComfyUI using process manager
        success = self.process_manager.stop()
        
        if success:
            self.log("✓ ComfyUI stopped successfully")
            self.update_button_states()
        else:
            self.log("✗ Failed to stop ComfyUI")
    
    def restart_comfyui(self):
        """Restart ComfyUI."""
        mode = self.mode_var.get()
        mode_names = {
            "lowvram": "Low VRAM",
            "normalvram": "Normal VRAM",
            "highvram": "High VRAM",
            "cpu": "CPU Only"
        }
        mode_display = mode_names.get(mode, mode)
        
        self.log(f"Restarting ComfyUI in {mode_display} mode...")
        
        # Stop first, then start
        if self.process_manager.is_running():
            self.stop_comfyui()
            # Wait 2 seconds before restarting
            self.after(2000, lambda: self.start_comfyui())
        else:
            self.start_comfyui()
    
    def update_button_states(self):
        """Update button states based on process status."""
        is_running = self.process_manager.is_running()
        
        if is_running:
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.restart_btn.config(state=tk.NORMAL)
        else:
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            self.restart_btn.config(state=tk.DISABLED)
    
    def update_status(self):
        """Update status display."""
        is_running = self.process_manager.is_running()
        
        if is_running:
            self.status_label.config(text="Status: Running", foreground="green")
            pid = self.process_manager.get_pid()
            self.pid_label.config(text=f"PID: {pid}")
            self.mode_label.config(text=f"Mode: Running")
        else:
            self.status_label.config(text="Status: Stopped", foreground="red")
            self.pid_label.config(text="PID: N/A")
            
            # Show selected mode
            mode = self.mode_var.get()
            mode_names = {
                "lowvram": "Low VRAM",
                "normalvram": "Normal VRAM",
                "highvram": "High VRAM",
                "cpu": "CPU Only"
            }
            mode_display = mode_names.get(mode, mode)
            self.mode_label.config(text=f"Mode: {mode_display} (selected)")
        
        # Schedule next update
        self.after(1000, self.update_status)
    
    def log(self, message):
        """Add message to log."""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
    
    def refresh(self):
        """Refresh control tab."""
        self.update_button_states()
        self.update_status()


class MonitorTab(ttk.Frame):
    """Monitor tab."""
    
    def __init__(self, parent, config, system_monitor):
        super().__init__(parent)
        self.config = config
        self.system_monitor = system_monitor
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI elements."""
        # System Monitor
        monitor = SystemMonitor(self)
        monitor.frame.pack(fill=tk.X, padx=20, pady=20)
        self.monitor_widget = monitor
        
        # Stats
        stats_frame = ttk.LabelFrame(self, text="Detailed Statistics", padding=10)
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Create treeview for stats
        columns = ("Metric", "Value")
        self.stats_tree = ttk.Treeview(
            stats_frame,
            columns=columns,
            show="headings",
            height=10
        )
        
        # Define headings
        self.stats_tree.heading("Metric", text="Metric")
        self.stats_tree.heading("Value", text="Value")
        
        # Define columns
        self.stats_tree.column("Metric", width=200)
        self.stats_tree.column("Value", width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(
            stats_frame,
            orient=tk.VERTICAL,
            command=self.stats_tree.yview
        )
        self.stats_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview and scrollbar
        self.stats_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Add sample data
        sample_data = [
            ("CPU Cores", "16"),
            ("Total Memory", "32 GB"),
            ("GPU Memory", "8 GB"),
            ("Disk Space", "512 GB"),
            ("Python Version", "3.11.5"),
            ("PyTorch Version", "2.1.0"),
        ]
        
        for item in sample_data:
            self.stats_tree.insert("", tk.END, values=item)
        
        # Start updating monitor
        self.after(1000, self.update_monitor)
    
    def update_monitor(self):
        """Update monitor widgets."""
        if hasattr(self.system_monitor, 'cpu_percent'):
            self.monitor_widget.update_cpu(self.system_monitor.cpu_percent)
            self.monitor_widget.update_memory(self.system_monitor.memory_percent)
            self.monitor_widget.update_gpu(self.system_monitor.gpu_percent)
        
        # Schedule next update
        self.after(1000, self.update_monitor)
    
    def refresh(self):
        """Refresh monitor tab."""
        print("Refreshing monitor tab...")

class ConfigTab(ttk.Frame):
    """Configuration tab."""
    
    def __init__(self, parent, config):
        super().__init__(parent)
        self.config = config
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI elements."""
        # Settings frame
        settings_frame = ttk.LabelFrame(self, text="Settings", padding=10)
        settings_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Create a canvas with scrollbar for many settings
        canvas = tk.Canvas(settings_frame)
        scrollbar = ttk.Scrollbar(settings_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Add settings
        self.create_settings(scrollable_frame)
        
        # Pack canvas and scrollbar
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Buttons
        buttons_frame = ttk.Frame(self)
        buttons_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        save_btn = ttk.Button(
            buttons_frame,
            text="💾 Save Settings",
            command=self.save_settings,
            width=15
        )
        save_btn.pack(side=tk.RIGHT, padx=5)
        
        load_btn = ttk.Button(
            buttons_frame,
            text="📂 Load Settings",
            command=self.load_settings,
            width=15
        )
        load_btn.pack(side=tk.RIGHT, padx=5)
        
        reset_btn = ttk.Button(
            buttons_frame,
            text="🔄 Reset to Defaults",
            command=self.reset_settings,
            width=15
        )
        reset_btn.pack(side=tk.RIGHT, padx=5)
    
    def create_settings(self, parent):
        """Create settings widgets."""
        row = 0
        
        # ComfyUI Path
        ttk.Label(parent, text="ComfyUI Path:").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.comfyui_path_var = tk.StringVar(
            value=self.config.get("comfyui_path", "")
        )
        comfyui_entry = ttk.Entry(
            parent,
            textvariable=self.comfyui_path_var,
            width=50
        )
        comfyui_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        row += 1
        
        # Output Directory
        ttk.Label(parent, text="Output Directory:").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.output_dir_var = tk.StringVar(
            value=self.config.get("output_dir", "")
        )
        output_entry = ttk.Entry(
            parent,
            textvariable=self.output_dir_var,
            width=50
        )
        output_entry.grid(row=row, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        row += 1
        
        # Port
        ttk.Label(parent, text="Port:").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.port_var = tk.IntVar(value=self.config.get("port", 8188))
        port_spinbox = ttk.Spinbox(
            parent,
            from_=1,
            to=65535,
            textvariable=self.port_var,
            width=10
        )
        port_spinbox.grid(row=row, column=1, sticky=tk.W, pady=5, padx=(5, 0))
        row += 1
        
        # GPU Optimizations
        ttk.Label(parent, text="GPU Optimizations:").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        row += 1
        
        self.tf32_var = tk.BooleanVar(value=self.config.get("enable_tf32", True))
        tf32_cb = ttk.Checkbutton(
            parent,
            text="TF32 Precision",
            variable=self.tf32_var
        )
        tf32_cb.grid(row=row, column=1, sticky=tk.W, pady=2)
        row += 1
        
        self.cudnn_var = tk.BooleanVar(value=self.config.get("enable_cudnn_benchmark", True))
        cudnn_cb = ttk.Checkbutton(
            parent,
            text="cudNN Benchmark",
            variable=self.cudnn_var
        )
        cudnn_cb.grid(row=row, column=1, sticky=tk.W, pady=2)
        row += 1
        
        # Configure grid weights
        parent.columnconfigure(1, weight=1)
    
    def save_settings(self):
        """Save settings."""
        self.config.set("comfyui_path", self.comfyui_path_var.get())
        self.config.set("output_dir", self.output_dir_var.get())
        self.config.set("port", self.port_var.get())
        self.config.set("enable_tf32", self.tf32_var.get())
        self.config.set("enable_cudnn_benchmark", self.cudnn_var.get())
        
        if self.config.save():
            print("Settings saved successfully")
        else:
            print("Failed to save settings")
    
    def load_settings(self):
        """Load settings."""
        print("Loading settings...")
    
    def reset_settings(self):
        """Reset settings to defaults."""
        print("Resetting settings...")
    
    def refresh(self):
        """Refresh config tab."""
        print("Refreshing config tab...")

class LogsTab(ttk.Frame):
    """Logs tab."""
    
    def __init__(self, parent, config):
        super().__init__(parent)
        self.config = config
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI elements."""
        # Controls frame
        controls_frame = ttk.Frame(self)
        controls_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Filter options
        ttk.Label(controls_frame, text="Filter:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.filter_var = tk.StringVar()
        filter_entry = ttk.Entry(
            controls_frame,
            textvariable=self.filter_var,
            width=30
        )
        filter_entry.pack(side=tk.LEFT, padx=5)
        
        # Level filter
        ttk.Label(controls_frame, text="Level:").pack(side=tk.LEFT, padx=(20, 5))
        
        self.level_var = tk.StringVar(value="ALL")
        level_combo = ttk.Combobox(
            controls_frame,
            textvariable=self.level_var,
            values=["ALL", "INFO", "WARNING", "ERROR"],
            state="readonly",
            width=10
        )
        level_combo.pack(side=tk.LEFT, padx=5)
        
        # Buttons
        refresh_btn = ttk.Button(
            controls_frame,
            text="🔄 Refresh",
            command=self.refresh_logs,
            width=10
        )
        refresh_btn.pack(side=tk.RIGHT, padx=5)
        
        clear_btn = ttk.Button(
            controls_frame,
            text="🧹 Clear",
            command=self.clear_logs,
            width=10
        )
        clear_btn.pack(side=tk.RIGHT, padx=5)
        
        # Log display
        log_frame = ttk.LabelFrame(self, text="Logs", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Text widget for logs
        self.log_text = tk.Text(log_frame, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.log_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.log_text.yview)
        
        # Add sample logs
        self.add_sample_logs()
    
    def add_sample_logs(self):
        """Add sample log entries."""
        sample_logs = [
            "[10:25:52] [INFO] ComfyUI Manager started",
            "[10:26:15] [INFO] Loading configuration",
            "[10:26:30] [INFO] System monitor started",
            "[10:27:00] [INFO] GPU detected: NVIDIA RTX 5060",
            "[10:27:15] [INFO] Ready to start ComfyUI",
        ]
        
        for log in sample_logs:
            self.log_text.insert(tk.END, log + "\n")
    
    def refresh_logs(self):
        """Refresh log display."""
        print("Refreshing logs...")
    
    def clear_logs(self):
        """Clear log display."""
        self.log_text.delete(1.0, tk.END)
    
    def refresh(self):
        """Refresh logs tab."""
        print("Refreshing logs tab...")