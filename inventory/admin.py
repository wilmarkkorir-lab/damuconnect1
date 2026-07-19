from django.contrib import admin
from .models import BloodStock

@admin.register(BloodStock)
class BloodStockAdmin(admin.ModelAdmin):
    list_display = ('entity', 'blood_type', 'units_available', 'last_updated')
    list_filter = ('blood_type',)
