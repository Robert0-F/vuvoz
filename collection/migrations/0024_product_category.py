from django.db import migrations, models
import django.db.models.deletion


def seed_categories(apps, schema_editor):
    ProductCategory = apps.get_model('collection', 'ProductCategory')
    Product = apps.get_model('collection', 'Product')
    defaults = [
        ('office', 'Канцелярия', 10),
        ('eco', 'Эко-товары', 20),
        ('merch', 'Сувениры', 30),
        ('other', 'Прочее', 100),
    ]
    slug_map = {}
    for slug, name, order in defaults:
        cat, _ = ProductCategory.objects.get_or_create(
            slug=slug,
            defaults={'name': name, 'sort_order': order, 'is_active': True},
        )
        slug_map[slug] = cat
    other = slug_map['other']
    Product.objects.filter(category__isnull=True).update(category=other)


class Migration(migrations.Migration):

    dependencies = [
        ('collection', '0023_material_icon_image_paths'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120)),
                ('slug', models.SlugField(max_length=120, unique=True)),
                ('sort_order', models.PositiveIntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Категория товаров (баллы)',
                'verbose_name_plural': 'Категории товаров (баллы)',
                'ordering': ['sort_order', 'name'],
            },
        ),
        migrations.AddField(
            model_name='product',
            name='category',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='products',
                to='collection.productcategory',
            ),
        ),
        migrations.RunPython(seed_categories, migrations.RunPython.noop),
    ]
