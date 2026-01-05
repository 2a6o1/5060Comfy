
# ComfyUI Manager

A GUI application for managing ComfyUI with system monitoring and automatic GPU optimizations specifically tuned for Ubuntu systems. Perfect for Stable Diffusion users on Ubuntu who want an easy way to start, stop, and monitor their ComfyUI instance with hardware-optimized settings for NVIDIA RTX GPUs.

Developed on Hardware
Tested and Optimized for:

Operating System: Ubuntu 24.04.3 LTS

Kernel: 6.14.0-37-generic

CPU: AMD Ryzen 7 5700 (16 cores)

RAM: 31GB DDR4

GPU: NVIDIA GeForce RTX 5060 (8GB VRAM)

GPU Memory: 8151 MiB

Open for Contributions: This project welcomes community contributions for new GPU optimizations, additional hardware support, and integration with other AI frameworks. Whether you're running on different NVIDIA cards, AMD GPUs, or other hardware configurations, your improvements are welcome!


## Documentation

[Documentation]()


## Installation

Install ComfyUI Manager with pip

```bash
  pip install comfyui-manager
  cd comfyui-manager
```
    
## Deployment

To deploy this project as a standalone executable run

```bash
  pyinstaller --onefile --windowed --name comfyui-manager src/comfyui_manager/main.py
```


## Run Locally

Clone the project

```bash
  git clone https://github.com/yourusername/comfyui-manager.git
```

Go to the project directory

```bash
  cd comfyui-manager
```

Install dependencies

```bash
  pip install -r requirements.txt
  pip install -e .
```

Start the server

```bash
  python -m comfyui_manager.main
```


## Screenshots

![App Screenshot]


## Developed on:

=== SYSTEM SUMMARY ===
OS: Ubuntu 24.04.3 LTS
Kernel: 6.14.0-37-generic
CPU: AMD Ryzen 7 5700
Cores: 16
RAM: 31Gi
GPU: NVIDIA GeForce RTX 5060
GPU Memory: 8151 MiB
===================================================
Python 3.12.12
PyTorch: 2.9.1+cu128
CUDA: True
nvidia-cublas-cu12                     12.8.4.1
nvidia-cuda-cupti-cu12                 12.8.90
nvidia-cuda-nvrtc-cu12                 12.8.93
nvidia-cuda-runtime-cu12               12.8.90
nvidia-cudnn-cu12                      9.10.2.21
nvidia-cufft-cu12                      11.3.3.83
nvidia-cufile-cu12                     1.13.1.3
nvidia-curand-cu12                     10.3.9.90
nvidia-cusolver-cu12                   11.7.3.90
nvidia-cusparse-cu12                   12.5.8.93
nvidia-cusparselt-cu12                 0.7.1
nvidia-nccl-cu12                       2.27.5
nvidia-nvjitlink-cu12                  12.8.93
nvidia-nvshmem-cu12                    3.3.20
nvidia-nvtx-cu12                       12.8.90
torch                                  2.9.1
torchaudio                             2.4.0+cu124
torchsde                               0.2.6
torchvision                            0.19.0+cu124


## Usage/Examples

Usage/Examples
Here's a step-by-step example of how to use ComfyUI Manager to optimize your Stable Diffusion workflow:

Step 1: Launch the Application
bash
# After installation, simply run:
python -m comfyui_manager.main

# Or use the shortcut script:
./scripts/run.sh
Step 2: Configure Your Setup
First-time setup example:

python
# The application will auto-detect your ComfyUI installation
# If it doesn't find it, go to Settings → Paths and set:
- ComfyUI Path: /path/to/your/ComfyUI
- Output Directory: /path/for/generated/images
- Temp Directory: /path/for/temporary/files
Step 3: Select the Right Memory Mode
Based on your GPU VRAM, choose the appropriate mode:

For RTX 5060 (8GB): Select "Normal VRAM" mode

For GPUs with ≤4GB: Select "Low VRAM" mode

For GPUs with ≥12GB: Select "High VRAM" mode

No GPU available: Select "CPU Only" mode

Step 4: Start ComfyUI with Optimizations
Click the "Start ComfyUI" button. The manager will automatically:

Apply NVIDIA CUDA optimizations

Set up memory management for your GPU

Configure cache directories

Launch ComfyUI with the correct parameters

Step 5: Monitor Your System
Use the Monitor tab to track:

GPU VRAM usage in real-time

CPU and memory utilization

System temperatures

Process status and PID

Step 6: Access the Web Interface
Once started, click "Open WebUI" to access ComfyUI at:

text
http://localhost:8188
Example Workflow:
Launch ComfyUI Manager

Select "Normal VRAM" mode (for RTX 5060)

Click "Start ComfyUI"

Monitor GPU usage in the dashboard

Click "Open WebUI" to start generating images

When finished, click "Stop ComfyUI" to free resources

Advanced Example: Batch Processing
bash
# You can also use the generated bash script directly:
./scripts/start_comfyui.sh normalvram

# Or with specific optimizations:
./scripts/start_comfyui.sh lowvram --precision fp16
Troubleshooting Example:
If you encounter "Out of Memory" errors:

Stop ComfyUI if it's running

Switch to "Low VRAM" mode

Clear cache from the Tools menu

Restart ComfyUI

Check the logs tab for detailed error messages

The manager provides real-time feedback and logging, making it easy to diagnose and fix common ComfyUI issues while maintaining optimal performance for your specific hardware configuration.

