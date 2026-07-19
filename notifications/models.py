from django.db import models
from django.conf import settings


class Notification(models.Model):
    # The user who receives this notification
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
    )

    # Short title e.g. "Entity Approved"
    title = models.CharField(max_length=100)

    # Full message e.g. "Your entity Nairobi Hospital has been approved."
    message = models.TextField()

    # False = unread, True = read
    is_read = models.BooleanField(default=False)

    # When the notification was created
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']  # newest first

    def __str__(self):
        return f"{self.user.username} — {self.title}"
