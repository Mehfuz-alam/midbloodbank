# Generated by Django 3.0.5 on 2025-01-25 09:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('donor', '0002_auto_20250124_1822'),
    ]

    operations = [
        migrations.AddField(
            model_name='donor',
            name='latitude',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='donor',
            name='longitude',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
