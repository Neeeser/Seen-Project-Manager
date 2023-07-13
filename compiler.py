import PyInstaller.__main__
from sys import platform

if platform == "linux" or platform == "linux2":
    # linux
    print()
elif platform == "darwin":
    # OS X
    PyInstaller.__main__.run([
        "Gui.py",
        '--onefile',
        "--add-data=seenworkflow_private_key.json:/",
        '--add-data=manulife.icns:/',
        '--windowed',
        '--icon=manulife.icns',
        '--name=Seen',
        '--osx-bundle-identifier=Seen',
        '-y'

    ])

elif platform == "win32":
    # Windows...
    PyInstaller.__main__.run([
        "Gui.py",
        '--onefile',
        "--add-data=seenworkflow_private_key.json;\\",
        "--add-data=manulife.ico;\\",
        '--windowed',
        '--icon=manulife.ico',
        '--name=Seen',
        '-y'

    ])
