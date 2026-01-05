"""
Configuration management for ComfyUI Manager
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
import logging

class ConfigManager:
    """Manages application configuration."""
    
    def __init__(self, config_path: Optional[Path] = None):
        if config_path is None:
            config_path = self.get_default_config_path()  # ¡CORREGIDO!
        
        self.config_path = config_path
        self.config = self.load_config()
        
        # Set up default paths
        self.setup_default_paths()
    
    def get_default_config_path(self) -> Path:  # ¡CORREGIDO!
        """Get default configuration path."""
        # Try user config directory
        if os.name == 'posix':
            config_dir = Path.home() / '.config' / 'comfyui-manager'
        elif os.name == 'nt':
            config_dir = Path.home() / 'AppData' / 'Local' / 'comfyui-manager'
        else:
            config_dir = Path.home() / '.comfyui-manager'
        
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / 'config.json'
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        default_config = self.get_default_config()
        
        if not self.config_path.exists():
            logging.info(f"Creating new config file: {self.config_path}")
            self.save_config(default_config)
            return default_config
        
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            # Merge with defaults for missing keys
            for key, value in default_config.items():
                if key not in config:
                    config[key] = value
            
            return config
            
        except (json.JSONDecodeError, IOError) as e:
            logging.error(f"Error loading config: {e}")
            return default_config
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            # Base directory
            "base_dir": "/myfiles/ssd/stuff",
            
            # ComfyUI Paths
            "comfyui_path": "",
            "comfyui_env_path": "",
            "miniforge_path": "",
            
            # Directories
            "output_dir": "",
            "temp_dir": "",
            "log_dir": "",
            "cache_dir": "",
            
            # Network
            "host": "0.0.0.0",
            "port": 8188,
            
            # GPU Settings
            "cuda_device": 0,
            "enable_tf32": True,
            "enable_cudnn_benchmark": True,
            "enable_cuda_malloc_async": True,
            
            # Performance
            "omp_num_threads": "auto",
            "mkl_num_threads": "auto",
            
            # Startup Mode
            "startup_mode": "highvram",
            "precision_mode": "fp16",
            
            # UI Settings
            "theme": "dark",
            "language": "en",
            "auto_update_check": True,
            "check_updates_on_startup": True,
            
            # Advanced
            "extra_args": "",
            "environment_vars": {},
        }
    
    def setup_default_paths(self):
        """Setup default paths if not configured."""
        # Try to auto-detect ComfyUI
        if not self.config.get("comfyui_path"):
            possible_paths = [
                Path.home() / "ComfyUI",
                Path.home() / "comfyui",
                Path.home() / "stable-diffusion" / "ComfyUI",
                Path("/opt/ComfyUI"),
                Path("/myfiles/ssd/stuff/projects/ComfyUI"),  # Tu ruta específica
            ]
            
            for path in possible_paths:
                if path.exists() and (path / "main.py").exists():
                    self.config["comfyui_path"] = str(path)
                    logging.info(f"Auto-detected ComfyUI at: {path}")
                    break
        
        # Set default output directories
        if not self.config.get("output_dir"):
            default_output = Path.home() / "ComfyUI" / "output"
            self.config["output_dir"] = str(default_output)
        
        if not self.config.get("log_dir"):
            default_logs = Path.home() / "ComfyUI" / "logs"
            self.config["log_dir"] = str(default_logs)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value."""
        self.config[key] = value
    
    def save(self) -> bool:
        """Save configuration to file."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            logging.info(f"Configuration saved to: {self.config_path}")
            return True
        except IOError as e:
            logging.error(f"Error saving config: {e}")
            return False
    
    def save_config(self, config: Dict[str, Any]) -> bool:
        """Save given configuration."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except IOError as e:
            logging.error(f"Error saving config: {e}")
            return False
    
    def validate(self) -> Dict[str, str]:
        """Validate configuration and return errors."""
        errors = {}
        
        # Check required paths
        required_paths = ["comfyui_path"]
        for path_key in required_paths:
            path = self.get(path_key)
            if not path:
                errors[path_key] = "Path is required"
            elif not Path(path).exists():
                errors[path_key] = "Path does not exist"
        
        # Validate port
        port = self.get("port", 8188)
        if not isinstance(port, int) or port < 1 or port > 65535:
            errors["port"] = "Port must be between 1 and 65535"
        
        return errors