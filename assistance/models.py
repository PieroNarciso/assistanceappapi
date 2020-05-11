from django.db import models
from django.contrib.auth import settings
from django.contrib.auth.models import User

import random


# Create your models here.
class Assistance(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE, related_name='user_data')
    check_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - {self.check_time.strftime('%Y/%m/%d %H:%M:%S')}"


class NumCode(models.Model):
    code = models.IntegerField(default=random.randint(100000, 999999))

    def __str__(self):
        return f"{self.code}"


# Change __str__ method of User model
def get_user_str(self):
    return f"{self.first_name} {self.last_name}"


User.add_to_class("__str__", get_user_str)
