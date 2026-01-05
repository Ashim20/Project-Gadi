from django.core.exceptions import PermissionDenied

def owner_required(view_func):
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied("Login required.")
        if not getattr(request.user, "is_owner", False):
            raise PermissionDenied("Only vehicle owners can access this page.")
        return view_func(request, *args, **kwargs)
    return _wrapped
