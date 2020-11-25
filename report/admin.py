from django.contrib import admin
from .models import Report, Tag, Collaboration

class ReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'reporter', 'date_reported')

class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'creator')

# Register your models here.
admin.site.register(Report, ReportAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Collaboration)
