from django.urls import path
from .views import my_vehicles_view, vehicle_detail_json, vehicle_register_view, vehicle_edit_resubmit_view

urlpatterns = [
     path("<int:vehicle_id>/detail/", vehicle_detail_json, name="vehicle_detail_json"),
    path("register/", vehicle_register_view, name="register_vehicle"),
    path("mine/", my_vehicles_view, name="my_vehicles"),
    path("<int:vehicle_id>/edit/", vehicle_edit_resubmit_view, name="edit_vehicle"),
]
