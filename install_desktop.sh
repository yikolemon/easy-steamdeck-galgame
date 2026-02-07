#!/bin/bash
#
# Install desktop shortcut for SteamDeck Galgame Tool
# This script creates a .desktop file so the app can be launched from the application menu
#
# Usage:
#   ./install_desktop.sh [path_to_executable]
#
# If no path is provided, it will look for the executable in the current directory.
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DESKTOP_FILE="steamdeck-galgame.desktop"
DESKTOP_TEMPLATE="${SCRIPT_DIR}/${DESKTOP_FILE}"

# Find the executable
if [ -n "$1" ]; then
    EXEC_PATH="$1"
elif [ -f "${SCRIPT_DIR}/steamdeck-galgame" ]; then
    EXEC_PATH="${SCRIPT_DIR}/steamdeck-galgame"
elif [ -f "${SCRIPT_DIR}/dist/steamdeck-galgame" ]; then
    EXEC_PATH="${SCRIPT_DIR}/dist/steamdeck-galgame"
else
    echo "ERROR: Could not find steamdeck-galgame executable."
    echo "Usage: $0 [path_to_executable]"
    echo ""
    echo "Examples:"
    echo "  $0 /home/deck/steamdeck-galgame"
    echo "  $0 ./dist/steamdeck-galgame"
    exit 1
fi

# Get absolute path
EXEC_PATH="$(realpath "$EXEC_PATH")"

# Verify executable exists
if [ ! -f "$EXEC_PATH" ]; then
    echo "ERROR: Executable not found: $EXEC_PATH"
    exit 1
fi

# Make sure it's executable
chmod +x "$EXEC_PATH"

echo "Installing desktop shortcut..."
echo "Executable: $EXEC_PATH"

# Create user applications directory if needed
APPLICATIONS_DIR="${HOME}/.local/share/applications"
mkdir -p "$APPLICATIONS_DIR"

# Create the desktop file with correct exec path
DEST_DESKTOP="${APPLICATIONS_DIR}/${DESKTOP_FILE}"

if [ -f "$DESKTOP_TEMPLATE" ]; then
    # Use template and replace placeholder
    sed "s|EXEC_PATH_PLACEHOLDER|${EXEC_PATH}|g" "$DESKTOP_TEMPLATE" > "$DEST_DESKTOP"
else
    # Create desktop file directly
    cat > "$DEST_DESKTOP" << EOF
[Desktop Entry]
Name=SteamDeck Galgame
Name[zh_CN]=SteamDeck 中文游戏助手
Comment=Configure Chinese/Japanese game environment on SteamDeck
Comment[zh_CN]=SteamDeck 中文/日文游戏环境配置工具
Exec=${EXEC_PATH}
Icon=applications-games
Terminal=false
Type=Application
Categories=Game;Utility;
Keywords=steamdeck;galgame;chinese;japanese;fonts;locale;
StartupNotify=true
EOF
fi

# Make desktop file executable (for KDE/Plasma)
chmod +x "$DEST_DESKTOP"

# Update desktop database
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "$APPLICATIONS_DIR" 2>/dev/null || true
fi

echo ""
echo "SUCCESS: Desktop shortcut installed!"
echo "Location: $DEST_DESKTOP"
echo ""
echo "You can now:"
echo "  1. Find 'SteamDeck Galgame' in your application menu"
echo "  2. Or copy the shortcut to your desktop:"
echo "     cp '$DEST_DESKTOP' ~/Desktop/"
echo ""
