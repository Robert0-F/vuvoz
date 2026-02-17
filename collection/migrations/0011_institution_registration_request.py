# Institution registration request from public homepage

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('collection', '0010_product_image_order_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='InstitutionRegistrationRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=150)),
                ('patronymic', models.CharField(blank=True, max_length=150)),
                ('institution_name', models.CharField(max_length=255)),
                ('address', models.TextField()),
                ('phone', models.CharField(max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Заявка на регистрацию учреждения',
                'verbose_name_plural': 'Заявки на регистрацию учреждений',
                'ordering': ['-created_at'],
            },
        ),
    ]
