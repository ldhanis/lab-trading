# Generated by Django 4.1 on 2022-10-26 12:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0016_rename_fullfilled_on_order_position_closed_at_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='leverage',
            field=models.IntegerField(default=2),
        ),
    ]