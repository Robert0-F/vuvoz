# Material icon image + separate storage paths for icons and photos

import collection.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('collection', '0022_pickup_lines_company_registration'),
    ]

    operations = [
        migrations.AddField(
            model_name='material',
            name='icon_image',
            field=models.ImageField(
                blank=True,
                help_text='Square icon for homepage and calculator (stored as 96×96 PNG).',
                null=True,
                upload_to=collection.models.material_icon_upload_to,
            ),
        ),
        migrations.AlterField(
            model_name='material',
            name='icon',
            field=models.CharField(
                blank=True,
                help_text='MDI icon fallback when no icon image is uploaded, e.g. package-variant',
                max_length=64,
            ),
        ),
        migrations.AlterField(
            model_name='material',
            name='image',
            field=models.ImageField(
                blank=True,
                help_text='Photo for the materials catalog page.',
                null=True,
                upload_to=collection.models.material_photo_upload_to,
            ),
        ),
    ]
