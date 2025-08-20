# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['eve_log_reader.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('google_form_config.json', '.'),
        ('version_info_enhanced.txt', '.'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib', 'numpy', 'pandas', 'scipy', 'PIL', 'cv2',
        'tkinter.test', 'test', 'unittest', 'doctest',
        'pydoc', 'pdb', 'profile', 'cProfile', 'trace',
        'distutils', 'setuptools', 'pip', 'wheel',
        'IPython', 'jupyter', 'notebook',
        'sphinx', 'docutils', 'jinja2',
        'flask', 'django', 'fastapi',
        'sqlalchemy', 'sqlite3', 'psycopg2',
        'requests.packages.urllib3.contrib.pyopenssl',
        'requests.packages.urllib3.contrib.socks',
        'requests.packages.urllib3.packages.ssl_match_hostname',
        'requests.packages.urllib3.packages.rfc3986',
        'requests.packages.urllib3.packages.ordered_dict',
        'requests.packages.urllib3.packages.ssl_match_hostname',
        'requests.packages.urllib3.packages.rfc3986',
        'requests.packages.urllib3.packages.ordered_dict',
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
    name='EVE_Log_Reader_Enhanced',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version_file='version_info_enhanced.txt',
    icon=None,
)
