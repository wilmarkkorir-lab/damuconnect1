from django.db import models
from django.conf import settings
from entities.models import Entity

# All 8 possible human blood types
BLOOD_TYPE_CHOICES = (
    ('A+', 'A+'), ('A-', 'A-'),
    ('B+', 'B+'), ('B-', 'B-'),
    ('AB+', 'AB+'), ('AB-', 'AB-'),
    ('O+', 'O+'), ('O-', 'O-'),
)

class Donor(models.Model):
    # Links this donor profile to a login account (optional — donor may not have an account)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='donor_profile',
    )

    # Full legal name of the donor
    full_name = models.CharField(max_length=150)

    # Donor's email address — must be unique
    email = models.EmailField(unique=True)

    # Donor's phone number
    phone = models.CharField(max_length=20)

    # The donor's blood type — must be one of the 8 choices above
    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPE_CHOICES)

    # Used to calculate the donor's age and check eligibility
    date_of_birth = models.DateField()

    # The last time this donor gave blood (empty if they have never donated)
    last_donation_date = models.DateField(null=True, blank=True)

    # True = donor can give blood, False = donor is not eligible right now
    eligible = models.BooleanField(default=True)

    # The entity (hospital/blood bank) that registered this donor
    entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,   # if the entity is deleted, delete its donors too
        related_name='donors',      # lets us do entity.donors.all() to list all donors
    )

    def __str__(self):
        # Shows donor name when printed e.g. "John Doe"
        return self.full_name


class DonorCard(models.Model):
    # The donor this card belongs to
    donor = models.ForeignKey(
        Donor,
        on_delete=models.CASCADE,   # if the donor is deleted, delete their cards too
        related_name='cards',       # lets us do donor.cards.all() to list all cards
    )

    # The entity that issued this card
    entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,   # if the entity is deleted, delete the cards it issued
        related_name='issued_cards',  # lets us do entity.issued_cards.all()
    )

    # Unique card number printed on the physical card
    card_number = models.CharField(max_length=30, unique=True)

    # Automatically set to today when the card is created
    date_issued = models.DateField(auto_now_add=True)

    # The date this card stops being valid
    expiry_date = models.DateField()

    def __str__(self):
        # Shows card number when printed e.g. "CARD-00123"
        return self.card_number
