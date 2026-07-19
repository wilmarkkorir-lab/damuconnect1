from django.contrib import admin
from .models import Donation

@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ('donor', 'entity', 'donation_date', 'quantity', 'status')
    list_filter = ('status',)
