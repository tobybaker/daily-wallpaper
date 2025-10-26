uv run move_images.py
uv run main.py
git add images/archive/*.png
git add images/current/generated_image.png

git commit -m "Daily wallpaper update"
git push origin main