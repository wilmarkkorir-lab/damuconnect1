import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'damuconnect.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
print("Sending test email...")

try:
    send_mail(
        subject='DamuConnect — Password Reset OTP',
        message='Your DamuConnect password reset code is: 482916\n\nThis code expires in 10 minutes. Do not share it with anyone.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=['wilmark891@gmail.com'],
        fail_silently=False,
    )
    print("Email sent successfully!")
except Exception as e:
    print(f"Email failed: {e}")
