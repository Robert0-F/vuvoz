# Material catalog fields + public pickup requests from homepage

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('collection', '0019_support_role_chat'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='material',
            options={'ordering': ['sort_order', 'name'], 'verbose_name': 'Material', 'verbose_name_plural': 'Materials'},
        ),
        migrations.AddField(
            model_name='material',
            name='icon',
            field=models.CharField(blank=True, help_text='MDI icon name without prefix, e.g. package-variant', max_length=64),
        ),
        migrations.AddField(
            model_name='material',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='materials/'),
        ),
        migrations.AddField(
            model_name='material',
            name='short_description',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='material',
            name='sort_order',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.CreateModel(
            name='PublicPickupRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contact_name', models.CharField(blank=True, max_length=255)),
                ('phone', models.CharField(max_length=50)),
                ('address', models.TextField()),
                ('preferred_date', models.DateField()),
                ('weight_kg', models.DecimalField(decimal_places=2, max_digits=10)),
                ('estimated_payout', models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ('status', models.CharField(choices=[('new', 'Новая'), ('contacted', 'Связались'), ('done', 'Выполнена'), ('cancelled', 'Отменена')], db_index=True, default='new', max_length=20)),
                ('admin_notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('material', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='public_pickup_requests', to='collection.material')),
            ],
            options={
                'verbose_name': 'Заявка на вывоз с сайта',
                'verbose_name_plural': 'Заявки на вывоз с сайта',
                'ordering': ['-created_at'],
            },
        ),
    ]
