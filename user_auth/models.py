from django.db import models
from django.contrib.auth.models import User
# Create your models here.

# class Profile(models.Model):
#     is_admin = models.BooleanField(default=True)
#     user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

#     def __str__(self):
#         return self.user.username