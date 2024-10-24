# Generated by Django 5.1.2 on 2024-10-23 18:22

import chats.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Chat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer_id', models.IntegerField()),
                ('employee_id', models.IntegerField()),
                ('identifier', models.CharField(default=chats.models.generate_identifier, max_length=8)),
            ],
        ),
    ]
