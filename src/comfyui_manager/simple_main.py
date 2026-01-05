#!/usr/bin/env python3
"""
Simple version to test basic functionality
"""

import tkinter as tk
from tkinter import ttk
import sys

def main():
    """Simple test of tkinter."""
    root = tk.Tk()
    root.title("ComfyUI Manager - Test")
    root.geometry("400x300")
    
    label = ttk.Label(root, text="ComfyUI Manager is working!", font=("Arial", 14))
    label.pack(pady=50)
    
    button = ttk.Button(root, text="Exit", command=root.quit)
    button.pack()
    
    root.mainloop()

if __name__ == "__main__":
    main()