# -*- mode: python -*-

block_cipher = None


a = Analysis(['C:\\Dropbox\\Actual Documents\\PycharmProjects\\hisokocasino\\hisokocasino.py'],
             pathex=['C:\\Dropbox\\Actual Documents\\PycharmProjects\\hisokocasino'],
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
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='hisokocasino',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True , icon='C:\\Dropbox\\Actual Documents\\PycharmProjects\\hisokocasino\\hisoCate.ico')
