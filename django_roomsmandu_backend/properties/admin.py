from django.contrib import admin
from .models import Property, Reservation, VideoCallSchedule

# Register your models here.
admin.site.register(Property)
admin.site.register(Reservation)
admin.site.register(VideoCallSchedule)