# Migration: new material types, unique material_type on PriceList, optional valid_from

from django.db import migrations, models


def migrate_material_types(apps, schema_editor):
    """Map old material_type values to new; keep one PriceList per material_type."""
    PriceList = apps.get_model('collection', 'PriceList')
    CollectionRequest = apps.get_model('collection', 'CollectionRequest')
    RequestMaterialLine = apps.get_model('collection', 'RequestMaterialLine')

    old_to_new = {
        'newspapers': 'paper',
        'mixed': 'paper',
        'archive': 'paper',
    }

    # Update CollectionRequest
    for old_val, new_val in old_to_new.items():
        CollectionRequest.objects.filter(material_type=old_val).update(material_type=new_val)

    # Update RequestMaterialLine
    for old_val, new_val in old_to_new.items():
        RequestMaterialLine.objects.filter(material_type=old_val).update(material_type=new_val)

    # PriceList: update old types then keep one row per material_type (delete duplicates)
    for old_val, new_val in old_to_new.items():
        PriceList.objects.filter(material_type=old_val).update(material_type=new_val)

    # Delete duplicate PriceList rows (keep lowest id per material_type)
    seen = set()
    for row in PriceList.objects.order_by('material_type', 'id'):
        if row.material_type in seen:
            row.delete()
        else:
            seen.add(row.material_type)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('collection', '0013_collectionrequest_cancelled_status'),
    ]

    operations = [
        migrations.RunPython(migrate_material_types, noop),
        migrations.AlterField(
            model_name='pricelist',
            name='material_type',
            field=models.CharField(
                choices=[
                    ('cardboard', 'Картон'),
                    ('paper', 'Макулатура'),
                    ('canisters', 'Канистры/флаконы'),
                    ('polyethylene', 'Полиэтилен/стрейч пленка'),
                    ('metal', 'Металл бытовой'),
                    ('glass', 'Стекло (бутылки)'),
                ],
                max_length=24,
                unique=True,
            ),
        ),
        migrations.AlterField(
            model_name='pricelist',
            name='valid_from',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='collectionrequest',
            name='material_type',
            field=models.CharField(
                choices=[
                    ('cardboard', 'Картон'),
                    ('paper', 'Макулатура'),
                    ('canisters', 'Канистры/флаконы'),
                    ('polyethylene', 'Полиэтилен/стрейч пленка'),
                    ('metal', 'Металл бытовой'),
                    ('glass', 'Стекло (бутылки)'),
                ],
                default='paper',
                max_length=24,
            ),
        ),
        migrations.AlterField(
            model_name='requestmaterialline',
            name='material_type',
            field=models.CharField(
                choices=[
                    ('cardboard', 'Картон'),
                    ('paper', 'Макулатура'),
                    ('canisters', 'Канистры/флаконы'),
                    ('polyethylene', 'Полиэтилен/стрейч пленка'),
                    ('metal', 'Металл бытовой'),
                    ('glass', 'Стекло (бутылки)'),
                ],
                max_length=24,
            ),
        ),
    ]
