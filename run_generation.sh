#!/bin/bash
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

