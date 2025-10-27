#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to that directory
cd "$SCRIPT_DIR" || exit 1

# Add common locations for uv to PATH
export PATH="$HOME/.cargo/bin:$HOME/.local/bin:/usr/local/bin:$PATH"
PYTHON=$(uv python find)

$PYTHON ./main.py
$PYTHON ./image_upload.py

