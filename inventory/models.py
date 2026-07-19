from django.db import models
from entities.models import Entity
from donors.models import BLOOD_TYPE_CHOICES  # reuse the same blood type list from donors

# If stock drops below this number, it is considered low
LOW_STOCK_THRESHOLD = 5

class BloodStock(models.Model):
    # The entity (hospital/blood bank) that owns this stock
    entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,       # if the entity is deleted, delete its stock too
        related_name='blood_stock',     # lets us do entity.blood_stock.all()
    )

    # The blood type this stock row tracks e.g. A+, O-, etc.
    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPE_CHOICES)

    # How many units of this blood type are currently available
    units_available = models.PositiveIntegerField(default=0)

    # Automatically updates to the current time every time this row is saved
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        # Prevents duplicate rows — one entity can only have one row per blood type
        unique_together = ('entity', 'blood_type')

    @property
    def is_low(self):
        # Returns True if stock is below the threshold — used to trigger low stock alerts
        return self.units_available < LOW_STOCK_THRESHOLD

    def __str__(self):
        # Shows entity name, blood type and units when printed
        return f"{self.entity.entity_name} - {self.blood_type}: {self.units_available} units"
