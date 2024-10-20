from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal


class User(models.Model):
    CUSTOMER = 'customer'
    EMPLOYEE = 'employee'

    USER_TYPE_CHOICES = [
        (CUSTOMER, 'Customer'),
        (EMPLOYEE, 'Employee'),
    ]

    user_type = models.CharField(
        max_length=16,
        choices=USER_TYPE_CHOICES,
        default=CUSTOMER
    )

    username = models.CharField(unique=True, max_length=32)
    password = models.CharField(max_length=32)

    first_name = models.CharField(max_length=16)
    last_name = models.CharField(max_length=16)

    rating = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        validators=[
            MinValueValidator(Decimal('0.0')),
            MaxValueValidator(Decimal('5.0'))
        ],
        default=0.0
    )