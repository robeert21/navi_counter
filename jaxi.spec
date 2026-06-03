# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_all

pytchat_datas, pytchat_binaries, pytchat_hiddenimports = collect_all("pytchat")

a = Analysis(
    ["gui.py"],
    pathex=[],
    binaries=pytchat_binaries,
    datas=[
        ("overlay", "overlay"),
        *pytchat_datas,
    ],
    hiddenimports=[
        *pytchat_hiddenimports,
        "websockets",
        "websockets.server",
        "websockets.client",
        "websockets.legacy",
        "websockets.legacy.server",
        "websockets.legacy.client",
        "websockets.asyncio",
        "websockets.asyncio.server",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="navi_counter",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
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
    name="navi_counter",
)
