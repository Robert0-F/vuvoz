#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Create media/products/ if missing, add a small test image, and attach it to the first
bonus product so product photos display in the institution UI.
Run from project root with the project venv activated:
  python scripts/attach_test_product_image.py
Requires: create_bonus_products.py to have been run so at least one product exists.
"""
import os
import sys

_script_dir = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(_script_dir)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vuvoz.settings')

import django
django.setup()

from pathlib import Path
from django.conf import settings
from django.core.files.base import ContentFile
from collection.models import Product

# Minimal 1x1 PNG (valid image bytes)
PNG_BYTES = (
    b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
    b'\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82'
)


def run():
    media_root = Path(settings.MEDIA_ROOT)
    products_dir = media_root / 'products'
    products_dir.mkdir(parents=True, exist_ok=True)
    print(f"Media dir: {media_root} (products: {products_dir})")

    product = Product.objects.filter(is_active=True).order_by('name').first()
    if not product:
        print("No active product found. Run scripts/create_bonus_products.py first.")
        return

    # Save a test image via the model so it goes to media/products/ and DB is updated
    filename = f"test_{product.id}.png"
    product.image.save(filename, ContentFile(PNG_BYTES), save=True)
    print(f"Attached image to product: {product.name} (id={product.id})")
    print(f"  File: {product.image.path}")
    print(f"  URL:  {product.image.url}")
    assert product.image.path and Path(product.image.path).exists(), "File should exist on disk"
    print("Done. Reload the institution page to see the photo.")


if __name__ == '__main__':
    run()
