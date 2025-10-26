import os
import pathlib
import time

if __name__ == "__main__":
    os.chdir(pathlib.Path(__file__).parent)
    image_path = (
        pathlib.Path(__file__).parent / "images" / "current" / "generated_image.png"
    )
    # move the image to images/archive with a timestamp
    archive_dir = pathlib.Path(__file__).parent / "images" / "archive"
    archive_dir.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    if image_path.exists():
        new_image_path = archive_dir / f"generated_image_{timestamp}.png"
        image_path.rename(new_image_path)
