# Generated by Django 5.1.2 on 2024-10-23 11:05

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_type', models.CharField(choices=[('customer', 'Customer'), ('employee', 'Employee')], default='customer', max_length=16)),
                ('username', models.CharField(max_length=32, unique=True)),
                ('passrord', models.CharField(max_length=32)),
                ('first_name', models.CharField(max_length=16)),
                ('last_name', models.CharField(max_length=16)),
            ],
        ),
    ]