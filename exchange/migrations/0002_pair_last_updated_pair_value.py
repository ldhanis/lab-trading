# Generated by Django 4.1 on 2022-08-17 14:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exchange', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='pair',
            name='last_updated',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='pair',
            name='value',
            field=models.FloatField(default=0),
        ),
    ]
