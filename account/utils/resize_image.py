from io import BytesIO
from django.core.files.base import ContentFile
from PIL import Image


def resize_image(file, filename, width, height):
    image = Image.open(file)

    if image.size[0] > width or image.size[1] > height:
        new_img = image.resize((width, height))
        buffer = BytesIO()
        new_img.save(fp=buffer, format='JPEG', quality=85, optimize=True)
        return ContentFile(buffer.getvalue(), name=filename)

    return file