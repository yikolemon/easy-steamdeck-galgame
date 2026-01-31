#!/bin/bash

# SteamDeck PyInstaller Cross-Platform Build Script
# Build standalone executables for different architectures on standard Linux
# Supports: x86_64, ARM64 (SteamDeck and other platforms)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

# Get target architecture (defaults to current system architecture)
TARGET_ARCH="${1:-native}"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
}

print_success() {
    echo -e "${GREEN}[OK] $1${NC}"
}

print_error() {
    echo -e "${RED}[FAIL] $1${NC}"
}

print_info() {
    echo -e "${BLUE}[INFO] $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}[WARN] $1${NC}"
}

# ============================================================================
# Show usage information
# ============================================================================
show_usage() {
    cat << EOF
Usage: bash build_pyinstaller_crossplatform.sh [architecture]

Supported architectures:
    native      Build for current system (default)
    x86_64      Build for x86_64 (SteamDeck, most Linux PCs)
    aarch64     Build for ARM64/aarch64

Examples:
    bash build_pyinstaller_crossplatform.sh              # Build for current system
    bash build_pyinstaller_crossplatform.sh x86_64       # Build for x86_64
    bash build_pyinstaller_crossplatform.sh aarch64      # Build for ARM64

Requirements:
    - Python 3.7+
    - pip or pip3
    - (Cross-compile) Appropriate build tools for target architecture

Output files:
    dist/steamdeck-galgame                    (executable)
    dist/steamdeck-galgame-{arch}.tar.gz      (distribution package)

EOF
    exit 1
}

# ============================================================================
# Check arguments
# ============================================================================
if [[ "$TARGET_ARCH" == "-h" || "$TARGET_ARCH" == "--help" ]]; then
    show_usage
fi

# ============================================================================
# Check dependencies
# ============================================================================
check_command() {
    if ! command -v $1 &> /dev/null; then
        print_error "Missing $1, please install"
        return 1
    fi
    print_success "$1 installed"
    return 0
}

print_header "Checking system dependencies"

check_command python3 || exit 1
check_command pip3 || exit 1

# Get Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
print_info "Python version: $PYTHON_VERSION"

# Get system architecture
SYSTEM_ARCH=$(uname -m)
print_info "System architecture: $SYSTEM_ARCH"

# ============================================================================
# Cross-compile architecture setup
# ============================================================================
print_header "Setting up build architecture"

if [[ "$TARGET_ARCH" == "native" ]]; then
    print_info "Building for native architecture"
    EFFECTIVE_ARCH="$SYSTEM_ARCH"
elif [[ "$TARGET_ARCH" == "x86_64" ]]; then
    if [[ "$SYSTEM_ARCH" == "x86_64" ]]; then
        EFFECTIVE_ARCH="x86_64"
        print_info "System is already x86_64, no cross-compile needed"
    else
        EFFECTIVE_ARCH="x86_64"
        print_warning "Cross-compiling: $SYSTEM_ARCH -> x86_64"
        print_warning "Ensure appropriate cross-compile toolchain is installed"
    fi
elif [[ "$TARGET_ARCH" == "aarch64" ]]; then
    if [[ "$SYSTEM_ARCH" == "aarch64" ]]; then
        EFFECTIVE_ARCH="aarch64"
        print_info "System is already aarch64, no cross-compile needed"
    else
        EFFECTIVE_ARCH="aarch64"
        print_warning "Cross-compiling: $SYSTEM_ARCH -> aarch64"
        print_warning "Ensure appropriate cross-compile toolchain is installed"
    fi
else
    print_error "Unknown architecture: $TARGET_ARCH"
    show_usage
fi

# ============================================================================
# Set up Python virtual environment
# ============================================================================
print_header "Setting up Python virtual environment"

VENV_DIR="venv_${EFFECTIVE_ARCH}"

if [ -d "$VENV_DIR" ]; then
    print_warning "Virtual environment already exists: $VENV_DIR, skipping"
else
    print_info "Creating virtual environment: $VENV_DIR..."
    python3 -m venv "$VENV_DIR"
    print_success "Virtual environment created"
fi

# Activate virtual environment
source "$VENV_DIR/bin/activate"

# ============================================================================
# Install dependencies
# ============================================================================
print_header "Installing Python dependencies"

print_info "Upgrading pip..."
pip install --upgrade pip

print_info "Installing project dependencies..."
pip install -r requirements.txt

print_info "Installing PyInstaller..."
pip install pyinstaller

print_success "All dependencies installed"

# ============================================================================
# Clean old builds
# ============================================================================
print_header "Cleaning old build files"

print_info "Removing build/ dist/ directories..."
rm -rf build dist __pycache__ .pytest_cache

print_info "Cleaning caches..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true

print_success "Cleanup complete"

# ============================================================================
# Build executable
# ============================================================================
print_header "Building PyInstaller executable"

EXECUTABLE_NAME="steamdeck-galgame"
OUTPUT_DIR="dist"

print_info "Target architecture: $EFFECTIVE_ARCH"
print_info "Output name: $EXECUTABLE_NAME"
print_info "Output directory: $OUTPUT_DIR"
echo ""

# Set environment variables for PyInstaller
export ARCHFLAGS=""  # Clear any architecture flags

# Run PyInstaller
print_info "Running PyInstaller..."
echo ""

pyinstaller \
    --name "$EXECUTABLE_NAME" \
    --onefile \
    --console \
    --add-data "data/icons:data/icons" \
    --hidden-import=src \
    --hidden-import=src.tui \
    --hidden-import=src.core \
    --hidden-import=src.core.installers \
    --hidden-import=src.utils \
    --hidden-import=requests \
    --collect-all=rich \
    --strip \
    --clean \
    run.py

echo ""

# ============================================================================
# Verify output
# ============================================================================
print_header "Verifying build results"

EXECUTABLE_PATH="$OUTPUT_DIR/$EXECUTABLE_NAME"

if [ -f "$EXECUTABLE_PATH" ]; then
    print_success "Executable generated: $EXECUTABLE_PATH"
    
    # Display file size
    FILE_SIZE=$(ls -lh "$EXECUTABLE_PATH" | awk '{print $5}')
    print_info "File size: $FILE_SIZE"
    
    # Display file info
    echo ""
    print_info "File type:"
    file "$EXECUTABLE_PATH"
    
    # Display architecture info
    echo ""
    if command -v file &> /dev/null; then
        ARCH_INFO=$(file "$EXECUTABLE_PATH" | grep -oP '(x86-64|ARM|aarch64|x86)' || echo "unknown")
        print_info "Detected architecture: $ARCH_INFO"
    fi
else
    print_error "Build failed!"
    print_error "File not found: $EXECUTABLE_PATH"
    exit 1
fi

# ============================================================================
# Create distribution package
# ============================================================================
print_header "Creating distribution package"

TARBALL_NAME="${EXECUTABLE_NAME}-${EFFECTIVE_ARCH}-$(date +%Y%m%d).tar.gz"
TARBALL_PATH="$OUTPUT_DIR/$TARBALL_NAME"

print_info "Creating package: $TARBALL_NAME..."
cd "$OUTPUT_DIR"
tar -czf "$TARBALL_NAME" "$EXECUTABLE_NAME"
cd "$PROJECT_ROOT"

if [ -f "$TARBALL_PATH" ]; then
    TARBALL_SIZE=$(ls -lh "$TARBALL_PATH" | awk '{print $5}')
    print_success "Package created: $TARBALL_PATH"
    print_info "Package size: $TARBALL_SIZE"
else
    print_warning "Package creation failed, but executable is ready"
fi

# ============================================================================
# Display usage instructions
# ============================================================================
print_header "Usage Instructions"

echo ""
echo "[1] Run executable directly on this system:"
echo "    $EXECUTABLE_PATH"
echo ""

if [[ "$EFFECTIVE_ARCH" == "x86_64" ]]; then
    echo "[2] Copy to SteamDeck and run:"
    echo "    scp $EXECUTABLE_PATH deck@steamdeck:~/"
    echo "    ssh deck@steamdeck"
    echo "    chmod +x ~/$EXECUTABLE_NAME"
    echo "    ~/$EXECUTABLE_NAME"
    echo ""
fi

echo "[3] Or copy the distribution package:"
echo "    scp $TARBALL_PATH deck@steamdeck:~/"
echo "    ssh deck@steamdeck"
echo "    tar -xzf $TARBALL_NAME"
echo "    chmod +x $EXECUTABLE_NAME"
echo "    ./$EXECUTABLE_NAME"
echo ""

echo "No Python, pip, or dependencies needed!"
echo ""

# ============================================================================
# Display completion information
# ============================================================================
print_header "Build Complete"

echo ""
echo "Output files:"
echo "    Executable: $EXECUTABLE_PATH"
echo "    Package:    $TARBALL_PATH (optional)"
echo ""

echo "Build information:"
echo "    Architecture: $EFFECTIVE_ARCH"
echo "    File size:    $FILE_SIZE"
echo "    Timestamp:    $(date)"
echo ""

echo "Next steps:"
echo "    1. Test the executable: $EXECUTABLE_PATH"
echo "    2. Upload to GitHub Releases"
echo "    3. Share with users for download"
echo ""

print_success "All operations complete!"

echo "════════════════════════════════════════════════════════════════"
