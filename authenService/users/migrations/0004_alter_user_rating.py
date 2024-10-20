# Generated by Django 5.1.2 on 2024-10-23 18:05

import django.core.validators
from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_user_rating'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='rating',
            field=models.DecimalField(decimal_places=1, default=0.0, max_digits=3, validators=[django.core.validators.MinValueValidator(Decimal('0.0')), django.core.validators.MaxValueValidator(Decimal('5.0'))]),
        ),
    ]
