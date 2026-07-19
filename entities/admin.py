from django.contrib import admin
from .models import Entity

@admin.register(Entity)
class EntityAdmin(admin.ModelAdmin):
    list_display = ('entity_name', 'entity_type', 'status', 'created_at')
    list_filter = ('status', 'entity_type')
