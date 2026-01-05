from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Reservation

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ("vehicle", "user", "start_date", "end_date", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("vehicle__number_plate_no", "user__username")
