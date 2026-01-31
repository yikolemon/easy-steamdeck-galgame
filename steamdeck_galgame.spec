# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for SteamDeck Galgame Chinese Configuration Tool
# This creates a standalone executable with all dependencies bundled

import sys
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

block_cipher = None

datas = []

# Collect requests data files (if needed)
datas += collect_data_files('requests')

a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'src',
        'src.tui',
        'src.core',
        'src.core.downloader',
        'src.core.installers',
        'src.utils',
        'requests',
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
    [],
    exclude_binaries=True,
    name='steamdeck-galgame',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='steamdeck-galgame',
)
