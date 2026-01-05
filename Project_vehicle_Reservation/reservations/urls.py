from django.urls import path
from . import views

urlpatterns = [
    # user
    path("vehicle/<int:vehicle_id>/reserve/", views.reserve_vehicle, name="reserve_vehicle"),
    path("mine/", views.my_reservations, name="my_reservations"),
    path("<int:reservation_id>/cancel/", views.cancel_my_reservation, name="cancel_my_reservation"),

    # owner
    path("owner/", views.owner_reservations_dashboard, name="owner_reservations"),
    path("owner/<int:reservation_id>/decide/", views.owner_decide_reservation, name="owner_decide_reservation"),
    path("owner/<int:reservation_id>/cancel/", views.owner_cancel_approved, name="owner_cancel_approved"),
]
