# Generated by Django 4.1 on 2022-08-17 14:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('exchange', '0002_pair_last_updated_pair_value'),
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CurrencyAmount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.FloatField(default=0)),
                ('currency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='exchange.currency')),
                ('user', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.DeleteModel(
            name='CurrencyAmout',
        ),
    ]
