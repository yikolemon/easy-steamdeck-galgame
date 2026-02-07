"""
Steam library management module
Handles adding non-Steam games to Steam library
"""

import os
import sys
import struct
import binascii
from typing import List, Tuple, Dict, Optional
from src.config import Config
from src.utils import get_home_dir


def debug_log(message: str):
    """Print debug message when running in debug mode"""
    # Check if running in debug mode (debug build or console available)
    if hasattr(sys, "frozen"):
        # PyInstaller bundled app - check if it's debug build
        if "debug" in sys.executable.lower():
            print(f"[DEBUG] {message}")
    else:
        # Running from source
        print(f"[DEBUG] {message}")


class SteamManager:
    """Manages Steam library operations"""

    @staticmethod
    def get_steam_userdata_dirs() -> List[str]:
        """
        Get all Steam userdata directories
        Returns: List of userdata directory paths
        """
        steam_dir = Config.get_steam_dir()
        debug_log(f"Steam userdata directory: {steam_dir}")
        debug_log(f"Directory exists: {os.path.exists(steam_dir)}")

        try:
            if not os.path.exists(steam_dir):
                debug_log(f"Steam directory does not exist: {steam_dir}")
                # Try alternative paths
                alt_paths = [
                    os.path.join(os.path.expanduser("~"), ".steam/root/userdata"),
                    os.path.join(os.path.expanduser("~"), ".steam/steam/userdata"),
                    os.path.join(
                        os.path.expanduser("~"), ".local/share/Steam/userdata"
                    ),
                ]
                for alt_path in alt_paths:
                    debug_log(f"Trying alternative path: {alt_path}")
                    if os.path.exists(alt_path):
                        debug_log(f"Found alternative path: {alt_path}")
                        steam_dir = alt_path
                        break
                else:
                    debug_log("No Steam userdata directory found in any location")
                    return []

            # List all user IDs
            debug_log(f"Listing contents of: {steam_dir}")
            user_dirs = []
            for user_id in os.listdir(steam_dir):
                user_path = os.path.join(steam_dir, user_id)
                is_dir = os.path.isdir(user_path)
                is_digit = user_id.isdigit()
                debug_log(f"  Found: {user_id} (isdir={is_dir}, isdigit={is_digit})")
                if is_dir and is_digit:
                    user_dirs.append(user_path)

            debug_log(f"Found {len(user_dirs)} user directories: {user_dirs}")
            return user_dirs
        except Exception as e:
            debug_log(f"Error getting Steam userdata directories: {e}")
            print(f"Error getting Steam userdata directories: {e}")
            return []

    @staticmethod
    def get_shortcuts_vdf_path(user_dir: str) -> str:
        """Get shortcuts.vdf file path for a user"""
        return os.path.join(user_dir, "config", "shortcuts.vdf")

    @staticmethod
    def browse_directory(path: str) -> Tuple[List[str], List[str]]:
        """
        Browse directory and return subdirectories and exe files

        Args:
            path: Directory path to browse

        Returns:
            (subdirectories, exe_files)
        """
        subdirs = []
        exe_files = []

        try:
            if not os.path.exists(path) or not os.path.isdir(path):
                return subdirs, exe_files

            for item in os.listdir(path):
                item_path = os.path.join(path, item)

                if os.path.isdir(item_path):
                    subdirs.append(item)
                elif os.path.isfile(item_path) and item.lower().endswith(".exe"):
                    exe_files.append(item)

            subdirs.sort()
            exe_files.sort()

        except Exception as e:
            print(f"Error browsing directory: {e}")

        return subdirs, exe_files

    @staticmethod
    def calculate_shortcut_id(exe_path: str, app_name: str) -> int:
        """
        Calculate Steam shortcut ID using CRC32 algorithm
        This matches Steam's internal algorithm

        Args:
            exe_path: Full path to executable
            app_name: Application name

        Returns:
            Shortcut ID
        """
        # Combine exe path and app name as Steam does
        input_string = f'"{exe_path}"{app_name}'

        # Calculate CRC32
        crc = binascii.crc32(input_string.encode("utf-8")) & 0xFFFFFFFF

        # Steam's shortcut ID is: (CRC32 | 0x80000000) << 32
        shortcut_id = (crc | 0x80000000) << 32

        return shortcut_id

    @staticmethod
    def read_vdf_shortcuts(vdf_path: str) -> List[Dict]:
        """
        Read existing shortcuts from VDF file

        Args:
            vdf_path: Path to shortcuts.vdf file

        Returns:
            List of shortcut dictionaries
        """
        shortcuts = []

        try:
            if not os.path.exists(vdf_path):
                return shortcuts

            with open(vdf_path, "rb") as f:
                data = f.read()

            # VDF binary format parsing (simplified)
            # This is a basic implementation - Steam's VDF format is complex
            # For production use, consider using a VDF parsing library

            # Skip header ("shortcuts")
            offset = 0
            while offset < len(data):
                if data[offset : offset + 10] == b"shortcuts\x00":
                    offset += 10
                    break
                offset += 1

            # Parse shortcuts
            index = 0
            while offset < len(data) - 1:
                if data[offset] == 0x00:  # Section start
                    offset += 1
                    # Read section index
                    if offset >= len(data):
                        break

                    shortcut = {"index": index}
                    index += 1

                    # Parse key-value pairs
                    while offset < len(data) - 1:
                        type_byte = data[offset]

                        if type_byte == 0x08:  # End of section
                            offset += 1
                            break
                        elif type_byte == 0x01:  # String value
                            offset += 1
                            # Read key
                            key_end = data.find(b"\x00", offset)
                            if key_end == -1:
                                break
                            key = data[offset:key_end].decode("utf-8", errors="ignore")
                            offset = key_end + 1

                            # Read value
                            value_end = data.find(b"\x00", offset)
                            if value_end == -1:
                                break
                            value = data[offset:value_end].decode(
                                "utf-8", errors="ignore"
                            )
                            offset = value_end + 1

                            shortcut[key] = value
                        elif type_byte == 0x02:  # Integer value
                            offset += 1
                            # Read key
                            key_end = data.find(b"\x00", offset)
                            if key_end == -1:
                                break
                            key = data[offset:key_end].decode("utf-8", errors="ignore")
                            offset = key_end + 1

                            # Read 4-byte integer
                            if offset + 4 > len(data):
                                break
                            value = struct.unpack("<I", data[offset : offset + 4])[0]
                            offset += 4

                            shortcut[key] = value
                        else:
                            offset += 1

                    shortcuts.append(shortcut)
                elif data[offset] == 0x08:  # End of shortcuts
                    break
                else:
                    offset += 1

        except Exception as e:
            print(f"Error reading VDF shortcuts: {e}")

        return shortcuts

    @staticmethod
    def write_vdf_shortcuts(vdf_path: str, shortcuts: List[Dict]) -> Tuple[bool, str]:
        """
        Write shortcuts to VDF file

        Args:
            vdf_path: Path to shortcuts.vdf file
            shortcuts: List of shortcut dictionaries

        Returns:
            (success, message)
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(vdf_path), exist_ok=True)

            # Build VDF binary data
            data = bytearray()

            # Header
            data.extend(b"\x00shortcuts\x00")

            # Write shortcuts
            for idx, shortcut in enumerate(shortcuts):
                # Section start
                data.extend(b"\x00")
                data.extend(str(idx).encode("utf-8"))
                data.extend(b"\x00")

                # Write key-value pairs
                for key, value in shortcut.items():
                    if key == "index":
                        continue

                    if isinstance(value, str):
                        # String value
                        data.extend(b"\x01")
                        data.extend(key.encode("utf-8"))
                        data.extend(b"\x00")
                        data.extend(value.encode("utf-8"))
                        data.extend(b"\x00")
                    elif isinstance(value, int):
                        # Integer value
                        data.extend(b"\x02")
                        data.extend(key.encode("utf-8"))
                        data.extend(b"\x00")
                        data.extend(struct.pack("<I", value))

                # Section end
                data.extend(b"\x08")

            # File end markers
            data.extend(b"\x08\x08")

            # Write to file
            with open(vdf_path, "wb") as f:
                f.write(data)

            return True, "SUCCESS: Shortcuts saved"

        except Exception as e:
            return False, f"ERROR: Failed to write shortcuts: {e}"

    @staticmethod
    def add_non_steam_game(
        exe_path: str,
        app_name: str,
        launch_options: str = "",
        start_dir: Optional[str] = None,
    ) -> Tuple[bool, str]:
        """
        Add a non-Steam game to Steam library

        Args:
            exe_path: Full path to game executable
            app_name: Game name to display in Steam
            launch_options: Launch options (e.g., locale settings)
            start_dir: Starting directory (defaults to exe directory)

        Returns:
            (success, message)
        """
        try:
            debug_log(f"Adding non-Steam game: {app_name}")
            debug_log(f"Executable path: {exe_path}")

            # Validate exe exists
            if not os.path.exists(exe_path):
                return False, f"ERROR: Executable not found: {exe_path}"

            # Get Steam user directories
            debug_log("Getting Steam user directories...")
            user_dirs = SteamManager.get_steam_userdata_dirs()
            debug_log(f"User directories found: {user_dirs}")

            if not user_dirs:
                return False, "ERROR: No Steam user directories found"

            # Use the first user directory
            # In the future, we could let the user choose if multiple exist
            user_dir = user_dirs[0]
            vdf_path = SteamManager.get_shortcuts_vdf_path(user_dir)

            # Read existing shortcuts
            shortcuts = SteamManager.read_vdf_shortcuts(vdf_path)

            # Check if game already exists
            for shortcut in shortcuts:
                if (
                    shortcut.get("appname") == app_name
                    or shortcut.get("exe") == f'"{exe_path}"'
                ):
                    return (
                        False,
                        f"ERROR: Game '{app_name}' already exists in Steam library",
                    )

            # Set start directory
            if start_dir is None:
                start_dir = os.path.dirname(exe_path)

            # Create new shortcut
            new_shortcut = {
                "appname": app_name,
                "exe": f'"{exe_path}"',
                "StartDir": f'"{start_dir}"',
                "icon": "",
                "ShortcutPath": "",
                "LaunchOptions": launch_options,
                "IsHidden": 0,
                "AllowDesktopConfig": 1,
                "AllowOverlay": 1,
                "OpenVR": 0,
                "Devkit": 0,
                "DevkitGameID": "",
                "LastPlayTime": 0,
                "tags": {},
            }

            # Add to shortcuts list
            shortcuts.append(new_shortcut)

            # Write back to VDF
            success, msg = SteamManager.write_vdf_shortcuts(vdf_path, shortcuts)

            if success:
                return True, f"SUCCESS: Added '{app_name}' to Steam library"
            else:
                return False, msg

        except Exception as e:
            return False, f"ERROR: Exception occurred: {e}"
