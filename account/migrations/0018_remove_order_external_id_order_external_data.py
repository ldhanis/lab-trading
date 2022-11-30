# Generated by Django 4.1 on 2022-11-16 12:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0017_order_leverage'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='external_id',
        ),
        migrations.AddField(
            model_name='order',
            name='external_data',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
