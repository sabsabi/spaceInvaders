import os
from PIL import Image

def remove_icc_profile(image_path):
    try:
        with Image.open(image_path) as img:
            # Re-save the image without the ICC profile
            img.save(image_path, icc_profile=None)
        print(f"Processed {image_path}")
    except Exception as e:
        print(f"Error processing {image_path}: {e}")

def process_sprites_folder(folder_path):
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".png"):
            image_path = os.path.join(folder_path, filename)
            remove_icc_profile(image_path)

if __name__ == '__main__':
    sprites_folder = 'sprites'
    if os.path.exists(sprites_folder) and os.path.isdir(sprites_folder):
        process_sprites_folder(sprites_folder)
    else:
        print(f"Folder '{sprites_folder}' not found.")