from django.contrib import admin
from django import forms
from django.utils import timezone
from .models import Vehicle


class VehicleAdminForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = "__all__"

    def clean(self):
        cleaned = super().clean()
        status = cleaned.get("status")
        feedback = (cleaned.get("admin_feedback") or "").strip()

        if status == Vehicle.ApprovalStatus.REJECTED and not feedback:
            self.add_error("admin_feedback", "Feedback is required when rejecting a vehicle.")

        # Optional: if approved, clear feedback (avoid old rejection note staying)
        if status == Vehicle.ApprovalStatus.APPROVED:
            cleaned["admin_feedback"] = ""

        return cleaned


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    form = VehicleAdminForm

    list_display = ("model_name", "vehicle_type", "number_plate_no", "owner", "status", "submitted_at")
    list_filter = ("status", "vehicle_type")
    search_fields = ("number_plate_no", "license_no", "owner__username", "model_name")

    readonly_fields = ("submitted_at", "reviewed_at", "reviewed_by")

    def save_model(self, request, obj, form, change):
        if "status" in form.changed_data:
            obj.reviewed_by = request.user
            obj.reviewed_at = timezone.now()

            # Also clear feedback when approving (double-safety)
            if obj.status == Vehicle.ApprovalStatus.APPROVED:
                obj.admin_feedback = ""

        super().save_model(request, obj, form, change)
