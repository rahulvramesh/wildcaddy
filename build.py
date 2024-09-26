import PyInstaller.__main__
import os

# Get the absolute path to the project root
project_root = os.path.abspath(os.path.dirname(__file__))

# Define the path to your main script
main_script = os.path.join(project_root, 'proxy_manager.py')

# Define the path to your icon file
icon_file = os.path.join(project_root, 'resources', 'wild_caddy_icon.icns')

# Run PyInstaller
PyInstaller.__main__.run([
    '--clean',
    '--log-level=DEBUG',
    main_script,
    '--name=WildCaddy',
    '--onefile',
    '--windowed',
    '--add-data=%s:resources' % os.path.join(project_root, 'resources'),
    '--icon=%s' % icon_file,
    '--collect-all=PyQt6',
    '--hidden-import=PyQt6.QtCore',
    '--hidden-import=PyQt6.QtGui',
    '--hidden-import=PyQt6.QtWidgets',
    ])
