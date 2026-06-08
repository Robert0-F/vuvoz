# Generated manually for multi-material pickup and company registration

from decimal import Decimal

from django.db import migrations, models
import django.db.models.deletion


def migrate_pickup_to_lines(apps, schema_editor):
    PublicPickupRequest = apps.get_model('collection', 'PublicPickupRequest')
    PublicPickupRequestLine = apps.get_model('collection', 'PublicPickupRequestLine')
    for req in PublicPickupRequest.objects.all():
        if not hasattr(req, 'material_id') or req.material_id is None:
            continue
        PublicPickupRequestLine.objects.create(
            request_id=req.pk,
            material_id=req.material_id,
            weight_kg=req.weight_kg,
            line_payout=req.estimated_payout or Decimal('0'),
        )


class Migration(migrations.Migration):

    dependencies = [
        ('collection', '0021_rename_collecti_institu_0fdca2_idx_collection__institu_0ba30f_idx_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='PublicPickupRequestLine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('weight_kg', models.DecimalField(decimal_places=2, max_digits=10)),
                ('line_payout', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('material', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='public_pickup_lines', to='collection.material')),
                ('request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lines', to='collection.publicpickuprequest')),
            ],
            options={
                'verbose_name': 'Строка заявки на вывоз',
                'verbose_name_plural': 'Строки заявок на вывоз',
                'ordering': ['id'],
            },
        ),
        migrations.AddConstraint(
            model_name='publicpickuprequestline',
            constraint=models.UniqueConstraint(fields=('request', 'material'), name='uniq_public_pickup_request_material'),
        ),
        migrations.RunPython(migrate_pickup_to_lines, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='publicpickuprequest',
            name='material',
        ),
        migrations.RemoveField(
            model_name='publicpickuprequest',
            name='weight_kg',
        ),
        migrations.CreateModel(
            name='CompanyRegistrationRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company_name', models.CharField(max_length=255)),
                ('contact_name', models.CharField(max_length=150)),
                ('phone', models.CharField(max_length=50)),
                ('email', models.EmailField(blank=True, default='', max_length=254)),
                ('address', models.TextField(blank=True, default='')),
                ('comment', models.TextField(blank=True, default='')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Заявка на регистрацию компании',
                'verbose_name_plural': 'Заявки на регистрацию компаний',
                'ordering': ['-created_at'],
            },
        ),
    ]
