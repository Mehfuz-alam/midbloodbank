# Generated by Django 5.1.6 on 2025-02-16 11:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('donor', '0005_blooddonate_name'),
    ]

    operations = [
        migrations.RenameField(
            model_name='blooddonate',
            old_name='name',
            new_name='first_name',
        ),
    ]
