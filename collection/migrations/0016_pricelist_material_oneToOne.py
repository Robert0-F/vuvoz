# Change PriceList.material from ForeignKey(unique=True) to OneToOneField (same DB, fixes W342).

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('collection', '0015_material_model_and_fks'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pricelist',
            name='material',
            field=models.OneToOneField(
                on_delete=models.CASCADE,
                related_name='price',
                to='collection.material',
            ),
        ),
    ]
