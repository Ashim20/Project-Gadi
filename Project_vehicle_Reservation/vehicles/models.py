from django.conf import settings
from django.db import models


def upload_vehicle_doc(instance, filename):
    # media/vehicles/<owner_id>/<filename>
    return f"vehicles/{instance.owner_id}/{filename}"


class Vehicle(models.Model):
    VEHICLE_TYPES = [
        ("bike", "Bike"),
        ("scooter", "Scooter"),
        ("car", "Car"),
        ("van", "Van"),
        ("truck", "Truck"),
    ]

    class ApprovalStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="vehicles",
    )

    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPES)
    model_name = models.CharField(max_length=120)

    # IMPORTANT: Your form uses number_plate_no and license_no
    number_plate_no = models.CharField(max_length=50, unique=True)
    license_no = models.CharField(max_length=50)

    # REQUIRED photos
    license_front_photo = models.ImageField(upload_to=upload_vehicle_doc)
    license_back_photo = models.ImageField(upload_to=upload_vehicle_doc)
    bluebook_photo = models.ImageField(upload_to=upload_vehicle_doc)
    vehicle_photo_with_plate = models.ImageField(upload_to=upload_vehicle_doc)

    status = models.CharField(
        max_length=20, choices=ApprovalStatus.choices, default=ApprovalStatus.PENDING
    )
    admin_feedback = models.TextField(blank=True)

    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="vehicle_reviews",
    )

    def __str__(self):
        return f"{self.model_name} - {self.number_plate_no}"
