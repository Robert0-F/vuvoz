# Migration: Material model; PriceList and RequestMaterialLine reference Material.
# CollectionRequest.material_type becomes free-form code (max_length=32).

from django.db import migrations, models


DEFAULT_MATERIALS = [
    ('Картон', 'cardboard'),
    ('Макулатура', 'paper'),
    ('Канистры/флаконы', 'canisters'),
    ('Полиэтилен/стрейч пленка', 'polyethylene'),
    ('Металл бытовой', 'metal'),
    ('Стекло (бутылки)', 'glass'),
]


def create_materials_and_backfill(apps, schema_editor):
    Material = apps.get_model('collection', 'Material')
    PriceList = apps.get_model('collection', 'PriceList')
    RequestMaterialLine = apps.get_model('collection', 'RequestMaterialLine')

    code_to_material = {}
    for name, code in DEFAULT_MATERIALS:
        m, _ = Material.objects.get_or_create(code=code, defaults={'name': name, 'is_active': True})
        code_to_material[code] = m

    for pl in PriceList.objects.all():
        mat = code_to_material.get(pl.material_type)
        if mat:
            pl.material = mat
            pl.save(update_fields=['material'])

    for rml in RequestMaterialLine.objects.all():
        mat = code_to_material.get(rml.material_type)
        if mat:
            rml.material = mat
            rml.save(update_fields=['material'])


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('collection', '0014_material_types_and_pricelist_unique'),
    ]

    operations = [
        migrations.CreateModel(
            name='Material',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
                ('code', models.CharField(max_length=32, unique=True)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'Material',
                'verbose_name_plural': 'Materials',
            },
        ),
        migrations.AlterField(
            model_name='collectionrequest',
            name='material_type',
            field=models.CharField(
                default='paper',
                help_text='Material code (e.g. paper, cardboard). Set from first line when request has material_lines.',
                max_length=32,
            ),
        ),
        migrations.AddField(
            model_name='pricelist',
            name='material',
            field=models.ForeignKey(
                null=True,
                on_delete=models.CASCADE,
                related_name='prices',
                to='collection.material',
                unique=True,
            ),
        ),
        migrations.AddField(
            model_name='requestmaterialline',
            name='material',
            field=models.ForeignKey(
                null=True,
                on_delete=models.PROTECT,
                related_name='request_lines',
                to='collection.material',
            ),
        ),
        migrations.RunPython(create_materials_and_backfill, noop),
        migrations.RemoveField(
            model_name='pricelist',
            name='material_type',
        ),
        migrations.AlterField(
            model_name='pricelist',
            name='material',
            field=models.ForeignKey(
                on_delete=models.CASCADE,
                related_name='prices',
                to='collection.material',
                unique=True,
            ),
        ),
        migrations.RemoveField(
            model_name='requestmaterialline',
            name='material_type',
        ),
        migrations.AlterField(
            model_name='requestmaterialline',
            name='material',
            field=models.ForeignKey(
                on_delete=models.PROTECT,
                related_name='request_lines',
                to='collection.material',
            ),
        ),
    ]
