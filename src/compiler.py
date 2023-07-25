import PyInstaller.__main__
from sys import platform

if platform == "linux" or platform == "linux2":
    # linux
    print()
elif platform == "darwin":
    # OS X
    PyInstaller.__main__.run([
        "src/main.py",
        '--onefile',
        "--add-data=private_key.json:/",
        '--add-data=manulife.icns:/',
        '--windowed',
        '--icon=img/manulife.icns',
        '--name=Seen',
        '--osx-bundle-identifier=Seen',
        '--clean',
        '-y'

    ])

elif platform == "win32":
    # Windows...
    PyInstaller.__main__.run([
        "src/main.py",
        '--onefile',
        "--add-data=private_key.json;\\",
        "--add-data=img\\manulife.ico;\\img",
        '--windowed',
        '--icon=img\\manulife.ico',
        '--name=Seen',
        '--clean',
        '-y'

    ])
