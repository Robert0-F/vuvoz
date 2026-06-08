"""Image processing for uploaded material icons and photos."""

from __future__ import annotations

import io
import os
from uuid import uuid4

from django.core.files.base import ContentFile
from PIL import Image, ImageOps

MATERIAL_ICON_SIZE = 96
MATERIAL_PHOTO_MAX_EDGE = 1200


def _unique_name(prefix: str, ext: str) -> str:
    return f'{prefix}_{uuid4().hex[:12]}{ext}'


def process_material_icon(uploaded_file) -> ContentFile:
    """Resize icon to a fixed square PNG (transparent background)."""
    img = Image.open(uploaded_file)
    img = ImageOps.exif_transpose(img)
    if img.mode not in ('RGB', 'RGBA'):
        img = img.convert('RGBA')
    elif img.mode == 'RGB':
        img = img.convert('RGBA')

    img.thumbnail((MATERIAL_ICON_SIZE, MATERIAL_ICON_SIZE), Image.Resampling.LANCZOS)
    canvas = Image.new('RGBA', (MATERIAL_ICON_SIZE, MATERIAL_ICON_SIZE), (0, 0, 0, 0))
    offset = (
        (MATERIAL_ICON_SIZE - img.width) // 2,
        (MATERIAL_ICON_SIZE - img.height) // 2,
    )
    canvas.paste(img, offset, img if img.mode == 'RGBA' else None)

    buffer = io.BytesIO()
    canvas.save(buffer, format='PNG', optimize=True)
    return ContentFile(buffer.getvalue(), name=_unique_name('icon', '.png'))


def process_material_photo(uploaded_file) -> ContentFile:
    """Resize photo to fit within max edge, keep aspect ratio."""
    img = Image.open(uploaded_file)
    img = ImageOps.exif_transpose(img)
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')

    img.thumbnail((MATERIAL_PHOTO_MAX_EDGE, MATERIAL_PHOTO_MAX_EDGE), Image.Resampling.LANCZOS)

    ext = os.path.splitext(getattr(uploaded_file, 'name', '') or '')[1].lower()
    if ext in ('.png',):
        fmt, save_ext = 'PNG', '.png'
    elif ext in ('.webp',):
        fmt, save_ext = 'WEBP', '.webp'
    else:
        fmt, save_ext = 'JPEG', '.jpg'

    buffer = io.BytesIO()
    save_kwargs = {'optimize': True}
    if fmt == 'JPEG':
        save_kwargs['quality'] = 88
    img.save(buffer, format=fmt, **save_kwargs)
    return ContentFile(buffer.getvalue(), name=_unique_name('photo', save_ext))
