# Generated by Django 4.1 on 2022-08-27 12:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0008_order_direction_order_external_id_order_fees_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='success',
            field=models.BooleanField(default=False),
        ),
    ]
