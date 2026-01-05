from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render

from .forms import OwnerDecisionForm, ReservationCreateForm
from .models import Reservation
from .services import create_reservation
from vehicles.models import Vehicle


def owner_required(view_func):
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated or not getattr(request.user, "is_owner", False):
            return HttpResponseForbidden("Owner access only.")
        return view_func(request, *args, **kwargs)
    return _wrapped


# --------------------
# USER: create reservation
# --------------------
@login_required
def reserve_vehicle(request, vehicle_id: int):
    vehicle = get_object_or_404(
        Vehicle,
        id=vehicle_id,
        status=Vehicle.ApprovalStatus.APPROVED,
    )

    if request.method == "POST":
        form = ReservationCreateForm(request.POST)
        if form.is_valid():
            try:
                res = create_reservation(
                    user=request.user,
                    vehicle_id=vehicle.id,
                    start_date=form.cleaned_data["start_date"],
                    end_date=form.cleaned_data["end_date"],
                    purpose=form.cleaned_data["purpose"],
                )
                messages.success(request, "Reservation request submitted (Pending owner approval).")
                return redirect("my_reservations")
            except Exception as e:
                messages.error(request, str(e))
    else:
        form = ReservationCreateForm()

    return render(request, "reservations/reserve_vehicle.html", {"vehicle": vehicle, "form": form})



@login_required
def my_reservations(request):
    reservations = (
        Reservation.objects
        .filter(user=request.user)   # ✅ only mine
        .select_related("vehicle")
        .order_by("-created_at")
    )
    return render(request, "reservations/my_reservations.html", {"reservations": reservations})


@login_required
def cancel_my_reservation(request, reservation_id: int):
    r = get_object_or_404(Reservation, id=reservation_id, user=request.user)

    if r.status in ["cancelled", "rejected"]:
        messages.error(request, "This reservation cannot be cancelled.")
        return redirect("my_reservations")

    if not r.can_user_cancel():
        messages.error(request, "You can cancel only if at least 2 days remain before start date.")
        return redirect("my_reservations")

    r.status = "cancelled"
    r.save(update_fields=["status"])
    messages.success(request, "Reservation cancelled.")
    return redirect("my_reservations")




# --------------------
# OWNER: manage reservations for own vehicles
# --------------------
@login_required
@owner_required
def owner_reservations_dashboard(request):
    qs = Reservation.objects.filter(
        vehicle__owner=request.user
    ).select_related("vehicle", "user").order_by("-created_at")

    return render(request, "reservations/owner_dashboard.html", {"reservations": qs})


@login_required
@owner_required
def owner_decide_reservation(request, reservation_id: int):
    r = get_object_or_404(Reservation, id=reservation_id, vehicle__owner=request.user)

    if r.status != "pending":
        messages.error(request, "Only pending reservations can be approved/rejected.")
        return redirect("owner_reservations")

    if request.method == "POST":
        form = OwnerDecisionForm(request.POST)
        if form.is_valid():
            decision = form.cleaned_data["decision"]
            note = (form.cleaned_data["note"] or "").strip()

            if decision == "approve":
                # Approving must ensure no overlap with other approved reservations
                overlapping = Reservation.objects.filter(
                    vehicle=r.vehicle,
                    status="approved",
                    start_date__lt=r.end_date,
                    end_date__gt=r.start_date,
                ).exists()

                if overlapping:
                    messages.error(request, "Cannot approve: vehicle already has an approved booking for those dates.")
                    return redirect("owner_reservations")

                r.status = "approved"
                r.owner_note = ""
                r.save(update_fields=["status", "owner_note"])
                messages.success(request, "Reservation approved.")
                return redirect("owner_reservations")

            # reject
            r.status = "rejected"
            r.owner_note = note
            r.save(update_fields=["status", "owner_note"])
            messages.success(request, "Reservation rejected.")
            return redirect("owner_reservations")
    else:
        form = OwnerDecisionForm()

    return render(request, "reservations/owner_decide.html", {"reservation": r, "form": form})


@login_required
@owner_required
def owner_cancel_approved(request, reservation_id: int):
    r = get_object_or_404(Reservation, id=reservation_id, vehicle__owner=request.user)

    if r.status != "approved":
        messages.error(request, "Only approved reservations can be cancelled by owner.")
        return redirect("owner_reservations")

    if not r.can_owner_cancel():
        messages.error(request, "Owner can cancel only if at least 5 days remain before start date.")
        return redirect("owner_reservations")

    r.status = "cancelled"
    r.owner_note = "Cancelled by owner."
    r.save(update_fields=["status", "owner_note"])
    messages.success(request, "Reservation cancelled by owner.")
    return redirect("owner_reservations")
