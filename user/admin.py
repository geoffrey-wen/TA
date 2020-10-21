from django.contrib import admin
from .models import Profile, Unit, CareerHistory, Auth, PointHistory

# Register your models here.
admin.site.register(Profile)
admin.site.register(Unit)
admin.site.register(CareerHistory)
admin.site.register(Auth)
admin.site.register(PointHistory)

