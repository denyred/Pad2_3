# Generated by Django 5.1.2 on 2024-10-23 12:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='passrord',
            new_name='password',
        ),
    ]