#!/bin/bash
#
# Uninstall script for SteamDeck Galgame Tool
# This script removes the desktop shortcut and optionally the application files
#
# Usage:
#   ./uninstall.sh           # Remove desktop shortcut only
#   ./uninstall.sh --all     # Remove desktop shortcut and application files
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DESKTOP_FILE="steamdeck-galgame.desktop"
APPLICATIONS_DIR="${HOME}/.local/share/applications"
DEST_DESKTOP="${APPLICATIONS_DIR}/${DESKTOP_FILE}"

echo "SteamDeck Galgame Uninstaller"
echo "=============================="
echo ""

# Check for --all flag
REMOVE_ALL=false
if [ "$1" = "--all" ] || [ "$1" = "-a" ]; then
    REMOVE_ALL=true
fi

# Remove desktop shortcut
if [ -f "$DEST_DESKTOP" ]; then
    echo "Removing desktop shortcut..."
    rm -f "$DEST_DESKTOP"
    echo "[OK] Removed: $DEST_DESKTOP"
else
    echo "[SKIP] Desktop shortcut not found: $DEST_DESKTOP"
fi

# Remove from desktop if exists
DESKTOP_SHORTCUT="${HOME}/Desktop/${DESKTOP_FILE}"
if [ -f "$DESKTOP_SHORTCUT" ]; then
    echo "Removing desktop icon..."
    rm -f "$DESKTOP_SHORTCUT"
    echo "[OK] Removed: $DESKTOP_SHORTCUT"
fi

# Update desktop database
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$APPLICATIONS_DIR" 2>/dev/null || true
fi

# Remove application files if --all specified
if [ "$REMOVE_ALL" = true ]; then
    echo ""
    echo "Removing application files..."
    
    # List of files to remove (relative to script directory)
    FILES_TO_REMOVE=(
        "steamdeck-galgame"
        "steamdeck-galgame.desktop"
        "install_desktop.sh"
        "uninstall.sh"
        "README.txt"
    )
    
    for file in "${FILES_TO_REMOVE[@]}"; do
        FILE_PATH="${SCRIPT_DIR}/${file}"
        if [ -f "$FILE_PATH" ]; then
            rm -f "$FILE_PATH"
            echo "[OK] Removed: $FILE_PATH"
        fi
    done
    
    # Try to remove the directory if empty
    if [ -d "$SCRIPT_DIR" ] && [ -z "$(ls -A "$SCRIPT_DIR")" ]; then
        rmdir "$SCRIPT_DIR"
        echo "[OK] Removed empty directory: $SCRIPT_DIR"
    fi
fi

echo ""
echo "=============================="
echo "Uninstallation completed!"
echo ""

if [ "$REMOVE_ALL" = false ]; then
    echo "Note: Application files were not removed."
    echo "To completely remove everything, run:"
    echo "  ./uninstall.sh --all"
    echo ""
    echo "Or manually delete the application directory:"
    echo "  rm -rf \"$SCRIPT_DIR\""
fi
echo ""
