from django.contrib import admin
from .models import dummyproduct, Report, Tag


class dummyproductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock')

class ReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'reporter', 'date_reported')

class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'creator')

# Register your models here.
admin.site.register(dummyproduct, dummyproductAdmin)
admin.site.register(Report, ReportAdmin)
admin.site.register(Tag, TagAdmin)