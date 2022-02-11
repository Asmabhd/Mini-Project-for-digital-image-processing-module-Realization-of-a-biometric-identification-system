# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['IRIS_Applicatio.py'],
             pathex=['C:\\Users\\pc\\Downloads\\Projet_Tin_Groupe_11__Allouche_Kenza_Oubara_Mouna_Bouhadadou_Asma\\Projet_Tin_Groupe_11__Allouche_Kenza_Oubara_Mouna_Bouhadadou_Asma'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='IRIS_Applicatio',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='IRIS_Applicatio')
