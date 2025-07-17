# PyInstaller spec file for mdsplit4gpt

import os
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Get version
try:
    from setuptools_scm import get_version
    version = get_version()
except:
    version = "0.0.0"

block_cipher = None

a = Analysis(
    ['src/split_python4gpt/__main__.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'split_python4gpt',
        'split_python4gpt.minifier',
        'fire',
        'tiktoken',
        'python_minifier',
        'simpleaichat',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'pytype',  # Exclude pytype to reduce binary size
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
        'jupyter',
        'IPython',
    ],
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
    name='mdsplit4gpt',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version=version,
)