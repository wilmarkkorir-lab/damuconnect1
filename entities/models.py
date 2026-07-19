from django.db import models
from django.conf import settings

# The types of organizations that can register as an entity
ENTITY_TYPE_CHOICES = (
    ('hospital', 'Hospital'),
    ('blood_bank', 'Blood Bank'),
    ('red_cross', 'Red Cross'),
    ('clinic', 'Clinic'),
)

# Approval status of an entity — starts as pending until an admin reviews it
STATUS_CHOICES = (
    ('pending', 'Pending'),       # just registered, waiting for admin review
    ('approved', 'Approved'),     # admin approved, can fully use the system
    ('rejected', 'Rejected'),     # admin rejected, cannot use the system
)

class Entity(models.Model):
    # Links this entity to its login account (1 entity = 1 user account)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,   # points to our custom User model in accounts
        on_delete=models.CASCADE,   # if the user is deleted, delete the entity too
        related_name='entity_profile',  # lets us do user.entity_profile to get the entity
    )

    # The official name of the hospital/blood bank/clinic
    entity_name = models.CharField(max_length=150)

    # What kind of organization this is (hospital, blood bank, etc.)
    entity_type = models.CharField(max_length=20, choices=ENTITY_TYPE_CHOICES)

    # Physical location of the entity
    address = models.CharField(max_length=255)

    # Phone number to reach the entity
    contact_number = models.CharField(max_length=20)

    # Approval status — new entities start as 'pending' until admin approves
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    # The admin who approved or rejected this entity (empty until reviewed)
    registered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,  # if admin is deleted, keep the entity but clear this field
        null=True,                  # can be empty in the database
        blank=True,                 # can be empty in forms
        related_name='entities_reviewed',  # lets us do admin_user.entities_reviewed.all()
    )

    # Automatically saves the date and time when this entity first registered
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Shows entity name when printed e.g. "Kenyatta Hospital"
        return self.entity_name
