# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('collection', '0012_alter_pointsorder_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collectionrequest',
            name='status',
            field=models.CharField(
                choices=[
                    ('new', 'New'),
                    ('accepted', 'Accepted'),
                    ('completed', 'Completed'),
                    ('cancelled', 'Cancelled'),
                ],
                default='new',
                max_length=20,
            ),
        ),
    ]
