#!/bin/bash

# ComfyUI Manager Installer
# Run with: bash scripts/install.sh

set -e

echo "========================================="
echo "ComfyUI Manager Installer"
echo "========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check command
check_command() {
    if ! command -v $1 &> /dev/null; then
        echo -e "${RED}Error: $1 is not installed${NC}"
        return 1
    fi
    return 0
}

# Check prerequisites
echo -e "${BLUE}Checking prerequisites...${NC}"

# Check Python
if ! check_command python3; then
    exit 1
fi

# Check Python version
python_version=$(python3 --version 2>/dev/null | cut -d' ' -f2)
python_major=$(echo $python_version | cut -d. -f1)
python_minor=$(echo $python_version | cut -d. -f2)

if [[ $python_major -lt 3 ]] || [[ $python_major -eq 3 && $python_minor -lt 8 ]]; then
    echo -e "${RED}Python 3.8 or higher is required (found $python_version)${NC}"
    exit 1
fi

echo -e "${GREEN}Python $python_version detected${NC}"

# Check tkinter
echo -e "${BLUE}Checking for tkinter...${NC}"
if python3 -c "import tkinter" 2>/dev/null; then
    tk_version=$(python3 -c "import tkinter; print('tkinter', tkinter.TkVersion)")
    echo -e "${GREEN}$tk_version detected${NC}"
else
    echo -e "${YELLOW}tkinter not found. It may need to be installed separately.${NC}"
    echo ""
    echo "To install tkinter:"
    echo "  Ubuntu/Debian: sudo apt-get install python3-tk"
    echo "  Fedora:        sudo dnf install python3-tkinter"
    echo "  Arch:          sudo pacman -S tk"
    echo "  macOS:         Comes with Python from python.org"
    echo "  Windows:       Comes with Python installer"
    echo ""
    read -p "Continue anyway? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check for virtual environment
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo -e "${YELLOW}No virtual environment detected. Creating one...${NC}"
    
    # Create venv
    python3 -m venv venv
    
    # Activate venv
    if [[ -f "venv/bin/activate" ]]; then
        source venv/bin/activate
        echo -e "${GREEN}Virtual environment activated${NC}"
    else
        echo -e "${RED}Failed to create virtual environment${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}Using existing virtual environment: $VIRTUAL_ENV${NC}"
fi

# Upgrade pip
echo -e "${BLUE}Upgrading pip...${NC}"
pip install --upgrade pip

# Install requirements
echo -e "${BLUE}Installing requirements...${NC}"
if [[ -f "requirements.txt" ]]; then
    pip install -r requirements.txt
else
    echo -e "${RED}requirements.txt not found${NC}"
    exit 1
fi

# Install in development mode
echo -e "${BLUE}Installing package in development mode...${NC}"
pip install -e .

# Create directories
echo -e "${BLUE}Creating directories...${NC}"
mkdir -p logs
mkdir -p config
mkdir -p assets/icons

# Create default icon if missing
if [[ ! -f "assets/icons/app_icon.png" ]]; then
    echo -e "${YELLOW}Creating placeholder icon...${NC}"
    # Create a simple placeholder icon using PIL if available
    python3 -c "
try:
    from PIL import Image, ImageDraw
    img = Image.new('RGB', (256, 256), color='#3498db')
    d = ImageDraw.Draw(img)
    d.ellipse([(50, 50), (206, 206)], fill='#2c3e50')
    d.text((128, 128), 'CM', fill='white', anchor='mm', font_size=100)
    img.save('assets/icons/app_icon.png')
    print('Icon created')
except ImportError:
    pass
" 2>/dev/null || true
fi

# Copy example config if it doesn't exist
if [[ ! -f ".env" ]] && [[ -f ".env.example" ]]; then
    echo -e "${YELLOW}Copying .env.example to .env${NC}"
    cp .env.example .env
    echo -e "${YELLOW}Please edit .env with your configuration${NC}"
fi

# Create desktop entry (Linux)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo -e "${BLUE}Creating desktop entry...${NC}"
    
    DESKTOP_DIR="$HOME/.local/share/applications"
    mkdir -p "$DESKTOP_DIR"
    DESKTOP_ENTRY="$DESKTOP_DIR/comfyui-manager.desktop"
    
    cat > "$DESKTOP_ENTRY" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=ComfyUI Manager
Comment=GUI Manager for ComfyUI
Exec=$(pwd)/scripts/run.sh
Icon=$(pwd)/assets/icons/app_icon.png
Terminal=false
Categories=Graphics;AI;
Keywords=comfyui;ai;stable-diffusion;
EOF
    
    chmod +x "$DESKTOP_ENTRY"
    echo -e "${GREEN}Desktop entry created at $DESKTOP_ENTRY${NC}"
fi

# Create run script
echo -e "${BLUE}Creating run script...${NC}"
cat > scripts/run.sh << 'EOF'
#!/bin/bash

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"

# Activate virtual environment if it exists
if [[ -f "$PROJECT_DIR/venv/bin/activate" ]]; then
    source "$PROJECT_DIR/venv/bin/activate"
fi

# Run the application
cd "$PROJECT_DIR"
python -m comfyui_manager.main "$@"
EOF

chmod +x scripts/run.sh

# Create simple launcher
cat > comfyui-manager << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
./scripts/run.sh "$@"
EOF

chmod +x comfyui-manager

echo ""
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}Installation complete!${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo -e "To run ComfyUI Manager:"
echo -e "  ${BLUE}./comfyui-manager${NC}"
echo -e "  ${BLUE}./scripts/run.sh${NC}"
echo ""
echo -e "Or from anywhere after activating venv:"
echo -e "  ${BLUE}comfyui-manager${NC}"
echo ""
echo -e "Next steps:"
echo -e "1. Edit ${YELLOW}.env${NC} file with your paths"
echo -e "2. Configure ComfyUI location in the app"
echo -e "3. Launch with ${BLUE}./comfyui-manager${NC}"
echo ""