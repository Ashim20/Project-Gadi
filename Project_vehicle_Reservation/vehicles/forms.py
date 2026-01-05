from django import forms
from .models import Vehicle

MAX_MB = 5

class VehicleRegistrationForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = [
            "vehicle_type",
            "model_name",
            "number_plate_no",
            "license_no",
            "license_front_photo",
            "license_back_photo",
            "bluebook_photo",
            "vehicle_photo_with_plate",
        ]

    def clean(self):
        cleaned = super().clean()

        # Ensure all files exist (ImageField normally required, but good to enforce)
        required_files = [
            "license_front_photo",
            "license_back_photo",
            "bluebook_photo",
            "vehicle_photo_with_plate",
        ]
        for f in required_files:
            if not cleaned.get(f):
                self.add_error(f, "This file is required.")

        # Validate file size (optional but recommended)
        for f in required_files:
            file = cleaned.get(f)
            if file and file.size > MAX_MB * 1024 * 1024:
                self.add_error(f, f"Max file size is {MAX_MB}MB.")

        return cleaned
