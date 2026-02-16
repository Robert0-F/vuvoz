# Product image, order status label

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('collection', '0009_points_products_orders'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='image',
            field=models.ImageField(blank=True, help_text='Фото товара', null=True, upload_to='products/'),
        ),
    ]
