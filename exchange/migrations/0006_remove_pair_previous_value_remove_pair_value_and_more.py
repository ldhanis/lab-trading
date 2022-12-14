# Generated by Django 4.1 on 2022-09-06 06:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('exchange', '0005_pair_previous_value'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pair',
            name='previous_value',
        ),
        migrations.RemoveField(
            model_name='pair',
            name='value',
        ),
        migrations.CreateModel(
            name='PairValue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('value', models.FloatField(default=0)),
                ('pair', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='values_history', to='exchange.pair')),
            ],
        ),
    ]
