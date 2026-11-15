#!/bin/bash
# mukta Packaging Script

echo "Installing dependencies..."
# Ensure dependencies are installed in the current uv environment
uv pip install pyinstaller matplotlib

echo "Packaging mukta into a standalone executable..."
# --windowed removes the console window
# --onefile packages everything into a single binary
# --name sets the binary name
uv run python -m PyInstaller --name mukta --windowed --onefile main.py

echo "Build complete!"
echo "Your standalone Linux application is located at: ./dist/mukta"
echo "You can move this file anywhere on your system or distribute it to other Linux users without them needing Python!"
rm  ~/.local/share/applications/mukta.desktop
cp mukta.desktop ~/.local/share/applications/