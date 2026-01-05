"""
Simple Process Manager for ComfyUI - Just runs the bash script
"""

import subprocess
import os
import signal
from pathlib import Path
import logging

class ProcessManager:
    """Simple manager that just runs the bash script."""
    
    def __init__(self, config):
        self.config = config
        self.process = None
        self.running = False
        
        # Get script path
        self.script_dir = Path(__file__).parent.parent.parent / "scripts"
        self.script_path = self.script_dir / "start_comfyui.sh"
        
        # Ensure script exists
        self.ensure_script_exists()
    
    def ensure_script_exists(self):
        """Ensure the bash script exists."""
        if not self.script_path.exists():
            logging.error(f"Bash script not found: {self.script_path}")
            logging.info("Creating a simple bash script...")
            self.create_simple_script()
    
    def create_simple_script(self):
        """Create a simple bash script if it doesn't exist."""
        script_content = '''#!/bin/bash
# Simple ComfyUI Starter
# This script should be replaced with your actual start_comfyui.sh

echo "========================================="
echo "Starting ComfyUI..."
echo "========================================="

# Change to your ComfyUI directory
cd /myfiles/ssd/stuff/projects/ComfyUI || {
    echo "ERROR: Cannot change to ComfyUI directory"
    exit 1
}

# Activate conda environment
source /myfiles/ssd/stuff/software/miniforge3/etc/profile.d/conda.sh
conda activate /myfiles/ssd/stuff/envs/comfyui

# Start ComfyUI
echo "Starting ComfyUI on port 8188..."
exec python main.py --listen 0.0.0.0 --port 8188 --highvram \\
    --output-directory /myfiles/ssd/stuff/outputs/comfyui \\
    --temp-directory /myfiles/ssd/stuff/temp
'''

        # Create scripts directory if it doesn't exist
        self.script_dir.mkdir(parents=True, exist_ok=True)
        
        # Write the script
        self.script_path.write_text(script_content)
        
        # Make it executable
        os.chmod(self.script_path, 0o755)
        
        logging.info(f"Created simple bash script at: {self.script_path}")
    
    def start(self, mode="highvram"):
        """Start ComfyUI by executing the bash script."""
        if self.running:
            logging.warning("ComfyUI is already running")
            return False
        
        if not self.script_path.exists():
            logging.error(f"Script not found: {self.script_path}")
            return False
        
        try:
            logging.info(f"Executing bash script: {self.script_path}")
            
            # Execute the bash script
            # Use shell=True to run as a shell script
            self.process = subprocess.Popen(
                [str(self.script_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                shell=True,
                preexec_fn=os.setsid  # Create new process group for proper signal handling
            )
            
            self.running = True
            logging.info(f"ComfyUI started with PID: {self.process.pid}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to start ComfyUI: {e}")
            return False
    
    def stop(self):
        """Stop ComfyUI process."""
        if not self.running or not self.process:
            logging.warning("ComfyUI is not running")
            return False
        
        try:
            logging.info("Stopping ComfyUI...")
            
            # Send SIGTERM to the entire process group
            os.killpg(os.getpgid(self.process.pid), signal.SIGTERM)
            
            # Wait for process to terminate
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                logging.warning("Force killing ComfyUI...")
                os.killpg(os.getpgid(self.process.pid), signal.SIGKILL)
                self.process.wait()
            
            self.running = False
            self.process = None
            
            logging.info("ComfyUI stopped")
            return True
            
        except Exception as e:
            logging.error(f"Failed to stop ComfyUI: {e}")
            return False
    
    def is_running(self):
        """Check if process is running."""
        if not self.process:
            return False
        
        # Check if process is still alive
        return self.process.poll() is None
    
    def get_pid(self):
        """Get process PID if running."""
        if self.is_running():
            return self.process.pid
        return None