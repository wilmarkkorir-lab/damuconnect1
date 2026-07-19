from rest_framework import serializers
from .models import Donation
from inventory.models import BloodStock
from notifications.utils import send_notification
from django.utils import timezone


class DonationSerializer(serializers.ModelSerializer):
    donor_name = serializers.CharField(source='donor.full_name', read_only=True)
    blood_type = serializers.CharField(source='donor.blood_type', read_only=True)
    entity_name = serializers.CharField(source='entity.entity_name', read_only=True)

    class Meta:
        model = Donation
        fields = (
            'id', 'donor_name', 'blood_type', 'entity_name',
            'donation_date', 'quantity', 'status',
        )
        read_only_fields = ('donation_date',)


class RecordDonationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donation
        fields = ('donor', 'quantity', 'status')

    def validate_donor(self, donor):
        entity = self.context['request'].user.entity_profile
        if donor.entity != entity:
            raise serializers.ValidationError("This donor does not belong to your entity.")
        if not donor.eligible:
            raise serializers.ValidationError("This donor is not currently eligible to donate.")
        return donor

    def create(self, validated_data):
        entity = self.context['request'].user.entity_profile
        donation = Donation.objects.create(entity=entity, **validated_data)
        # Update donor's last_donation_date when donation is completed
        if donation.status == 'completed':
            donor = donation.donor
            donor.last_donation_date = timezone.now().date()
            donor.save()
        return donation


class UpdateDonationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donation
        fields = ('status',)

    def update(self, instance, validated_data):
        old_status = instance.status
        new_status = validated_data.get('status', instance.status)
        instance.status = new_status
        instance.save()
        if new_status == 'completed':
            donor = instance.donor
            donor.last_donation_date = timezone.now().date()
            donor.save()
            # Update blood stock when status changes to completed
            if old_status != 'completed':
                stock, _ = BloodStock.objects.get_or_create(
                    entity=instance.entity,
                    blood_type=donor.blood_type,
                )
                stock.units_available += instance.quantity
                stock.save()
            # Notify donor
            if donor.user:
                send_notification(
                    donor.user,
                    "Donation Completed",
                    f"Your donation of {instance.quantity} unit(s) at {instance.entity.entity_name} has been marked as completed."
                )
        return instance
