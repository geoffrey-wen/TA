from django.contrib import admin
from .models import Profile, Unit, CareerHistory

# Register your models here.
admin.site.register(Profile)
admin.site.register(Unit)
admin.site.register(CareerHistory)