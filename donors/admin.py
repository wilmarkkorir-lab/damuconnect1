from django.contrib import admin
from .models import Donor, DonorCard

@admin.register(Donor)
class DonorAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'blood_type', 'entity', 'eligible', 'last_donation_date')
    list_filter = ('blood_type', 'eligible')

@admin.register(DonorCard)
class DonorCardAdmin(admin.ModelAdmin):
    list_display = ('card_number', 'donor', 'entity', 'date_issued', 'expiry_date')
