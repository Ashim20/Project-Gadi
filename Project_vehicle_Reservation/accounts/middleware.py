from django.shortcuts import redirect
from django.urls import reverse

from .models import Profile


class ForceOwnerProfileCompletionMiddleware:
    """
    If a logged-in user is an OWNER and profile is not completed,
    force them to /accounts/profile/complete/ for all pages
    (except auth/profile/admin/static/media).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)

        if user and user.is_authenticated and getattr(user, "is_owner", False):
            profile, _ = Profile.objects.get_or_create(user=user)

            if not profile.is_completed:
                allowed_paths = {
                    reverse("profile_complete"),
                    reverse("logout"),
                    reverse("login"),
                }

                # allow admin, static, media, and accounts routes
                path = request.path
                if (
                    path not in allowed_paths
                    and not path.startswith("/admin/")
                    and not path.startswith("/static/")
                    and not path.startswith("/media/")
                    and not path.startswith("/accounts/")
                ):
                    return redirect("profile_complete")

        return self.get_response(request)
