from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission

User = get_user_model()

def is_admin(user):
    return user.is_staff or user.is_superuser

@login_required
@user_passes_test(is_admin)
def dashboard(request):
    users = User.objects.all()
    groups = Group.objects.all()
    permissions = Permission.objects.all()

    context = {
        'users': users,
        'groups': groups,
        'permissions': permissions,
    }
    return render(request, 'custom_admin/dashboard.html', context)
