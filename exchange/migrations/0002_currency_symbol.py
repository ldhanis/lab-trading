# Generated by Django 4.1 on 2022-08-15 20:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exchange', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='currency',
            name='symbol',
            field=models.CharField(default='', max_length=64),
            preserve_default=False,
        ),
    ]
