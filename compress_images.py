import os
from PIL import Image

def compress_image(file_path):
    try:
        size = os.path.getsize(file_path)
        if size > 500 * 1024:  # > 500KB
            print(f"Compressing {file_path} (Current size: {size / 1024 / 1024:.2f} MB)")
            img = Image.open(file_path)
            
            # Convert RGBA to RGB if needed
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            
            # Resize if very large
            max_width = 1280
            if img.width > max_width:
                ratio = max_width / img.width
                new_height = int(img.height * ratio)
                try:
                    resample_filter = Image.Resampling.LANCZOS
                except AttributeError:
                    resample_filter = getattr(Image, 'LANCZOS', getattr(Image, 'ANTIALIAS'))
                img = img.resize((max_width, new_height), resample_filter)
                
            img.save(file_path, optimize=True, quality=75)
            new_size = os.path.getsize(file_path)
            print(f"Done! New size: {new_size / 1024 / 1024:.2f} MB")
    except Exception as e:
        print(f"Error compressing {file_path}: {e}")

dirs_to_check = [
    "/home/chillop/project/asamang/Asamang-website/static/assets/img/health",
    "/home/chillop/project/asamang/Asamang-website/media/doctors",
    "/home/chillop/project/asamang/Asamang-website/static/assets/img/clients",
    "/home/chillop/project/asamang/Asamang-website/static/assets/img/gallery",
    "/home/chillop/project/asamang/Asamang-website/static/assets/img/person"
]

for d in dirs_to_check:
    if os.path.exists(d):
        for filename in os.listdir(d):
            if filename.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                compress_image(os.path.join(d, filename))
