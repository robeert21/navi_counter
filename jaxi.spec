# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ["gui.py"],
    pathex=[],
    binaries=[],
    datas=[
        ("overlay", "overlay"),
    ],
    hiddenimports=[
        "websockets",
        "websockets.server",
        "websockets.client",
        "websockets.legacy",
        "websockets.legacy.server",
        "websockets.legacy.client",
        "websockets.asyncio",
        "websockets.asyncio.server",
        "google.api_core",
        "google.auth",
        "google.auth.transport",
        "google.auth.transport.requests",
        "google.oauth2",
        "googleapiclient",
        "googleapiclient.discovery",
        "googleapiclient.http",
        "httplib2",
        "uritemplate",
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
