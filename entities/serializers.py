from rest_framework import serializers
from .models import Entity


class EntitySerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Entity
        fields = (
            'id', 'username', 'entity_name', 'entity_type',
            'address', 'contact_number', 'status', 'created_at',
        )
        read_only_fields = ('status', 'created_at')


class EntityRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Entity
        fields = ('entity_name', 'entity_type', 'address', 'contact_number')

    def create(self, validated_data):
        user = self.context['request'].user
        return Entity.objects.create(user=user, **validated_data)


class EntityUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Entity
        fields = ('entity_name', 'entity_type', 'address', 'contact_number')


class EntityApprovalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Entity
        fields = ('status',)

    def validate_status(self, value):
        if value not in ('approved', 'rejected'):
            raise serializers.ValidationError("Status must be approved or rejected.")
        return value
