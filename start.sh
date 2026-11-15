#!/bin/bash
# Start MuktaSlate application
cd "$(dirname "$0")"

# Check if uv is available
if ! command -v uv &> /dev/null; then
    echo "Error: 'uv' is not installed or not in PATH."
    echo "Please install uv: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi
rm -f .venv/.lock
# sudo apt update && sudo apt install -y libxcb-cursor0
# 
# Run the app
echo "Starting mukta - infinite canvas board..."
export LC_ALL=C
uv run main.py


