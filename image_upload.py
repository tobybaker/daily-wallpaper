import os
import cloudinary
import cloudinary.uploader
from datetime import datetime


if __name__ == "__main__":
    cloudinary.config(
        cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
        api_key=os.environ.get('CLOUDINARY_API_KEY'),
        api_secret=os.environ.get('CLOUDINARY_API_SECRET')
    )

    # Upload the image
    try:
        result = cloudinary.uploader.upload(
            "images/current/daily_generated_wallpaper.png",  # Change this to your image path
            public_id="hourly-wallpaper",   # Keeps URL consistent
            overwrite=True,              # Replaces existing image
            invalidate=True,             # Clears CDN cache immediately
            resource_type="image"        # Explicitly set as image
        )
        
        print(f"✓ Upload successful at {datetime.now()}")
        print(f"URL: {result['secure_url']}")
        
    except Exception as e:
        print(f"✗ Upload failed: {e}")
        exit(1)