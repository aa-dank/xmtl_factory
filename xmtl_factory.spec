# -*- mode: python ; coding: utf-8 -*-
#
# PyInstaller spec for xmtl-factory
#
# Before building, place the wkhtmltopdf binary in the project root:
#   Windows : download wkhtmltopdf.exe from https://wkhtmltopdf.org/downloads.html
#   macOS   : brew install wkhtmltopdf  then cp $(which wkhtmltopdf) .
#
# Build (run on each target platform separately):
#   pyinstaller xmtl_factory.spec
#
# Output is placed in dist/xmtl-factory(.exe).

import sys
from pathlib import Path

block_cipher = None

# ------------------------------------------------------------------
# Detect & bundle the wkhtmltopdf binary if present in the project root
# ------------------------------------------------------------------
_binary_name = 'wkhtmltopdf.exe' if sys.platform == 'win32' else 'wkhtmltopdf'
_binary_path = Path(_binary_name)
binaries = [(str(_binary_path), '.')] if _binary_path.exists() else []

# ------------------------------------------------------------------
# Analysis
# ------------------------------------------------------------------
a = Analysis(
    ['submittal_cli.py'],
    pathex=[],
    binaries=binaries,
    datas=[
        ('templates',          'templates'),      # Jinja2 HTML templates
        ('images',             'images'),          # logo / header images
        ('styles.css',         '.'),               # CSS used by all pages
        ('xmtl_templates.yaml', '.'),              # project template data
    ],
    hiddenimports=[
        'dateutil',
        'dateutil.parser',
        'pkg_resources.extern',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['xhtml2pdf'],
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
    name='xmtl-factory',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
