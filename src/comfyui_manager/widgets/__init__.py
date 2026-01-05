"""
Widgets package for ComfyUI Manager
"""

from .dialogs import AboutDialog, SettingsDialog, confirmation_dialog, info_dialog
from .widgets import StatusBar, SystemMonitor, DashboardTab, ControlTab, MonitorTab, ConfigTab, LogsTab

__all__ = [
    'AboutDialog',
    'SettingsDialog',
    'confirmation_dialog',
    'info_dialog',
    'StatusBar',
    'SystemMonitor',
    'DashboardTab',
    'ControlTab',
    'MonitorTab',
    'ConfigTab',
    'LogsTab',
]