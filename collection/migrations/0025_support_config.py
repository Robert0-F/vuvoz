from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('collection', '0024_product_category'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SupportConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('support_user', models.OneToOneField(
                    blank=True,
                    limit_choices_to={'role': 'support'},
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='support_config',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'verbose_name': 'Настройка техподдержки',
                'verbose_name_plural': 'Настройки техподдержки',
            },
        ),
    ]
