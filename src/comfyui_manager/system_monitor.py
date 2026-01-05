"""
System monitoring for ComfyUI Manager
"""

import threading
import time
import psutil
from datetime import datetime
import logging

class SystemMonitorThread(threading.Thread):
    """Thread for monitoring system resources."""
    
    def __init__(self, config):
        super().__init__(daemon=True)
        self.config = config
        self.running = False
        
        # Current values
        self.cpu_percent = 0.0
        self.memory_percent = 0.0
        self.gpu_percent = 0.0
        self.gpu_memory_used = 0
        self.gpu_memory_total = 0
        
        # Try to import GPU monitoring libraries
        self.gpu_available = False
        try:
            import GPUtil
            self.gpu_available = True
            self.gputil = GPUtil
        except ImportError:
            try:
                import nvidia_smi
                self.nvidia_smi = nvidia_smi
                self.gpu_available = True
                # Initialize nvidia-smi
                self.nvidia_smi.nvmlInit()
            except ImportError:
                logging.info("GPU monitoring libraries not available")
    
    def run(self):
        """Main monitoring loop."""
        self.running = True
        logging.info("System monitor started")
        
        while self.running:
            try:
                # Update CPU usage
                self.cpu_percent = psutil.cpu_percent(interval=0.1)
                
                # Update memory usage
                memory = psutil.virtual_memory()
                self.memory_percent = memory.percent
                
                # Update GPU usage if available
                self.update_gpu_stats()
                
                # Sleep before next update
                time.sleep(1)
                
            except Exception as e:
                logging.error(f"Error in system monitor: {e}")
                time.sleep(5)
    
    def update_gpu_stats(self):
        """Update GPU statistics."""
        if not self.gpu_available:
            self.gpu_percent = 0.0
            return
        
        try:
            # Try GPUtil first
            if hasattr(self, 'gputil'):
                gpus = self.gputil.getGPUs()
                if gpus:
                    gpu = gpus[0]  # First GPU
                    self.gpu_percent = gpu.load * 100
                    self.gpu_memory_used = gpu.memoryUsed
                    self.gpu_memory_total = gpu.memoryTotal
            
            # Try nvidia-smi
            elif hasattr(self, 'nvidia_smi'):
                handle = self.nvidia_smi.nvmlDeviceGetHandleByIndex(0)
                util = self.nvidia_smi.nvmlDeviceGetUtilizationRates(handle)
                memory = self.nvidia_smi.nvmlDeviceGetMemoryInfo(handle)
                
                self.gpu_percent = util.gpu
                self.gpu_memory_used = memory.used // (1024 * 1024)  # MB
                self.gpu_memory_total = memory.total // (1024 * 1024)  # MB
        
        except Exception as e:
            logging.debug(f"GPU monitoring error: {e}")
            self.gpu_percent = 0.0
    
    def stop(self):
        """Stop the monitoring thread."""
        self.running = False
        logging.info("System monitor stopped")
        
        # Cleanup nvidia-smi if used
        if hasattr(self, 'nvidia_smi'):
            try:
                self.nvidia_smi.nvmlShutdown()
            except:
                pass
    
    def get_system_info(self):
        """Get comprehensive system information."""
        info = {
            "cpu_percent": self.cpu_percent,
            "memory_percent": self.memory_percent,
            "gpu_percent": self.gpu_percent,
            "gpu_memory": f"{self.gpu_memory_used}/{self.gpu_memory_total} MB",
            "timestamp": datetime.now().isoformat(),
        }
        
        # Add CPU info
        cpu_freq = psutil.cpu_freq()
        if cpu_freq:
            info["cpu_frequency"] = f"{cpu_freq.current:.0f} MHz"
        
        # Add memory info
        memory = psutil.virtual_memory()
        info["memory_total"] = f"{memory.total // (1024**3)} GB"
        info["memory_used"] = f"{memory.used // (1024**3)} GB"
        
        # Add disk info
        disk = psutil.disk_usage('/')
        info["disk_total"] = f"{disk.total // (1024**3)} GB"
        info["disk_used"] = f"{disk.used // (1024**3)} GB"
        info["disk_percent"] = disk.percent
        
        return info