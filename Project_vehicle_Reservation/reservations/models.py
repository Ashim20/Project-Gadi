from datetime import timedelta
from django.conf import settings
from django.db import models
from django.utils import timezone

from vehicles.models import Vehicle


class Reservation(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("cancelled", "Cancelled"),
    ]

    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name="reservations")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reservations")

    start_date = models.DateField()
    end_date = models.DateField()
    purpose = models.CharField(max_length=255)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    owner_note = models.TextField(blank=True)  # rejection reason / owner note

    created_at = models.DateTimeField(auto_now_add=True)

    def can_user_cancel(self):
        return timezone.now().date() <= self.start_date - timedelta(days=2)

    def can_owner_cancel(self):
        return timezone.now().date() <= self.start_date - timedelta(days=5)

    def __str__(self):
        return f"{self.vehicle} | {self.user} | {self.start_date} - {self.end_date} ({self.status})"
