# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Ntropy with embedded Tesseract OCR.

Para usar:
1. Certifique-se de que a pasta 'tesseract/' existe com os binários do Tesseract
2. Execute: pyinstaller ntropy.spec
"""

import os

block_cipher = None

# Caminho base do projeto
base_path = os.path.dirname(os.path.abspath(SPEC))

# Arquivos de dados a incluir
datas = []

# Incluir Tesseract se a pasta existir
tesseract_path = os.path.join(base_path, 'tesseract')
if os.path.exists(tesseract_path):
    # Incluir todos os arquivos do Tesseract
    datas.append((tesseract_path, 'tesseract'))
    print(f"[INFO] Tesseract encontrado em: {tesseract_path}")
else:
    print(f"[AVISO] Pasta 'tesseract/' não encontrada!")
    print(f"[AVISO] O executável NÃO terá Tesseract embutido.")
    print(f"[AVISO] Baixe o Tesseract portable e extraia para: {tesseract_path}")

a = Analysis(
    ['main.py'],
    pathex=[base_path],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'PIL._tkinter_finder',
        'pynput.keyboard._win32',
        'pynput.mouse._win32',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='Ntropy',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Sem janela de console (GUI app)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon='icon.ico',  # Descomente se tiver um ícone
)
