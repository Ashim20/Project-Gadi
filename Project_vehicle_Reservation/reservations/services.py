from django.db import transaction
from django.core.exceptions import ValidationError

from .models import Reservation
from vehicles.models import Vehicle


@transaction.atomic
def create_reservation(user, vehicle_id, start_date, end_date, purpose):
    # Only allow reservations on APPROVED vehicles
    vehicle = Vehicle.objects.select_for_update().get(
        id=vehicle_id,
        status=Vehicle.ApprovalStatus.APPROVED,
    )

    if end_date < start_date:
        raise ValidationError("End date must be >= start date")

    # Overlap check only against APPROVED reservations
    overlapping = Reservation.objects.filter(
        vehicle=vehicle,
        status="approved",
        start_date__lt=end_date,
        end_date__gt=start_date,
    ).exists()

    if overlapping:
        raise ValidationError("Vehicle already booked for the selected dates.")

    return Reservation.objects.create(
        vehicle=vehicle,
        user=user,
        start_date=start_date,
        end_date=end_date,
        purpose=purpose,
        status="pending",
    )
