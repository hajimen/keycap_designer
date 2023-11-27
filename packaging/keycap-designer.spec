# -*- mode: python ; coding: utf-8 -*-

datas = [
    ('../keycap_designer/area/xda/*', 'keycap_designer/area/xda/'),
    ('../keycap_designer/area/junana/*', 'keycap_designer/area/junana/'),
    ('../keycap_designer/icc/*', 'keycap_designer/icc/'),
    ('../keycap_designer/font/*', 'keycap_designer/font/'),
    ('../keycap_designer/deform/__init__.py', 'keycap_designer/deform/'),
    ('../keycap_designer/deform/junana/*', 'keycap_designer/deform/junana/'),
    ('../keycap_designer/*.py', 'keycap_designer/'),
]


a = Analysis(
    ['../keycap_designer/__main__.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    noarchive=False,
    module_collection_mode={'ordered_enum': 'py+pyz'},
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='keycap-designer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='keycap-designer',
)
