from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('collection', '0025_support_config'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collectionrequest',
            name='status',
            field=models.CharField(
                choices=[
                    ('new', 'New'),
                    ('accepted', 'Accepted'),
                    ('pending_confirmation', 'Pending confirmation'),
                    ('completed', 'Completed'),
                    ('cancelled', 'Cancelled'),
                ],
                default='new',
                max_length=24,
            ),
        ),
    ]
