#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to that directory
cd "$SCRIPT_DIR" || exit 1

# Add common locations for uv to PATH
export PATH="$HOME/.cargo/bin:$HOME/.local/bin:/usr/local/bin:$PATH"
PYTHON=$(uv python find)
#sync with origin main
git checkout main
git pull origin main

$PYTHON ./move_images.py
$PYTHON ./main.py
git add images/archive/*.png
git add images/current/generated_image.png

git commit -m "Daily wallpaper update"
git push origin main

