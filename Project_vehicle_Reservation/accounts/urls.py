from django.urls import path
from django.contrib.auth import views as auth_views
from .views import signup_view, profile_complete_view,RoleBasedLoginView

urlpatterns = [
    path("signup/", signup_view, name="signup"),
    path("profile/complete/", profile_complete_view, name="profile_complete"),

    # auth
    path("login/", RoleBasedLoginView.as_view(), name="login"),

    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
