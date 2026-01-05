from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from .forms import VehicleRegistrationForm
from .models import Vehicle
from django.db.models import Exists, OuterRef
from django.utils import timezone
from reservations.models import Reservation


def owner_required(view_func):
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated or not getattr(request.user, "is_owner", False):
            return HttpResponseForbidden("Owner access only.")
        return view_func(request, *args, **kwargs)
    return _wrapped


@login_required
@owner_required
def vehicle_register_view(request):
    if request.method == "POST":
        form = VehicleRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            v = form.save(commit=False)
            v.owner = request.user
            v.status = Vehicle.ApprovalStatus.PENDING
            v.admin_feedback = ""
            v.reviewed_by = None
            v.reviewed_at = None
            v.save()
            messages.success(request, "Vehicle submitted for admin approval.")
            return redirect("my_vehicles")
    else:
        form = VehicleRegistrationForm()

    return render(request, "vehicles/register_vehicle.html", {"form": form})


@login_required
@owner_required
def my_vehicles_view(request):
    vehicles = Vehicle.objects.filter(owner=request.user).order_by("-submitted_at")
    return render(request, "vehicles/my_vehicles.html", {"vehicles": vehicles})


@login_required
@owner_required
def vehicle_edit_resubmit_view(request, vehicle_id: int):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id, owner=request.user)

    if vehicle.status == Vehicle.ApprovalStatus.APPROVED:
        messages.error(request, "Approved vehicles cannot be edited.")
        return redirect("my_vehicles")

    if request.method == "POST":
        form = VehicleRegistrationForm(request.POST, request.FILES, instance=vehicle)
        if form.is_valid():
            v = form.save(commit=False)
            v.status = Vehicle.ApprovalStatus.PENDING
            v.admin_feedback = ""
            v.reviewed_by = None
            v.reviewed_at = None
            v.save()
            messages.success(request, "Vehicle updated and resubmitted for review.")
            return redirect("my_vehicles")
    else:
        form = VehicleRegistrationForm(instance=vehicle)

    return render(request, "vehicles/edit_vehicle.html", {"form": form, "vehicle": vehicle})




def public_vehicle_list(request):
    vehicle_type = request.GET.get("type")
    today = timezone.now().date()

    active_res_qs = Reservation.objects.filter(
        vehicle_id=OuterRef("pk"),
        status__in=["pending", "approved"],
        end_date__gte=today,   # still active / upcoming
    )

    qs = (
        Vehicle.objects.filter(status=Vehicle.ApprovalStatus.APPROVED)
        .annotate(has_active_res=Exists(active_res_qs))
        .filter(has_active_res=False)   # ✅ hide reserved
        .order_by("-submitted_at")
    )

    if vehicle_type:
        qs = qs.filter(vehicle_type=vehicle_type)

    return render(request, "vehicles/public_list.html", {
        "vehicles": qs,
        "types": Vehicle.VEHICLE_TYPES,
        "selected": vehicle_type,
    })


from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Vehicle


def vehicle_detail_json(request, vehicle_id: int):
    vehicle = get_object_or_404(
        Vehicle,
        id=vehicle_id,
        status=Vehicle.ApprovalStatus.APPROVED,
    )

    owner = vehicle.owner
    profile = getattr(owner, "profile", None)

    def build_address(p):
        if not p:
            return ""
        parts = [
            p.address_line1,
            p.address_line2,
            p.city,
            p.state,
            p.country,
        ]
        parts = [x.strip() for x in parts if x and x.strip()]
        return ", ".join(parts)

    data = {
        "vehicle": {
            "id": vehicle.id,
            "model_name": vehicle.model_name,
            "vehicle_type": vehicle.get_vehicle_type_display(),
            "number_plate_no": vehicle.number_plate_no,
            "photo_url": vehicle.vehicle_photo_with_plate.url if vehicle.vehicle_photo_with_plate else "",
        },
        "owner": {
            "username": owner.username,
            "full_name": (profile.full_name if profile and profile.full_name else f"{owner.first_name} {owner.last_name}".strip()),
            "phone": (profile.phone if profile else ""),
            "address": build_address(profile),
        },
    }
    return JsonResponse(data)
