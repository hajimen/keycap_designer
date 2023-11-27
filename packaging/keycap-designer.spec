# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = []
binaries = []
hiddenimports = []
tmp_ret = collect_all('cmm')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('frozendict')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]

datas += [
    ('../keycap_designer/area/xda/*', 'keycap_designer/area/xda/'),
    ('../keycap_designer/area/junana/*', 'keycap_designer/area/junana/'),
    ('../keycap_designer/icc/*', 'keycap_designer/icc/'),
    ('../keycap_designer/font/*', 'keycap_designer/font/'),
    ('../keycap_designer/deform/__init__.py', 'keycap_designer/deform/'),
    ('../keycap_designer/deform/junana/*', 'keycap_designer/deform/junana/'),
    ('../keycap_designer/*.py', 'keycap_designer/'),
]


block_cipher = None


a = Analysis(
    ['../keycap_designer/__main__.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=True,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
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
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='keycap-designer',
)
