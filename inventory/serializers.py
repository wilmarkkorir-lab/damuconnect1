from rest_framework import serializers
from .models import BloodStock


class BloodStockSerializer(serializers.ModelSerializer):
    entity_name = serializers.CharField(source='entity.entity_name', read_only=True)
    is_low = serializers.BooleanField(read_only=True)

    class Meta:
        model = BloodStock
        fields = ('id', 'entity_name', 'blood_type', 'units_available', 'is_low', 'last_updated')


class BloodStockAdjustSerializer(serializers.ModelSerializer):
    class Meta:
        model = BloodStock
        fields = ('units_available',)
