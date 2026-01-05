from django import forms
from .models import Reservation


class ReservationCreateForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ["start_date", "end_date", "purpose"]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }


class OwnerDecisionForm(forms.Form):
    decision = forms.ChoiceField(choices=[("approve", "Approve"), ("reject", "Reject")])
    note = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 3}))

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("decision") == "reject" and not (cleaned.get("note") or "").strip():
            self.add_error("note", "Rejection reason is required.")
        return cleaned
