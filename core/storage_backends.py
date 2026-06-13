import os
import io
from PIL import Image
from cloudinary_storage.storage import MediaCloudinaryStorage
from django.core.files.base import ContentFile

class CompressedImageStorage(MediaCloudinaryStorage):
    def _save(self, name, content):
        ext = os.path.splitext(name)[1].lower()
        if ext in ['.jpg', '.jpeg', '.png', '.webp']:
            try:
                img = Image.open(content)
                
                if img.mode in ("RGBA", "P") and ext in ['.jpg', '.jpeg']:
                    img = img.convert("RGB")
                
                max_width = 1280
                if img.width > max_width:
                    ratio = max_width / img.width
                    new_height = int(img.height * ratio)
                    try:
                        resample_filter = Image.Resampling.LANCZOS
                    except AttributeError:
                        resample_filter = getattr(Image, 'LANCZOS', getattr(Image, 'ANTIALIAS'))
                    img = img.resize((max_width, new_height), resample_filter)
                
                img_io = io.BytesIO()
                img_format = 'JPEG' if ext in ['.jpg', '.jpeg'] else ext[1:].upper()
                
                if img_format == 'JPEG':
                    img.save(img_io, format=img_format, optimize=True, quality=75)
                else:
                    img.save(img_io, format=img_format, optimize=True)
                
                new_content = ContentFile(img_io.getvalue())
                return super()._save(name, new_content)
            except Exception as e:
                if hasattr(content, 'seek'):
                    content.seek(0)
                pass
                
        return super()._save(name, content)
