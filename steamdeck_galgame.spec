# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for SteamDeck Galgame Chinese Configuration Tool
# This creates a standalone executable with all dependencies bundled
# 
# Usage: 
#   pyinstaller --clean steamdeck_galgame.spec
#   BUILD_TYPE=debug pyinstaller --clean steamdeck_galgame.spec
#   BUILD_TYPE=release pyinstaller --clean steamdeck_galgame.spec

import sys
import os
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# Determine build type from environment variable
build_type = os.environ.get('BUILD_TYPE', 'release').lower()
exe_name = 'steamdeck-galgame-debug' if build_type == 'debug' else 'steamdeck-galgame-release'

block_cipher = None

datas = []

# Collect requests data files
datas += collect_data_files('requests')

# Collect customtkinter data files (themes, assets, etc.)
datas += collect_data_files('customtkinter')

a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'src',
        'src.gui',
        'src.gui.main',
        'src.core',
        'src.core.downloader',
        'src.core.installers',
        'src.utils',
        'src.config',
        'requests',
        'customtkinter',
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.filedialog',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludedimports=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name=exe_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI mode, no console window
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
