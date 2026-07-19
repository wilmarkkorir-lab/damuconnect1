from .models import Notification


def send_notification(user, title, message):
    """
    Call this from anywhere in the project to create a notification.
    e.g. send_notification(user, "Entity Approved", "Your entity has been approved.")
    """
    Notification.objects.create(user=user, title=title, message=message)
