from django.db import models

from django.contrib.auth.models import AbstractUser



class User(AbstractUser):
    class Roles(models.TextChoices):
        USER = "user", "User"
        OWNER = "owner", "Vehicle Owner"

    role = models.CharField(max_length=20, choices=Roles.choices, default=Roles.USER)

    @property
    def is_owner(self) -> bool:
        return self.role == self.Roles.OWNER

    @property
    def is_admin(self) -> bool:
        return self.is_staff or self.is_superuser


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")

    full_name = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=30, blank=True)

    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True, default="Nepal")
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"Profile: {self.user.username}"

