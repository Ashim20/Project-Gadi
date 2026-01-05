from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Profile


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=User.Roles.choices, required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "role", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.role = self.cleaned_data["role"]
        if commit:
            user.save()
        return user


class ProfileCompleteForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            "full_name",
            "phone",
            "address_line1",
            "address_line2",
            "city",
            "state",
            "country",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make key fields required for "completion"
        self.fields["full_name"].required = True
        self.fields["phone"].required = True
        self.fields["address_line1"].required = True
        self.fields["city"].required = True
        self.fields["country"].required = True
