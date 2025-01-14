# pyinstaller_build.spec
# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path
import sys
import site

block_cipher = None

# Obtener el path absoluto del proyecto
PROJ_PATH = str(Path('.').absolute())

# Obtener el path del entorno virtual
if hasattr(sys, 'real_prefix'):
    # Para virtualenv
    VENV_PATH = sys.prefix
elif sys.base_prefix != sys.prefix:
    # Para venv
    VENV_PATH = sys.prefix
else:
    VENV_PATH = ''

# Obtener el path de los site-packages
if VENV_PATH:
    if sys.platform == 'win32':
        SITE_PACKAGES = Path(VENV_PATH) / 'Lib' / 'site-packages'
    else:
        SITE_PACKAGES = Path(VENV_PATH) / 'lib' / f'python{sys.version_info.major}.{sys.version_info.minor}' / 'site-packages'
else:
    SITE_PACKAGES = site.getsitepackages()[0]


a = Analysis(
    ['main.py'],
    pathex=[PROJ_PATH,
    str(SITE_PACKAGES),
    ], 
    binaries=[],
    datas=[
        ('gym/templates', 'gym/templates'),
        ('static', 'static'),
        ('templates', 'templates'),
        ('.env', '.'),  # Incluir archivo de variables de entorno
        ('db.sqlite3', '.'),  # Incluir base de datos si usas SQLite
        (str(Path(VENV_PATH) / 'Lib' / 'site-packages' / 'django'), 'django'),
    ],
    hiddenimports=[
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'corsheaders',
        'crispy_forms',
        'crispy_bootstrap4',
        'simple_history',
        'django_filters',
        'core',
        'core.settings',
        'core.urls',
        'core.wsgi',
        'gym',
        'gym.urls',
    ],
    hookspath=['.'],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher
)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='stefy_gym',
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
    entitlements_file=None
)