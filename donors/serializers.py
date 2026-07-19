from rest_framework import serializers
from .models import Donor, DonorCard
from entities.models import Entity
from django.utils import timezone
from dateutil.relativedelta import relativedelta


class DonorSerializer(serializers.ModelSerializer):
    entity_name = serializers.CharField(source='entity.entity_name', read_only=True)

    class Meta:
        model = Donor
        fields = (
            'id', 'full_name', 'email', 'phone', 'blood_type',
            'date_of_birth', 'last_donation_date', 'eligible', 'entity_name',
        )
        read_only_fields = ('eligible',)


class DonorRegisterSerializer(serializers.ModelSerializer):
    entity = serializers.PrimaryKeyRelatedField(
        queryset=Entity.objects.filter(status='approved'),
        required=False,
    )

    class Meta:
        model = Donor
        fields = ('full_name', 'email', 'phone', 'blood_type', 'date_of_birth', 'entity')

    def validate_email(self, value):
        if Donor.objects.filter(email=value).exists():
            raise serializers.ValidationError("A donor with this email already exists.")
        return value

    def validate_date_of_birth(self, value):
        # Donor must be at least 18 years old
        age = relativedelta(timezone.now().date(), value).years
        if age < 18:
            raise serializers.ValidationError("Donor must be at least 18 years old.")
        return value

    def create(self, validated_data):
        request = self.context['request']
        if request.user.is_superuser or request.user.role == 'admin':
            # Admin must provide entity
            if 'entity' not in validated_data:
                raise serializers.ValidationError({"entity": "Admin must specify an entity for the donor."})
        else:
            # Entity is automatically set to the logged in entity
            validated_data['entity'] = request.user.entity_profile
        return Donor.objects.create(**validated_data)


class DonorUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donor
        fields = ('full_name', 'email', 'phone', 'blood_type', 'date_of_birth')

    def validate_email(self, value):
        if Donor.objects.filter(email=value).exclude(pk=self.instance.pk).exists():
            raise serializers.ValidationError("A donor with this email already exists.")
        return value


class DonorCardSerializer(serializers.ModelSerializer):
    donor_name = serializers.CharField(source='donor.full_name', read_only=True)
    entity_name = serializers.CharField(source='entity.entity_name', read_only=True)
    is_expired = serializers.SerializerMethodField()

    class Meta:
        model = DonorCard
        fields = ('id', 'donor_name', 'entity_name', 'card_number', 'date_issued', 'expiry_date', 'is_expired')
        read_only_fields = ('date_issued',)

    def get_is_expired(self, obj):
        # Returns True if card expiry date has passed
        return obj.expiry_date < timezone.now().date()


class IssueCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = DonorCard
        fields = ('donor', 'card_number', 'expiry_date')

    def validate_donor(self, donor):
        # Make sure donor belongs to the entity issuing the card
        request = self.context['request']
        if request.user.role == 'entity' and donor.entity != request.user.entity_profile:
            raise serializers.ValidationError("This donor does not belong to your entity.")
        if not donor.eligible:
            raise serializers.ValidationError("This donor is not eligible.")
        return donor

    def create(self, validated_data):
        entity = self.context['request'].user.entity_profile
        return DonorCard.objects.create(entity=entity, **validated_data)
