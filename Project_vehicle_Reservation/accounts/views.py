from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib.auth.views import LoginView
from django.urls import reverse


def logout_view(request):
    logout(request)
    return redirect("login")   # or redirect to "home"


from .forms import SignUpForm, ProfileCompleteForm
from .models import Profile


def signup_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = SignUpForm()

    return render(request, "accounts/signup.html", {"form": form})


@login_required
def profile_complete_view(request):
    # ✅ always safe
    profile, _ = Profile.objects.get_or_create(user=request.user)

    # ✅ normal user doesn't need this page
    if not request.user.is_owner:
        return redirect("home")

    # ✅ already completed? go to owner area
    if profile.is_completed:
        return redirect("my_vehicles")

    if request.method == "POST":
        form = ProfileCompleteForm(request.POST, instance=profile)
        if form.is_valid():
            p = form.save(commit=False)
            p.is_completed = True
            p.save()
            return redirect("my_vehicles")
    else:
        form = ProfileCompleteForm(instance=profile)

    return render(request, "accounts/profile_complete.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("login")

class RoleBasedLoginView(LoginView):
    template_name = "../templates/accounts/login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        user = self.request.user

        # if user was trying to access a protected page, respect ?next=
        next_url = self.get_redirect_url()
        if next_url:
            return next_url

        # OWNER logic
        if getattr(user, "is_owner", False):
            profile, _ = Profile.objects.get_or_create(user=user)
            if not profile.is_completed:
                return reverse("profile_complete")
            return reverse("my_vehicles")  # or reverse("owner_reservations")

        # Normal user
        return reverse("home")