from django.db import models
from donors.models import Donor
from entities.models import Entity

# The 3 possible states of a donation record
STATUS_CHOICES = (
    ('pending', 'Pending'),       # donation recorded but not yet confirmed
    ('completed', 'Completed'),   # donation successfully done — updates blood stock
    ('rejected', 'Rejected'),     # donation was rejected (e.g. donor failed health check)
)

class Donation(models.Model):
    # The donor who gave blood in this event
    donor = models.ForeignKey(
        Donor,
        on_delete=models.CASCADE,   # if the donor is deleted, delete their donations too
        related_name='donations',   # lets us do donor.donations.all() to list all donations
    )

    # The entity (hospital/blood bank) where the donation happened
    entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,       # if the entity is deleted, delete its donations too
        related_name='donations',       # lets us do entity.donations.all()
    )

    # Automatically set to today when the donation record is created
    donation_date = models.DateField(auto_now_add=True)

    # How many units of blood were donated (usually 1 per visit)
    quantity = models.PositiveIntegerField(default=1)

    # Status of this donation — defaults to completed when recorded
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='completed')

    def save(self, *args, **kwargs):
        # Check if this is a brand new donation (not an update to an existing one)
        is_new = self.pk is None

        # Save the donation record to the database first
        super().save(*args, **kwargs)

        # Only update blood stock if this is a new completed donation
        if is_new and self.status == 'completed':
            # Import here to avoid circular import issues between apps
            from inventory.models import BloodStock

            # Get the existing stock row for this entity + blood type, or create one if it doesn't exist
            stock, created = BloodStock.objects.get_or_create(
                entity=self.entity,
                blood_type=self.donor.blood_type,
            )

            # Add the donated units to the current stock
            stock.units_available += self.quantity
            stock.save()

    def __str__(self):
        # Shows donor name and entity name when printed
        return f"{self.donor.full_name} -> {self.entity.entity_name}"
