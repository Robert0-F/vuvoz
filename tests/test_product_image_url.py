"""Product image_url should be a same-origin relative path for SPA clients."""
from django.core.files.base import ContentFile
from rest_framework.test import APIRequestFactory

from collection.models import Product
from collection.serializers import ProductSerializer

PNG_BYTES = (
    b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
    b'\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82'
)


def test_product_image_url_is_relative_media_path(db):
    product = Product.objects.create(name='Test product', price_in_points=10)
    product.image.save('test.png', ContentFile(PNG_BYTES), save=True)

    data = ProductSerializer(product).data
    assert data['image_url'].startswith('/media/')
    assert '127.0.0.1' not in (data['image_url'] or '')
    assert 'image' not in data

    factory = APIRequestFactory()
    request = factory.get('/api/products/')
    data_with_request = ProductSerializer(product, context={'request': request}).data
    assert data_with_request['image_url'] == data['image_url']
