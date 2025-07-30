#!/bin/bash

# Define folder name venv
VENV_DIR=".venv"

# Create venv if not exist
if [ ! -d "$VENV_DIR" ]; then
    echo "🔧 Virtual environment creation..."
    python3 -m venv "$VENV_DIR"
fi

# Enable venv
echo "✅ Enabling virtual environment..."
source "$VENV_DIR/bin/activate"

# Install dependencies
echo "📦 Installing Dependency..."
pip install -r requirements.txt

echo "✅ Environemnt Ready. VENV enabled."
