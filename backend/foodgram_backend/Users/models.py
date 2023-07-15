from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator


class User(AbstractUser):

    username = models.CharField(
        max_length=150,
        validators=[RegexValidator(regex=r"^[\w.@+-]+\Z"),],
        unique=True
    )
    email = models.EmailField(verbose_name='email address', unique=True)
    first_name = models.CharField(max_length=32)
    last_name = models.CharField(max_length=64)


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

