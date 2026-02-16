# Points (green points), products, orders

from decimal import Decimal
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def backfill_bonus_balance(apps, schema_editor):
    """Set institution.bonus_balance = sum of their confirmed bonuses."""
    InstitutionProfile = apps.get_model('collection', 'InstitutionProfile')
    InstitutionBonus = apps.get_model('collection', 'InstitutionBonus')
    for inst in InstitutionProfile.objects.all():
        total = Decimal('0')
        for b in InstitutionBonus.objects.filter(institution=inst, status='confirmed'):
            total += (b.awarded_amount or b.calculated_amount or Decimal('0'))
        inst.bonus_balance = total
        inst.save(update_fields=['bonus_balance'])


def create_test_product(apps, schema_editor):
    Product = apps.get_model('collection', 'Product')
    Product.objects.get_or_create(
        id=1,
        defaults={
            'name': 'Набор канцтоваров и инструментов',
            'description': (
                'Набор для школы и офиса: ручки шариковые (5 шт.), тетради 48 листов (10 шт.), '
                'карандаши (5 шт.), ластики (2 шт.), линейка, ножницы, степлер, скрепки, клей-карандаш, '
                'несколько отвёрток и пассатижи.'
            ),
            'price_in_points': Decimal('150'),
            'is_active': True,
        },
    )


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('collection', '0008_bonus_system'),
    ]

    operations = [
        migrations.AddField(
            model_name='institutionprofile',
            name='bonus_balance',
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                help_text='Баланс зелёных баллов (начисления минус траты)',
                max_digits=12,
            ),
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('price_in_points', models.DecimalField(decimal_places=2, default=0, help_text='Цена в зелёных баллах', max_digits=10)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Товар (баллы)',
                'verbose_name_plural': 'Товары (баллы)',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='PointsOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('pending', 'Ожидает'), ('completed', 'Выполнен'), ('cancelled', 'Отменён')], default='pending', max_length=20)),
                ('recipient_name', models.CharField(max_length=255)),
                ('recipient_phone', models.CharField(max_length=50)),
                ('address', models.TextField()),
                ('total_points', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('institution', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='points_orders', to='collection.institutionprofile')),
            ],
            options={
                'verbose_name': 'Заказ на баллы',
                'verbose_name_plural': 'Заказы на баллы',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='PointsOrderLine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('price_at_order', models.DecimalField(decimal_places=2, default=0, help_text='Цена за единицу в баллах на момент заказа', max_digits=10)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lines', to='collection.pointsorder')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='order_lines', to='collection.product')),
            ],
            options={
                'verbose_name': 'Строка заказа (баллы)',
                'verbose_name_plural': 'Строки заказов (баллы)',
            },
        ),
        migrations.RunPython(backfill_bonus_balance, migrations.RunPython.noop),
        migrations.RunPython(create_test_product, migrations.RunPython.noop),
    ]
